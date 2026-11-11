"""Independently validate historical ASM boundaries and audit callback operands.
Usage: python scan_win110_callback_references.py EXE ASM DECODER_DIR OUT_DIR
Historical reachability labels are not trusted or promoted.
"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
exe,asm,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,InstructionInfoFactory,MemorySizeExt,Register,OpAccess
b=exe.read_bytes();sha=hashlib.sha256(b).hexdigest();assert sha=='12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481'
ne=struct.unpack_from('<I',b,60)[0];w=lambda p:struct.unpack_from('<H',b,p)[0];segments={}
for n in range(1,w(ne+28)+1):
    sector,size,flags,_=struct.unpack_from('<4H',b,ne+w(ne+34)+(n-1)*8)
    if sector and not flags&1:segments[n]=b[sector<<w(ne+50):(sector<<w(ne+50))+(size or 65536)]
fmt=Formatter(FormatterSyntax.INTEL);factory=InstructionInfoFactory();seen=set();refs=[];mismatches=[];literal=[];indexed_writes=0;parsed=0
rx=re.compile(r'^([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})\s+((?:[0-9A-Fa-f]{2}\s+)+)')
writes={OpAccess.WRITE,OpAccess.COND_WRITE,OpAccess.READ_WRITE,OpAccess.READ_COND_WRITE}
for lineno,line in enumerate(asm.read_text(encoding='utf-8-sig').splitlines(),1):
    m=rx.match(line)
    if not m:continue
    parsed+=1;s,ip=int(m[1],16),int(m[2],16);raw=bytes.fromhex(m[3]);key=(s,ip)
    if key in seen:continue
    seen.add(key)
    if s not in segments or segments[s][ip:ip+len(raw)]!=raw:
        mismatches.append(dict(line=lineno,segment=s,offset=ip,reason='byte_or_segment_mismatch'));continue
    ins=Decoder(16,raw,ip=ip).decode()
    if ins.is_invalid or ins.len!=len(raw):
        mismatches.append(dict(line=lineno,segment=s,offset=ip,reason='invalid_or_boundary_mismatch'));continue
    for mem in factory.info(ins).used_memory():
        width=MemorySizeExt.size(mem.memory_size)
        if mem.access in writes and (mem.base!=Register.NONE or mem.index!=Register.NONE):indexed_writes+=1
        if mem.base==Register.NONE and mem.index==Register.NONE and mem.displacement<0x20dc and mem.displacement+width>0x20d0:
            refs.append(dict(segment=s,offset=ip,asm_line=lineno,bytes=raw.hex(),instruction=fmt.format(ins),memory_segment_register=mem.segment,address=mem.displacement,width=width,access_enum=mem.access,writes=mem.access in writes,status='PARTIAL',scope='literal effective offset only; runtime segment identity unresolved'))
    if any(raw[i:i+2] in (b'\xd0\x20',b'\xd2\x20',b'\xd4\x20',b'\xd6\x20',b'\xd8\x20',b'\xda\x20') for i in range(len(raw)-1)):
        literal.append(dict(segment=s,offset=ip,bytes=raw.hex(),instruction=fmt.format(ins),scope='byte-pattern candidate; may be immediate, displacement or other bytes'))
out.mkdir(parents=True,exist_ok=True)
def save(name,rows,fields):
    with (out/name).open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
save('direct_memory_references.csv',refs,['segment','offset','asm_line','bytes','instruction','memory_segment_register','address','width','access_enum','writes','status','scope'])
save('validation_issues.csv',mismatches,['line','segment','offset','reason'])
save('literal_candidates.csv',literal,['segment','offset','bytes','instruction','scope'])
result=dict(exe_sha256=sha,asm_path=str(asm),asm_sha256=hashlib.sha256(asm.read_bytes()).hexdigest(),parsed_lines=parsed,unique_starts=len(seen),independently_validated_starts=len(seen)-len(mismatches),validation_issues=len(mismatches),callback_direct_memory_references=len(refs),callback_direct_memory_writes=sum(r['writes'] for r in refs),indexed_write_operands_not_alias_resolved=indexed_writes,literal_pattern_candidates=len(literal),global_no_write_claim=False,reachability_verified=False,new_deep_verified_bytes=0,runtime_tests=0)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
