"""Reproduce bounded DOS20 RNG caller proof from a private EXE and ASM membership.

No original binary or complete disassembly is emitted. Requires iced-x86 1.21.0.
The ASM supplies candidate membership, never authoritative instruction semantics.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from iced_x86 import Decoder, Formatter, FormatterSyntax, InstructionInfoFactory, Register, OpAccess

SHA = '552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301'
SITES = ['0201:0468','04C7:09F6','04C7:0C37','083D:0490','083D:049C','083D:04AC','083D:1698','083D:16A7','083D:18F2','083D:1B3C','0AEA:03D6']
TABLES = [(0x83d,0x45e,23,8),(0x83d,0x1888,23,9),(0x83d,0x1b06,24,8),(0x83d,0x1458,10,0),(0x4c7,0xda0,22,0)]
REGISTER_NAMES={v:k.lower() for k,v in vars(Register).items() if k.isupper() and isinstance(v,int)}
ACCESS_NAMES={v:k.lower() for k,v in vars(OpAccess).items() if k.isupper() and isinstance(v,int)}
FMT = Formatter(FormatterSyntax.INTEL)

def signed16(n):
    n &= 65535
    return n - 65536 if n & 32768 else n

def coordinate_count(n):
    """Pre-call gate, with architectural low-word multiplication and #DE."""
    divisor = signed16(n*n*n)
    if not divisor:
        raise ZeroDivisionError('IDIV #DE before RNG')
    return (500 // abs(divisor)) * (-1 if divisor < 0 else 1)

def census(exe, asm):
    raw = exe.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('wrong source EXE SHA256')
    image = raw[int.from_bytes(raw[8:10],'little')*16:]
    rows = {}
    owners = {}
    owner = None
    for line in asm.read_text().splitlines():
        m = re.match(r'; FUNCTION CANDIDATE ([0-9A-F:]+)', line)
        if m: owner = m[1]
        m = re.match(r'[0-9A-F]+  ([0-9A-F]{4}):([0-9A-F]{4})  ((?:[0-9a-f]{2} )+)',line)
        if not m: continue
        seg,off = int(m[1],16),int(m[2],16)
        if seg not in (0x201,0x4c7,0x83d,0xaea,0xfba,0x11ee): continue
        b = bytes.fromhex(m[3]); pc = f'{seg:04X}:{off:04X}'
        if image[seg*16+off:seg*16+off+len(b)] != b:
            raise ValueError('ASM/source byte mismatch: '+pc)
        rows[pc] = (seg,off,b)
        owners.setdefault(pc,set()).add(owner)
    from csv import DictReader
    root=Path(__file__).resolve().parents[1]
    audit=json.loads((root/'docs/evidence/2026-10-25/RNG_state_reference_audit.json').read_text())
    calls=list(DictReader((root/'docs/evidence/2026-10-25/RNG_DEMO_rng_run_f_calls.csv').open()))
    # Runtime CSV naming is intentionally inspected, not guessed by this generator.
    direct=[e for e in audit['direct_far_edges'] if e['role']=='RNG_wrapper']
    out=[]
    info=InstructionInfoFactory()
    for pc in SITES:
        seg,off,b=rows[pc]
        assert b==bytes.fromhex('9aa001ba0f')
        owner_set=next(e['candidate_owners'] for e in direct if e['pc']==pc)
        effects=[]
        for key,(s,o,encoded) in sorted(rows.items()):
            if s!=seg or not off+5<=o<off+29: continue
            ins=Decoder(16,encoded,ip=o).decode()
            assert ins.len==len(encoded) and not ins.is_invalid
            effects.append({'pc':key,'bytes':encoded.hex(),'instruction':FMT.format(ins),
                'register_effects_iced': [{'register':REGISTER_NAMES[r.register],'access':ACCESS_NAMES[r.access]} for r in info.info(ins).used_registers()],
                'rflags_read':ins.rflags_read,'rflags_written':ins.rflags_written,'rflags_cleared':ins.rflags_cleared,'rflags_set':ins.rflags_set,'rflags_undefined':ins.rflags_undefined})
        out.append({'pc':pc,'candidate_owners':owner_set,'runtime_status':'NOT_OBSERVED_IN_run_f_ONLY','post_call_effects':effects})
    tables=[]
    for seg,off,n,base in TABLES:
        data=image[seg*16+off:seg*16+off+2*n]
        tables.append({'pc':f'{seg:04X}:{off:04X}','sha256':hashlib.sha256(data).hexdigest(),
            'selector_to_target':{str(base+i):f'{seg:04X}:{int.from_bytes(data[2*i:2*i+2],"little"):04X}' for i in range(n)}})
    target_owners=set(o for r in out for o in r['candidate_owners'])
    inbound=[]
    for pc,(s,o,b) in sorted(rows.items()):
        ins=Decoder(16,b,ip=o).decode()
        if b[0]==0xe8:
            target=f'{s:04X}:{ins.near_branch16:04X}'
        elif b[0]==0x9a:
            target=f'{int.from_bytes(b[3:5],"little"):04X}:{int.from_bytes(b[1:3],"little"):04X}'
        else: continue
        if target in target_owners: inbound.append({'pc':pc,'target':target,'candidate_owners':sorted(owners[pc])})
    return {'source_exe_sha256':SHA,'asm_sha256':hashlib.sha256(asm.read_bytes()).hexdigest(),
        'scope':'Byte-matched inherited ASM membership in six selected segments (0201,04C7,083D,0AEA,0FBA,11EE); original EXE bytes decoded with iced in 16-bit mode. Candidate ownership and global reachability remain open.',
        'scoped_asm_unique_byte_matches':len(rows),'sites':out,'jump_tables':tables,'direct_inbound_candidates':inbound,
        'runtime_csv_rows':len(calls),'coordinate_pre_gate':{str(n):('IDIV_DE' if n in (0,64,128,192) else coordinate_count(n)) for n in range(256)},
        'global_rng_coverage':False,'paired_remake_parity':False}

def cpu_contract(exe):
    """Synthetic execution of private original bytes; never original-game runtime."""
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    import unicorn.x86_const as regs
    raw=exe.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA: raise ValueError('wrong source hash')
    image=raw[int.from_bytes(raw[8:10],'little')*16:]
    results=[]
    for seed in [0,1,2,0x7fffffff,0x80000000,0xffffffff,0x12345678]:
        u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,image)
        u.mem_write(0x90000,bytes.fromhex('9aa001ba0f'))
        u.mem_write(0x21fd0+0x24b8,seed.to_bytes(4,'little'))
        initial={'CS':0x9000,'DS':0x21fd,'ES':0x7000,'SS':0x8000,'SP':0xff00,
                 'EAX':0x1234abcd,'ECX':0x2345beef,'EDX':0x3456dead,
                 'BX':0x1234,'BP':0x5678,'SI':0x9abc,'DI':0xdef0,'EFLAGS':0x602}
        for name,val in initial.items(): u.reg_write(getattr(regs,'UC_X86_REG_'+name),val)
        u.emu_start(0x90000,0x90005,count=1000)
        after={n:u.reg_read(getattr(regs,'UC_X86_REG_'+n)) for n in initial}
        state=(seed*214013+2531011)&0xffffffff
        assert int.from_bytes(u.mem_read(0x21fd0+0x24b8,4),'little')==state
        assert after['EAX']==0x12340000|((state>>16)&0x7fff)
        assert after['EDX']==0x34560000|(state>>16)
        assert after['ECX']==0x234543fd
        for n in ('CS','DS','ES','SS','SP','BX','BP','SI','DI'): assert after[n]==initial[n]
        ah=((state>>16)&0x7fff)>>8; flags=after['EFLAGS']
        assert flags&(1|0x80|0x800)==0
        assert bool(flags&0x40)==(ah==0)
        assert bool(flags&4)==(ah.bit_count()%2==0)
        assert flags&0x600==0x600
        results.append({'seed':seed,'state':state,'AX':after['EAX']&65535,'DX':after['EDX']&65535,'CX':after['ECX']&65535})
    return {'status':'SYNTHETIC_CPU_ONLY','source_sha256':SHA,'cases':results,'upper_register_halves_preserved':True,'stack_and_saved_registers_preserved':True,'byte_AH_flags_checked_AF_undefined':True}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cpu-check',action='store_true');p.add_argument('exe',type=Path);p.add_argument('asm',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();result=census(a.exe,a.asm)
    if a.cpu_check: result['original_bytes_synthetic_contract']=cpu_contract(a.exe)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'sites':len(result['sites']),'byte_matched_instructions':result['scoped_asm_unique_byte_matches'],'tables':len(result['jump_tables'])}))
