import pathlib,json,struct,random,hashlib,csv
from unicorn import *
from unicorn.x86_const import *
R=pathlib.Path(__file__).resolve().parents[1];rnd=random.Random(20261104);out=[]
regs=[UC_X86_REG_AX,UC_X86_REG_BX,UC_X86_REG_CX,UC_X86_REG_DX,UC_X86_REG_SI,UC_X86_REG_DI,UC_X86_REG_BP,UC_X86_REG_DS,UC_X86_REG_ES]
# DOS 0201:000A: 100 strided byte writes, preserving non-target bytes.
image=(R/'VERSIONS/DOS/N3D-UNFU.exe.loaded.bin').read_bytes();code=image[0x201*16+10:0x201*16+26];assert code.hex()=='bbf250c6070183c31281fbfa5772f4cb'
# Windows ordinal 1: physical NE segment offset, not MZ image arithmetic.
b=(R.parent/'inputs/nite3/windows/nite3w - 110.exe').read_bytes();layout=json.loads((R/'VERSIONS/WIN16/nite3w - 110.exe.layout.json').read_text());ex=layout['exports'][0];sg=layout['segments'][ex['segment']-1];wcode=b[sg['file_offset']+ex['offset']:sg['file_offset']+ex['offset']+14];assert wcode.hex()=='8cd0558bec1e8ed8b850021fc9cb'
for kind,blob in [('DOS_stride_init',code),('WIN_export_ordinal_1',wcode)]:
 cases=[]
 for idx in range(128):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);cs=0x1000;ss=0x7000;ds=0x4000;sp=0x8000;u.mem_write(cs*16,blob);memory=bytes(rnd.randrange(256)for _ in range(65536));u.mem_write(ds*16,memory)
  vals={r:rnd.randrange(65536) for r in regs};vals[UC_X86_REG_DS]=ds
  for r,v in vals.items():u.reg_write(r,v)
  flags=(rnd.randrange(65536)&0xCD5)|2;u.reg_write(UC_X86_REG_EFLAGS,flags);u.reg_write(UC_X86_REG_CS,cs);u.reg_write(UC_X86_REG_SS,ss);u.reg_write(UC_X86_REG_SP,sp);u.mem_write(ss*16+sp,struct.pack('<HH',0x100,0x2000));stop=0x20100
  u.emu_start(cs*16,stop,count=2000)
  assert u.reg_read(UC_X86_REG_CS)==0x2000 and u.reg_read(UC_X86_REG_IP)==0x100
  assert u.reg_read(UC_X86_REG_SP)==sp+4
  actual=bytes(u.mem_read(ds*16,65536));expected=bytearray(memory)
  if kind=='DOS_stride_init':
   for k in range(100):expected[0x50f2+18*k]=1
   assert u.reg_read(UC_X86_REG_BX)==0x57fa
   # CMP equal fixes six arithmetic flags; all other modeled low flags preserved.
   assert u.reg_read(UC_X86_REG_EFLAGS)&0x8d5==0x44
   assert (u.reg_read(UC_X86_REG_EFLAGS)^flags)&~0x8d5&0xffff==0
   altered=UC_X86_REG_BX
  else:
   assert u.reg_read(UC_X86_REG_AX)==0x250
   assert u.reg_read(UC_X86_REG_EFLAGS)&0xffff==flags
   altered=UC_X86_REG_AX
  assert actual==bytes(expected)
  for r,v in vals.items():
   if r!=altered:assert u.reg_read(r)==v,(kind,r)
  cases.append({'case':idx,'result':'PASS','initial_flags':flags,'initial_registers':{str(r):v for r,v in vals.items()}})
 out.append({'function':kind,'tests':len(cases),'status':'PASS','scope':'isolated Unicorn CPU execution; not original gameplay runtime','code_hex':blob.hex(),'cases':cases})
(R/'RUNTIME_EVIDENCE/isolated_function_emulation.json').write_text(json.dumps(out,indent=2));print([(x['function'],x['tests'],x['status'])for x in out])
# Locate same byte bodies in every available unique DOS snapshot and exported Win entry.
matches=[]
for p in sorted((R/'VERSIONS/DOS').glob('*.loaded.bin')):
 data=p.read_bytes();positions=[];pos=data.find(code)
 while pos>=0:positions.append(hex(pos));pos=data.find(code,pos+1)
 matches.append({'file':p.name,'scope':'loaded memory snapshot','signature':'DOS_stride_init','locations':positions,'classification':'IDENTICAL_BYTES' if len(positions)==1 else 'UNKNOWN_MATCH'})
for lp in sorted((R/'VERSIONS/WIN16').glob('*.layout.json')):
 name=lp.name.removesuffix('.layout.json');raw=(R.parent/'inputs/nite3/windows'/name).read_bytes();j=json.loads(lp.read_text())
 if name=='MAPS.EXE':continue
 for exp in j['exports']:
  sg=j['segments'][exp['segment']-1];off=sg['file_offset']+exp['offset'];got=raw[off:off+14]
  matches.append({'file':name,'scope':'NE export ordinal '+str(exp['ordinal']),'signature':'WIN_export_ordinal_1','locations':[f'{exp["segment"]:04x}:{exp["offset"]:04x}'],'bytes':got.hex(),'classification':'IDENTICAL_BYTES'if got==wcode else 'MODIFIED_INSTRUCTIONS'})
(R/'ASM_DIFF/audited_function_cross_version.json').write_text(json.dumps(matches,indent=2));print(json.dumps(matches,indent=2))
