"""Independent16/32-bit arithmetic and segmented zero-fill model, not a DOS heap implementation."""
import struct
class LargeAllocationModel:
 def __init__(self,ram,ds,count,size,os_replies,callback_actions):
  self.ram=bytearray(ram);self.ds=ds;self.count=count;self.size=size;self.os_replies=list(os_replies);self.callback_actions=list(callback_actions);self.calls=[];self.operations=[];self.result=(0,0);self.df_cleared=False
 def word(self,o):return struct.unpack_from('<H',self.ram,self.ds*16+o)[0]
 def put(self,a,size,value):self.ram[a:a+size]=value.to_bytes(size,'little');self.operations.append(('store',a,size,value))
 @staticmethod
 def layout(count,size):
  p=(count*size)&0xffffffff;lo=p&65535;hi=p>>16;align=0
  if not p or p>0xffff0:return None
  mask=(size-1)&size
  if p>0x20000 and mask:return None
  if hi>=1 and not(p>0x20000) and mask:
   align=(hi*65536)%size
   if lo+align>65535:return None
   p=65536+lo+align
  return ((p+15)//16,align,p)
 def zero(self,segment,paragraphs):
  end=(segment+paragraphs-1)&65535
  if end>self.word(0x20f6):self.put(self.ds*16+0x20f6,2,end)
  es=segment;left=paragraphs
  while left>0:
   n=min(left,0x1000);address=es*16;size=n*16;self.ram[address:address+size]=b'\0'*size;self.operations.append(('zero_words',address,size,0));left-=0x1000;es=(es+0x1000)&65535
  self.df_cleared=True
 def run(self):
  for attempt in range(20):
   layout=self.layout(self.count,self.size)
   if layout:
    paragraphs,alignment,adjusted=layout
    while True:
     success,segment=self.os_replies.pop(0) if self.os_replies else (False,8);self.calls.append(dict(kind='DOS48',paragraphs=paragraphs,success=success,segment_or_error=segment))
     if not success:break
     if segment<=self.word(0x20f8):continue
     self.zero(segment,paragraphs);self.result=(alignment,segment);return
   if not self.word(0x246a) and not self.word(0x246c):return
   action=self.callback_actions.pop(0);self.calls.append(dict(kind='callback',size=self.size,count=self.count,return_AX=action['AX'],new_count=action.get('count',self.count),new_size=action.get('size',self.size)))
   if not action['AX']:return
   self.count=action.get('count',self.count);self.size=action.get('size',self.size)
  raise AssertionError('unbounded fixture retry')
 def expected_writes(self):
  for kind,address,size,value in self.operations:
   if kind=='store':yield address,size,value
   else:
    for p in range(address,address+size,2):yield p,2,0
