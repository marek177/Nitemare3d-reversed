"""python audit_door_early_version_delta.py DECODER OUT
Instruction sequence alignment identifies real early-version instruction differences.
"""
import csv,difflib,json,sys
from pathlib import Path
decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,Register
fmt=Formatter(FormatterSyntax.INTEL);root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');comp=list(csv.DictReader((out/'dos_version_comparison.csv').open()));rows=[]
def tokens(label):
 r=next(x for x in comp if x['version_label']==label);b=(root/('N3D-'+label)/'unpacked_image.bin').read_bytes();a,z=int(r['start']),int(r['end_exclusive']);ip=int(r['ip']);result=[]
 for i in Decoder(16,b[a:z],ip=ip):
  if i.is_invalid:raise ValueError('invalid linear decode')
  off=i.ip-ip;raw=bytearray(b[a+off:a+off+i.len]);d=Decoder(16,bytes(raw),ip=i.ip);j=d.decode();co=d.get_constant_offsets(j)
  if i.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
   for q,n in ((co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)):
    if n:raw[q:q+n]=bytes(n)
  if co.displacement_size and ((i.memory_base==Register.NONE and i.memory_index==Register.NONE) or (raw[0]==0xf6 and i.memory_base==Register.BX)):
   raw[co.displacement_offset:co.displacement_offset+co.displacement_size]=bytes(co.displacement_size)
  result.append((raw.hex(),i.ip,fmt.format(i)))
 return result
reference=tokens('20')
for label in ('10','11','12'):
 old=tokens(label);m=difflib.SequenceMatcher(a=[x[0] for x in old],b=[x[0] for x in reference],autojunk=False)
 for kind,a,z,c,e in m.get_opcodes():
  if kind=='equal':continue
  rows.append(dict(version=label,alignment=kind,old=[dict(ip=x[1],asm=x[2],normalized_bytes=x[0]) for x in old[a:z]],dos20=[dict(ip=x[1],asm=x[2],normalized_bytes=x[0]) for x in reference[c:e]]))
(out/'early_version_instruction_deltas.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows,indent=2))
