from pathlib import Path
import hashlib,itertools,json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_DS,UC_X86_REG_SS,UC_X86_REG_SP,UC_X86_REG_IP
root=Path(__file__).resolve().parent.parent
def get(b,a):return struct.unpack_from('<H',b,a)[0]
def put(b,a,v):struct.pack_into('<H',b,a,v&65535)
def signed(v):return v-65536 if v&32768 else v

def model(records,vectors,cells):
 records=[bytearray(x) for x in records];vectors={k:bytearray(v) for k,v in vectors.items()};cells=dict(cells)
 for r in records:
  if get(r,12)!=2:continue
  put(r,12,0)
  for slot in range(4):
   pointer=get(r,slot*2)
   if not pointer:continue
   v=vectors[pointer];start,end=(12,16) if slot in (0,2) else (14,18)
   if signed(get(v,start))<signed(get(v,end)):
    put(v,start,get(v,start)+2);put(r,12,2)
  if get(r,12)==0:
   for other in records:
    if any(get(other,k)!=0 and get(other,k)==get(r,k) for k in (0,4,2,6)):
     for k in (0,2,4,6):
      pointer=get(other,k)
      if pointer:vectors[pointer][5]&=254
     cells[(get(other,10)<<4)+get(other,8)]=b'\0\0';put(other,12,0)
 return [bytes(x) for x in records],{k:bytes(v) for k,v in vectors.items()},cells

def run_case(label,records,vectors,cells,ticks=1):
 expected=model(records,vectors,cells)
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,bytes(payload))
 for reg,val in ((UC_X86_REG_CS,0x1000),(UC_X86_REG_DS,ds_seg),(UC_X86_REG_SS,ds_seg),(UC_X86_REG_SP,0xe000)):u.reg_write(reg,val)
 u.mem_write(pool_base,struct.pack('<HH',0,len(records)))
 for j,r in enumerate(records):u.mem_write(pool_base+0x34f6+14*j,bytes(r))
 for pointer,v in vectors.items():u.mem_write(ds_base+pointer,bytes(v))
 for address,v in cells.items():u.mem_write(address,v)
 timeline=[]
 for tick in range(ticks):
  if tick:expected=model(*expected)
  u.emu_start((0x10000+entry),(0x10000+end),count=30000)
  assert u.reg_read(UC_X86_REG_IP)==end,label
  actual=([bytes(u.mem_read(pool_base+0x34f6+14*j,14)) for j in range(len(records))],{p:bytes(u.mem_read(ds_base+p,0x1c)) for p in vectors},{a:bytes(u.mem_read(a,2)) for a in cells})
  assert actual==expected,(label,tick,actual,expected)
  assert u.reg_read(UC_X86_REG_DS)==ds_seg and u.reg_read(UC_X86_REG_SP)==0xe000,label
  timeline.append([get(r,12) for r in actual[0]])
 return {'label':label,'ticks':ticks,'state_timeline':timeline,'states_after':[get(r,12) for r in actual[0]],'cells_after':{hex(a):v.hex() for a,v in actual[2].items()},'vector_starts_after':{hex(p):[signed(get(v,12)),signed(get(v,14))] for p,v in actual[1].items()},'pass':True}

def make_record(j,state,presence,start,end):
 r=bytearray(14);vectors={};celloffset=0x7800+j*4
 for slot in range(4):
  if not presence&(1<<slot):continue
  pointer=0x7000+j*0x100+slot*0x20;v=bytearray(0x1c);v[5]=0xa1
  for a in (12,14):put(v,a,start)
  for a in (16,18):put(v,a,end)
  put(r,slot*2,pointer);vectors[pointer]=v
 put(r,8,celloffset);put(r,10,ds_seg);put(r,12,state)
 return r,vectors,{ds_base+celloffset:b'\x55\xaa'}

def main():
    results=[]
    for state,presence,pair in itertools.product((0,1,2,3),range(16),((100,100),(100,101),(100,102),(100,103),(101,100),(-2,0),(32766,32767))):
     r,v,c=make_record(0,state,presence,*pair);results.append(run_case(f'state{state}_mask{presence}_coords{pair}',[r],v,c))
    results.append(run_case('empty_pool',[],{},{}))
    for slot in range(4):
     r0,v0,c0=make_record(0,2,15,100,100);r1,v1,c1=make_record(1,2,15,0,4)
     put(r1,slot*2,get(r0,slot*2));results.append(run_case(f'same_slot_link_{slot}',[r0,r1],v0|v1,c0|c1))
    for slot in range(4):
     r0,v0,c0=make_record(0,2,15,100,100);r1,v1,c1=make_record(1,2,15,0,4)
     put(r1,((slot+1)%4)*2,get(r0,slot*2));results.append(run_case(f'cross_slot_link_{slot}',[r0,r1],v0|v1,c0|c1))
    r0,v0,c0=make_record(0,2,15,100,100);r1,v1,c1=make_record(1,2,15,0,4);r2,v2,c2=make_record(2,2,15,0,4)
    put(r1,0,get(r0,0));put(r2,2,get(r1,2));results.append(run_case('nontransitive_three_record_chain',[r0,r1,r2],v0|v1|v2,c0|c1|c2))
    for target_end,ticks in ((101,2),(102,2),(103,3),(100,2),(32767,3)):
     r,v,c=make_record(0,2,15,32766 if target_end==32767 else 100,target_end);results.append(run_case(f'temporal_end_{target_end}',[r],v,c,ticks))
    r0,v0,c0=make_record(0,2,15,100,100);r1,v1,c1=make_record(1,2,15,0,4);put(r1,0,get(r0,0));results.append(run_case('reverse_order_link',[r1,r0],v0|v1,c0|c1))
    out={'scope':'CONTROLLED_ORIGINAL_HANDLER_WITH_EMPTY_FIRST_POOL','build':build,'original_entry':f'1000:{entry:04x}','stop_before_retf':f'1000:{end:04x}','cases':len(results),'passed':len(results),'external_stubs':False,'hooks':False,'game_runtime':False,'results':results}
    (root/'pass4/evidence'/f'motion_{build}.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2))


if __name__ == '__main__':
 proofs=json.loads((root/'pass3/evidence/xlat_proofs.json').read_text())
 for build in ['10','11','12','15','17','18']:
  b=(root/'analysis/inputs'/('DOS'+build+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);payload=bytearray(b[h[4]*16:])
  for k in range(h[3]):
   off,seg=struct.unpack_from('<HH',b,h[12]+4*k);j=seg*16+off;struct.pack_into('<H',payload,j,(struct.unpack_from('<H',payload,j)[0]+0x1000)&65535)
  entry=0xae0 if build in ['10','11','12'] else 0xaea
  end=int(json.loads((root/'pass4/evidence'/('DOS'+build)/'boundary.json').read_text())['end'].split(':')[1],16)
  assert payload[entry+6]==0xb8;pool_seg=struct.unpack_from('<H',payload,entry+7)[0];pool_base=pool_seg*16
  ds_seg=int(next(x for x in proofs if x['build']==build)['ds'],16);ds_base=ds_seg*16
  main()
