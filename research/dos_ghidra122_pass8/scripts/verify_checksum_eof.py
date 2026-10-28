from pathlib import Path
import csv,json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent
out=root/'pass8/evidence';out.mkdir(parents=True,exist_ok=True)
results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);i=16*seg+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'))
 cs,callback=map(lambda x:int(x,16),q['callback_entry'].split(':'));base=cs*16
 near=[r for r in rows if r['address'].startswith(f'{cs:04x}:') and callback<=int(r['address'].split(':')[1],16)<int(q['mode_targets'][1].split(':')[1],16) and r['bytes'].startswith('e8')]
 site=int(near[0]['address'].split(':')[1],16);entry=(site+3+struct.unpack('<h',bytes.fromhex(near[0]['bytes'])[1:])[0])&65535
 body=[r for r in rows if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<callback]
 calls=[r for r in body if r['bytes'].startswith('9a')];assert len(calls)==6
 kinds=['open','open_error','read','read','checksum_error','close'];sites={base+int(r['address'].split(':')[1],16):kind for r,kind in zip(calls,kinds)}
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',exe_sha256=hashlib.sha256(b).hexdigest(),instructions=body))
 for data in [b'',b'\x00',b'\x01',b'\xff',b'\x12\x34',bytes(range(53))]:
  for limit in [0,len(data)+2,0xffffffff]:
   for seed in [0,0xa5]:
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));ds=q['actual_DS'];sp=0xe000;stream=0x9000
    u.mem_write(ds*16+sp,struct.pack('<HHHIH',0x600,0,0x9100,limit,0));u.mem_write(ds*16+sp-12,bytes([seed]))
    for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
    state=dict(reads=0,fold=None,closed=False,error=False);fold=0x7b
    count=len(data)+1 if limit==0 else (0 if limit&0x80000000 else limit)
    last=seed
    for i in range(count):
     if i<len(data):last=data[i]
     fold^=last
    u.mem_write(ds*16+sp+10,struct.pack('<H',fold))
    def hook(uc,a,n,_):
     if a not in sites:return
     kind=sites[a];stack=ds*16+uc.reg_read(UC_X86_REG_SP)
     if kind=='open':uc.reg_write(UC_X86_REG_AX,stream)
     elif kind=='read':
      dst,size,num,handle=struct.unpack('<4H',uc.mem_read(stack,8));assert (size,num,handle)==(1,1,stream)
      i=state['reads'];state['reads']+=1
      if i<len(data):uc.mem_write(ds*16+dst,data[i:i+1]);uc.reg_write(UC_X86_REG_AX,1)
      else:uc.mem_write(ds*16+stream+6,b'\x10');uc.reg_write(UC_X86_REG_AX,0)
     elif kind=='close':state['closed']=True;state['fold']=uc.mem_read(ds*16+sp-11,1)[0]
     else:state['error']=True;uc.emu_stop();return
     uc.reg_write(UC_X86_REG_IP,a-base+5)
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start(base+entry,0x600,count=100000)
    assert state['reads']==count and state['fold']==fold and state['closed'] and not state['error'],(v,data,limit,seed,state,fold)
    assert u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_CS)==0
    results.append(dict(build=v,data_hex=data.hex(),limit=limit,initial_local_byte=seed,**state,passed=True))
(out/'checksum_eof_emulation.json').write_text(json.dumps(dict(scope='Original complete validator; mocked fopen/fread/fclose. Failed fread preserves destination and sets EOF. No actual CRT or DOS executed.',cases=len(results),results=results),indent=2))
(out/'checksum_locations.json').write_text(json.dumps(locations,indent=2))
print(len(results),'passed')
