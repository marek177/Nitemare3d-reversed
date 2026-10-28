from pathlib import Path
import itertools,json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_DS,UC_X86_REG_SS,UC_X86_REG_SP,UC_X86_REG_BP,UC_X86_REG_SI,UC_X86_REG_DI,UC_X86_REG_AX,UC_X86_REG_IP
root=Path(__file__).resolve().parent.parent
def word(b,a):return struct.unpack_from('<H',b,a)[0]
def put(b,a,v):struct.pack_into('<H',b,a,v&65535)
def s(v):return v-65536 if v&32768 else v

def replace(old,new):
 o,n=old[7],new[7];ox0,oy0,ox1,oy1=[s(word(old,a)) for a in (12,14,16,18)];nx0,ny0,nx1,ny1=[s(word(new,a)) for a in (12,14,16,18)]
 if o==0 and n in (2,3):return (ox0<nx0 if n==2 else nx1<ox1) and oy0>ny0
 if o==1 and n in (2,3):return (ox0<nx0 if n==2 else nx1<ox1) and oy1<ny1
 if o==2 and n in (0,1):return nx1>ox1 and (oy1>ny1 if n==0 else oy0<ny0)
 if o==3 and n in (0,1):return nx0<ox0 and (oy1>ny1 if n==0 else oy0<ny0)
 return False

def run(label,old,new,owners=None,counter=5,viewport=(0,7),span=(3,3),projection=1):
 old,new=bytes(old),bytearray(new);put(new,20,span[0]);put(new,24,span[1]);new=bytes(new)
 owners=[0x7200]*16 if owners is None else owners.copy();expected=owners.copy();left=max(s(span[0]&65535),viewport[0]);right=min(s(span[1]&65535),viewport[1]);remain=counter&65535
 if projection:
  for column in range(left,right+1):
   if not expected[column]:expected[column]=0x7000;remain=(remain-1)&65535
   elif replace(new if expected[column]==0x7000 else old,new):expected[column]=0x7000
 expected_al=int(s(remain)<=0)
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,bytes(payload))
 for reg,val in ((UC_X86_REG_CS,renderer_seg),(UC_X86_REG_DS,ds_seg),(UC_X86_REG_SS,ds_seg),(UC_X86_REG_SP,0xdff4),(UC_X86_REG_BP,0xdffe),(UC_X86_REG_SI,0x7000),(UC_X86_REG_DI,0),(UC_X86_REG_AX,projection)):u.reg_write(reg,val)
 u.mem_write(DS+0xdff4,bytes(12));u.mem_write(DS+0xe000,struct.pack('<HHH',0x600,0,0x7000));u.mem_write(DS+0x7000,new);u.mem_write(DS+0x7200,old)
 u.mem_write(DS+viewport_offset,struct.pack('<HH',viewport[0]&65535,viewport[1]&65535));u.mem_write(DS+counter_offset,struct.pack('<H',counter&65535));u.mem_write(DS+owner_offset,struct.pack('<16H',*owners))
 u.emu_start(post_entry,0x600,count=10000)
 actual=list(struct.unpack('<16H',u.mem_read(DS+owner_offset,32)));actual_count=struct.unpack('<H',u.mem_read(DS+counter_offset,2))[0];al=u.reg_read(UC_X86_REG_AX)&255
 assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_IP)==0x600,label
 assert actual==expected and actual_count==remain and al==expected_al,(label,actual,expected,actual_count,remain,al,expected_al)
 assert bytes(u.mem_read(DS+0x7000,28))==new and bytes(u.mem_read(DS+0x7200,28))==old
 assert u.reg_read(UC_X86_REG_SP)==0xe004 and u.reg_read(UC_X86_REG_DS)==ds_seg
 return {'label':label,'old_orientation':old[7],'new_orientation':new[7],'owner3_after':actual[3],'counter_after_signed':s(actual_count),'AL':al,'raw_AX':u.reg_read(UC_X86_REG_AX),'pass':True}

def vec(orientation,coords):
 b=bytearray(28);b[5]=1;b[7]=orientation
 for off,val in zip((12,14,16,18),coords):put(b,off,val)
 return b
def main():
 results=[]
 for o,n,delta in itertools.product(range(4),range(4),itertools.product((-1,0,1),repeat=4)):
  results.append(run(f'orient{o}_{n}_delta{delta}',vec(o,tuple(100+d for d in delta)),vec(n,(100,100,100,100))))
 for o,n in ((0,2),(1,2),(2,0),(3,1)):
  for x,y in itertools.product((-32768,-1,0,32767),repeat=2):
   results.append(run(f'signed{o}_{n}_{x}_{y}',vec(o,(x,y,x,y)),vec(n,(0,0,0,0))))
 for counter in (1,0,-1,-32768,32767):
  results.append(run(f'empty_owner_counter{counter}',vec(0,(100,100,100,100)),vec(2,(100,100,100,100)),owners=[0]*16,counter=counter))
 for label,span,viewport,counter,projection in [('clip',(2,5),(3,4),3,1),('outside_positive',(9,12),(0,7),3,1),('outside_counter_zero',(9,12),(0,7),0,1),('reversed',(6,2),(0,7),3,1),('projection_rejected',(3,3),(0,7),0,0),('projection_rejected_negative',(3,3),(0,7),-1,0)]:
  results.append(run(label,vec(0,(100,100,100,100)),vec(2,(100,100,100,100)),owners=[0]*16,counter=counter,viewport=viewport,span=span,projection=projection))
 out={'scope':'POST_PROJECTION_ORIGINAL_OWNER_CONFLICT_BODY','build':build,'entry':f'{renderer_seg:04x}:{renderer_offset+26:04x}','prepared_return':'0000:0600','projection_and_prologue_executed':False,'hooks':False,'stubs':False,'cases':len(results),'passed':len(results),'game_runtime':False,'results':results}
 (root/'pass5/evidence'/f'owner_{build}.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2))

if __name__ == '__main__':
 dsproof=json.loads((root/'pass3/evidence/xlat_proofs.json').read_text())
 for cfg in json.loads((root/'pass5/evidence/scopes.json').read_text()):
  build=cfg['build'];b=(root/'analysis/inputs'/('DOS'+build+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);payload=bytearray(b[h[4]*16:])
  for k in range(h[3]):
   off,seg=struct.unpack_from('<HH',b,h[12]+4*k);j=seg*16+off;struct.pack_into('<H',payload,j,(struct.unpack_from('<H',payload,j)[0]+0x1000)&65535)
  renderer_seg,renderer_offset=map(lambda x:int(x,16),cfg['renderer_entry'].split(':'));pos=renderer_seg*16+renderer_offset-0x10000;post_entry=renderer_seg*16+renderer_offset+26
  assert payload[pos+35:pos+37]==b'\x3b\x06' and payload[pos+61:pos+63]==b'\x81\xc7'
  viewport_offset=struct.unpack_from('<H',payload,pos+37)[0]-2;owner_offset=struct.unpack_from('<H',payload,pos+63)[0];counter_offset=owner_offset-2
  ds_seg=int(next(x for x in dsproof if x['build']==build)['ds'],16);DS=ds_seg*16
  main()
