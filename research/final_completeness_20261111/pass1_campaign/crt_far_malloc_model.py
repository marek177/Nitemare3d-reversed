"""Independent byte-level model: whole CRT2065 scan, non-PSP growth and fresh DOS48 block.
PSP-flag4 growth and callback bodies intentionally outside this model.
"""
import struct
class FarMallocModel:
 def __init__(self,ram,ds):self.ram=bytearray(ram);self.ds=ds;self.writes=[];self.calls=[];self.scans=[];self.result=(0,0)
 def word(self,a):return struct.unpack_from('<H',self.ram,a)[0]
 def dg(self,o):return self.word(self.ds*16+o)
 def put(self,a,v):v&=65535;struct.pack_into('<H',self.ram,a,v);self.writes.append((a,2,v))
 def far(self,a):o,s=struct.unpack_from('<HH',self.ram,a);return o,s
 def scan(self,seg,wanted):
  b=seg*16;first,cursor,tail=(self.word(b+x) for x in (6,8,10));passes=[(cursor,tail)]+([] if cursor==first else [(first,cursor-1)]);self.scans.append(seg)
  for start,bound in passes:
   pos=start
   for j in range(10000):
    tag=self.word(b+pos)
    if tag&1:
     size=tag-1
     if size>=wanted:
      found=pos+2;self.put(b+pos,wanted);new=found+wanted
      if size!=wanted:self.put(b+new,size-wanted-1)
      self.put(b+8,new);return found
     nextpos=pos+2+size;nexttag=self.word(b+nextpos)
     if nexttag&1:self.put(b+pos,size+nexttag+2);continue
     pos=nextpos;tag=nexttag
    if pos>=bound:break
    pos+=2+tag
   else:raise AssertionError('invalid synthetic/native heap chain')
  self.put(b+8,first);return None
 def grow(self,seg,wanted,replies):
  b=seg*16;flags=self.word(b+2)
  if not(flags&1):return False
  assert not(flags&4),'PSP growth outside current model'
  first,cursor,tail=(self.word(b+o) for o in (6,8,10));pos=first if cursor==tail else cursor;last=None
  while pos!=tail:
   last=pos;pos+=2+(self.word(b+pos)&0xfffe)
   assert pos<=tail
  assert last is not None
  tag=self.word(b+last);current=self.word(b+4)
  if not current:return False
  adjusted=(wanted-tag+1)&65535 if tag&1 else wanted
  needed=((adjusted+2)&65535)+current
  if needed>65535:return False
  quantum=self.dg(0x2344)
  if quantum==0x2000:alignment=0x2000
  else:
   lower=0x8000
   while lower and lower>=quantum:lower>>=1
   alignment=(lower<<1)&65535 if lower>=8 else 16
  for align in ([alignment,16] if alignment!=16 else [16]):
   total=align-1+needed;candidate=0 if total>65535 else total&(~(align-1)&65535);paragraphs=candidate>>4 or 0x1000
   success,AX=replies.pop(0) if replies else (False,8);self.calls.append(dict(kind='DOS4A',ES=seg,paragraphs=paragraphs,success=success,segment_or_error=AX))
   if success:
    delta=(candidate-current)&65535;newtail=(tail+delta)&65535;self.put(b+4,candidate);self.put(b+8,last);self.put(b+tail,delta-1);self.put(b+newtail,0xfffe);self.put(b+10,newtail);return True
  return False
 def allocate(self,request,os_replies=(),resize_replies=()):
  if request>0xffe8:return self.result
  wanted=(request+1)&0xfffe;root=self.ds*16+0x2336;head=self.far(root)[1];cached=self.far(root+4)[1];chain=[];s=head
  while s:
   assert s not in chain;chain.append(s);o,s=self.far(s*16+12);assert o==0
  if chain:
   at=chain.index(cached);order=chain[at:]+chain[:at]
   for s in order:
    p=self.scan(s,wanted)
    if p is not None:self.put(root+6,s);self.put(root+4,0);self.result=(p,s);return self.result
   resize_replies=list(resize_replies)
   for s in order:
    if self.grow(s,wanted,resize_replies):
     p=self.scan(s,wanted);assert p is not None;self.put(root+6,s);self.put(root+4,0);self.result=(p,s);return self.result
  size=(wanted+39)&0xfff0;paragraphs=size//16 if size else 4096
  for success,segment in os_replies:
   self.calls.append(dict(kind='DOS48',paragraphs=paragraphs,success=success,segment_or_error=segment))
   if not success:return self.result
   if segment<=self.dg(0x20f8):continue
   if segment>self.dg(0x20f6):self.put(self.ds*16+0x20f6,segment)
   b=segment*16;tag=self.dg(0x2342);self.put(b+2,tag);self.put(b+4,size);tail=(size-2)&65535;self.put(b+tail,0xfffe);self.put(b+10,tail);self.put(b+20,size-23);self.put(b,segment)
   for o,v in ((6,20),(8,20),(12,0),(14,0),(16,0),(18,0)):self.put(b+o,v)
   if not head:self.put(root+2,segment);self.put(root,0)
   else:
    last=self.far(root+8)[1];self.put(last*16+14,segment);self.put(last*16+12,0);self.put(b+18,last);self.put(b+16,0)
   self.put(root+10,segment);self.put(root+8,0);self.put(root+6,segment);self.put(root+4,0)
   p=self.scan(segment,wanted);assert p is not None;self.put(root+6,segment);self.put(root+4,0);self.result=(p,segment);return self.result
  assert os_replies,'fixture exhaustion before DOS response'
  return self.result
