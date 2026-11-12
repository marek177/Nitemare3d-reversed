"""Byte-level independent model for original0768:0024 mode0. Fixtures have no RAM side effects."""
import struct
class InitModel:
 def __init__(self,ram,ds,cfg):self.ram=bytearray(ram);self.ds=ds;self.cfg=cfg;self.writes=[];self.calls=[];self.allocations=[];self.fatal=None
 def get(self,off,size=2):return int.from_bytes(self.ram[self.ds*16+off:self.ds*16+off+size],'little')
 def put(self,address,size,value,role):
  value &= (1<<(8*size))-1;self.ram[address:address+size]=value.to_bytes(size,'little');self.writes.append(dict(address=address,size=size,value=value,role=role))
 def dg(self,off,size,value,role):self.put(self.ds*16+off,size,value,role)
 def call(self,name,args,AX=0,DX=0,BX=0):self.calls.append(dict(name=name,args=args,AX=AX,DX=DX,BX=BX))
 def error(self,message):self.call('fatal',[message]);self.fatal=message
 def allocate(self,size):
  i=len(self.allocations);address=(0x60000+i*0x2010) if i<14 else (0x80000+(i-14)*0xc20)
  if i==self.cfg['fail_allocation']:address=0
  off,seg=address&15,address>>4
  if 'allocation_fars' in self.cfg:off,seg=self.cfg['allocation_fars'][i];address=seg*16+off
  self.allocations.append(dict(index=i,size=size,address=address));self.call('far_allocate',[size],off,seg);return address,off,seg
 def run(self):
  c=self.cfg
  for i in range(14):
   address,off,seg=self.allocate(0x2006);p=0x34cc+4*i;self.dg(p,2,off,'far buffer offset');self.dg(p+2,2,seg,'far buffer segment')
   if not address:self.error(0xb86 if i<10 else 0xbba);return
   self.put(address+4,2,0,'wall/sound marker');self.put(address,4,0,'wall/sound timestamp')
  self.call('probe_kib',[],c['probe']);self.dg(0x3cb4,2,c['probe'],'probe KiB')
  self.call('crt_probe',[],c['crt_probe']);self.dg(0x3cb0,2,c['crt_probe'],'second probe')
  numerator=(c['probe']-70)*1024;n=(abs(numerator)//3074)*(-1 if numerator<0 else 1);self.dg(0x3504,2,n,'initial object slot count')
  if n>128:n=128
  self.dg(0x3504,2,n,'signed upper cap128')
  if n<1:self.error(0xbee);return
  table=self.get(0x2560)*16
  for i in range(n):
   address,off,seg=self.allocate(0xc02);self.put(table+4*i,2,off,'object vector offset');self.put(table+4*i+2,2,seg,'object vector segment')
   if not address:self.error(0xc22);return
   self.put(address,2,0,'object owner')
  enabled=self.get(0x3cce,1)
  if enabled:
   self.call('detect_4300',[],0x4300)
   if not(c['detect_AL']&0x80):enabled=0;self.dg(0x3cce,1,0,'disable absent manager')
   else:
    self.call('detect_4310',[],0x4310);self.dg(0x350e,2,c.get('manager_offset',0x100),'manager offset');self.dg(0x3510,2,c.get('manager_segment',0x4f00),'manager segment')
    q=c['capacity'];self.call('manager_08',[],q,c.get('query_DX',0x2468),0x7800|c['query_error']);self.dg(0x3508,2,q,'queried KiB');self.dg(0x3cb8,2,q,'uncapped query');self.dg(0x350a,2,0,'XMS used reset')
    signed=lambda x:x if x<32768 else x-65536
    if signed(q)>2048:q=2048
    self.dg(0x3508,2,q,'signed upper cap2048')
    if signed(q)<64:enabled=0;self.dg(0x3cce,1,0,'disable signed capacity below64')
    else:
     ok,error,returned_dx=c['allocate_reply'];self.call('manager_09',[q],ok,returned_dx,0x7800|error)
     result_dx=0 if ok else (error<<8)|(returned_dx&255)
     if signed(result_dx)<0:enabled=0;self.dg(0x3cce,1,0,'disable negative allocation DX')
     else:
      handle=returned_dx if ok else 0;self.dg(0x3506,2,handle,'stored XMS handle')
      ok,error,returned_dx=c['lock_reply'];self.call('manager_0C',[handle],ok,returned_dx,0x7800|error)
      result_dx=returned_dx if ok else error<<8
      if signed(result_dx)<0:
       ok,error,returned_dx=c['release_reply'];self.call('manager_0A',[handle],ok,returned_dx,0x7800|error)
       enabled=0;self.dg(0x3cce,1,0,'disable negative lock DX');self.call('warning',[0xc56])
  self.dg(0x350c,1,enabled,'saved initialized BYTE')
