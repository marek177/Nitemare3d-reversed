from pathlib import Path
import json,struct,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[]
meta=json.loads((root/'pass58/evidence/store.json').read_text())['locations'];cache=json.loads((root/'pass50/evidence/cache.json').read_text())['locations'];xm=json.loads((root/'pass56/evidence/xms.json').read_text())['locations'];tr=json.loads((root/'pass55/evidence/transfer.json').read_text())['locations']
for m in meta:
 v=m['build'];c=next(x for x in cache if x['build']==v);x=next(x for x in xm if x['build']==v);t=next(x for x in tr if x['build']==v);ds=next(q['actual_DS'] for q in json.loads((root/'pass7/evidence/specs.json').read_text()) if q['build']==v);cs,entry=[int(a,16) for a in m['table_preparer_entry'].split(':')];table=int(c['resource_table'],16);ptrs=int(c['cache_pointers'],16);fcs,fip=[int(a,16) for a in t['entry'].split(':')];fileaddr=fcs*16+fip;driver=next(r for r in x['wrapper_instructions'] if r['bytes'].startswith('26ff1e'));driveraddr=int(x['wrapper_entry'].split(':')[0],16)*16+int(driver['address'].split(':')[1],16)
 b=(root/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+k*4);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 for length,alias,cap in itertools.product([0,1025,8193],['none','earlier_same','later_different'],[0,4]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xc000;ident=10;trace=[]
  for j in range(79):u.mem_write(ds*16+table+j*6,struct.pack('<Hi',1,1000+j))
  u.mem_write(ds*16+table+ident*6,struct.pack('<Hi',length,123))
  if alias=='earlier_same':u.mem_write(ds*16+table+9*6,struct.pack('<Hi',length,123))
  if alias=='later_different':u.mem_write(ds*16+table+11*6,struct.pack('<Hi',3,123))
  before=bytes(u.mem_read(ds*16+table,79*6));u.mem_write(ds*16+ptrs,struct.pack('<HH',0x200,0x6000))
  for a,n in [(int(m['capacity_global'],16),cap),(int(m['used_global'],16),1),(int(x['scratch_segment_global'],16),0x5000),(int(x['source_handle_global'],16),0x1234)]:u.mem_write(ds*16+a,struct.pack('<H',n))
  def hook(uc,a,n,_):
   if a==fileaddr:
    st=uc.reg_read(UC_X86_REG_SP);args=list(struct.unpack('<5H',uc.mem_read(ds*16+st+4,10)));trace.append(['file',args]);ip,retcs=struct.unpack('<HH',uc.mem_read(ds*16+st,4));uc.reg_write(UC_X86_REG_SP,st+4);uc.reg_write(UC_X86_REG_CS,retcs);uc.reg_write(UC_X86_REG_IP,ip)
   elif a==driveraddr:
    fields=list(struct.unpack('<IHIHI',uc.mem_read(uc.reg_read(UC_X86_REG_DS)*16+uc.reg_read(UC_X86_REG_SI),16)));trace.append(['xms',fields]);uc.reg_write(UC_X86_REG_AX,1);uc.reg_write(UC_X86_REG_BL,0);uc.reg_write(UC_X86_REG_IP,a-uc.reg_read(UC_X86_REG_CS)*16+5)
  u.hook_add(UC_HOOK_CODE,hook);u.mem_write(ds*16+sp,struct.pack('<3H',0x600,0,ident))
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=10000);eligible=length>0 and length<=8192 and alias!='earlier_same';stored=eligible and cap>=3
  assert trace==([['file',[0x206,0x6000,123,0,length]]]+([['xms',[2048,0,0x60000206,0x1234,1024]]] if stored else []) if eligible else []),(v,length,alias,cap,trace)
  after=bytearray(before)
  if stored:
   struct.pack_into('<i',after,ident*6+2,-1024)
   if alias=='later_different':struct.pack_into('<i',after,11*6+2,-1024)
  assert bytes(u.mem_read(ds*16+table,79*6))==bytes(after);assert struct.unpack('<H',u.mem_read(ds*16+int(m['used_global'],16),2))[0]==(3 if stored else 1);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,length=length,alias=alias,capacity=cap,stored=stored,trace=trace,passed=True))
(root/'pass58/evidence/tableprepare.json').write_text(json.dumps(dict(cases=len(results),scope='Original table preparer, XMS store and wrapper; SND transfer callee and XMS driver boundary mocked; synthetic 79-entry resource table.',results=results),indent=2));print(len(results),'table cases passed')
