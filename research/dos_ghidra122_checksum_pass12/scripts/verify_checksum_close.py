from pathlib import Path
import csv,json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent
out=root/'pass12/evidence';out.mkdir(parents=True,exist_ok=True)
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
 fread_raw=bytes.fromhex(calls[2]['bytes']); crt_cs=struct.unpack_from('<H',fread_raw,3)[0]; fread_ip=struct.unpack_from('<H',fread_raw,1)[0]
 fread_body=[r for r in rows if r['address'].startswith(f'{crt_cs:04x}:') and fread_ip<=int(r['address'].split(':')[1],16)<fread_ip+0xe3]
 fread_code=b''.join(bytes.fromhex(r['bytes']) for r in fread_body)
 sub=next(bytes.fromhex(r['bytes']) for r in fread_body if r['bytes'].startswith('2d')); native_stream=struct.unpack_from('<H',sub,1)[0]
 di=next(bytes.fromhex(r['bytes']) for r in fread_body if r['bytes'].startswith('bf')); extra=struct.unpack_from('<H',di,1)[0]
 nc=[r for r in fread_body if r['bytes'].startswith('e8')]; nr=nc[1]; nip=int(nr['address'].split(':')[1],16); lowread=(nip+3+struct.unpack('<h',bytes.fromhex(nr['bytes'])[1:])[0])&65535
 lowrows=[r for r in rows if r['address'].startswith(f'{crt_cs:04x}:') and lowread<=int(r['address'].split(':')[1],16)<lowread+0x30]
 cmp=next(bytes.fromhex(r['bytes']) for r in lowrows if r['bytes'].startswith('3b1e')); maxhandle=struct.unpack_from('<H',cmp,2)[0]
 def target(r):
  bb=bytes.fromhex(r['bytes']);return struct.unpack_from('<H',bb,1)[0],struct.unpack_from('<H',bb,3)[0]
 def section(seg,ip,n):return [r for r in rows if r['address'].startswith(f'{seg:04x}:') and ip<=int(r['address'].split(':')[1],16)<ip+n]
 fopen_ip,_=target(calls[0]);fc=[r for r in section(crt_cs,fopen_ip,0x15) if r['bytes'].startswith('9a')];openwrap,_=target(fc[0]);wc=[r for r in section(crt_cs,openwrap,0x2c) if r['bytes'].startswith('9a')];freeip,_=target(wc[0]);parseip,_=target(wc[1]);pc=[r for r in section(crt_cs,parseip,0x130) if r['bytes'].startswith('9a')];assert len(pc)==1
 lowopen_site=crt_cs*16+int(pc[0]['address'].split(':')[1],16)
 fr=section(crt_cs,freeip,0x60);limitrow=next(r for r in fr if r['bytes'].startswith('3936') or r['bytes'].startswith('3b06'));streamlimit=struct.unpack_from('<H',bytes.fromhex(limitrow['bytes']),2)[0]
 # Locate the first buffer allocator sequence; assert its effect in every read case.
 image=bytes(p);seq=bytes.fromhex('b80002509a');begin=crt_cs*16-0x10000;matches=[i for i in range(begin,begin+0x1200) if image[i:i+5]==seq];assert len(matches)>0
 allocsite=0x10000+matches[0]+4
 closeip,_=target(calls[-1]);cr=section(crt_cs,closeip,0x60);nearclose=[r for r in cr if r['bytes'].startswith('e8')];r=nearclose[1];siteip=int(r['address'].split(':')[1],16);cleanup=(siteip+3+struct.unpack('<h',bytes.fromhex(r['bytes'])[1:])[0])&65535
 freecall=next(r for r in section(crt_cs,cleanup,0x2c) if r['bytes'].startswith('9a'));freesite=crt_cs*16+int(freecall['address'].split(':')[1],16)
 kinds=['open','open_error','read','read','checksum_error','close'];sites={base+int(r['address'].split(':')[1],16):kind for r,kind in zip(calls,kinds)}
 locations.append(dict(build=v,crt_fopen=f'{crt_cs:04x}:{fopen_ip:04x}',crt_open_wrapper=f'{crt_cs:04x}:{openwrap:04x}',crt_free_stream=f'{crt_cs:04x}:{freeip:04x}',crt_mode_parser=f'{crt_cs:04x}:{parseip:04x}',lowopen_callsite=f'{crt_cs:04x}:{lowopen_site-crt_cs*16:04x}',allocator_callsite=f'{crt_cs:04x}:{allocsite-crt_cs*16:04x}',stream_limit_address=hex(streamlimit),crt_fread=f'{crt_cs:04x}:{fread_ip:04x}',crt_lowread=f'{crt_cs:04x}:{lowread:04x}',stream_table=hex(native_stream),extra_table=hex(extra),maxhandle_address=hex(maxhandle),entry=f'{cs:04x}:{entry:04x}',exe_sha256=hashlib.sha256(b).hexdigest(),instructions=body))
 for alloc_fail in [False,True]:
  for data,fault in [(x,False) for x in [b'',b'\x00',b'\x01',b'\xff',b'\x12\x34',bytes(range(53)),b'A\r\nB\x1aC']]+[(b'\x01',True)]:
   for limit in [0,len(data)+2,0xffffffff]:
    for seed in [0,0xa5]:
     u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));ds=q['actual_DS'];sp=0xe000;stream=native_stream
     u.mem_write(ds*16+sp,struct.pack('<HHHIH',0x600,0,0x9100,limit,0));u.mem_write(ds*16+sp-12,bytes([seed]))
     for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
     u.mem_write(ds*16+stream,bytes(8));u.mem_write(ds*16+extra,bytes(8));u.mem_write(ds*16+streamlimit,struct.pack('<H',stream));u.mem_write(ds*16+maxhandle,struct.pack('<H',20));u.mem_write(ds*16+maxhandle+2+5,b'\x00')
     state=dict(freed_buffers=[],dos_calls=[],mode=None,open_flags=None,allocation_calls=0,crt_callee_hits={},reads=0,dos_reads=0,file_position=0,fold=None,closed=False,error=False);fold=0x7b
     count=len(data)+1 if limit==0 else (0 if limit&0x80000000 else limit)
     last=seed
     if fault and limit!=0:
      fold=0x7b^(seed if count%2 else 0)
      count=0
     for i in range(count):
      if i<len(data):last=data[i]
      fold^=last
     if fault and limit!=0:count=0 if limit&0x80000000 else limit
     u.mem_write(ds*16+sp+10,struct.pack('<H',fold))
     def hook(uc,a,n,_):
      for nr in nc:
       ip=int(nr['address'].split(':')[1],16);target=(ip+3+struct.unpack('<h',bytes.fromhex(nr['bytes'])[1:])[0])&65535
       if a==crt_cs*16+target:
        key=f'{crt_cs:04x}:{target:04x}';state['crt_callee_hits'][key]=state['crt_callee_hits'].get(key,0)+1
      if a==lowopen_site:
       stack=ds*16+uc.reg_read(UC_X86_REG_SP);filename,flags,share,perms=struct.unpack('<4H',uc.mem_read(stack,8));state['open_flags']=flags;assert flags==0x8000
       return # Execute original low-level open and handle-flag construction.
      if a==freesite:
       stack=ds*16+uc.reg_read(UC_X86_REG_SP);ptr=struct.unpack('<H',uc.mem_read(stack,2))[0];assert ptr==0x9400;state['freed_buffers'].append(ptr);uc.reg_write(UC_X86_REG_IP,a-crt_cs*16+5);return
      if a==allocsite:
       stack=ds*16+uc.reg_read(UC_X86_REG_SP);assert struct.unpack('<H',uc.mem_read(stack,2))[0]==512;state['allocation_calls']+=1
       uc.reg_write(UC_X86_REG_AX,0 if alloc_fail else 0x9400);uc.reg_write(UC_X86_REG_IP,a-crt_cs*16+5);return
      if a not in sites:return
      kind=sites[a];stack=ds*16+uc.reg_read(UC_X86_REG_SP)
      if kind=='open':
       filename,mode=struct.unpack('<HH',uc.mem_read(stack,4));state['mode']=bytes(uc.mem_read(ds*16+mode,8)).split(b'\0')[0].decode('ascii');assert state['mode']=='rb';return
      elif kind=='read':
       dst,size,num,handle=struct.unpack('<4H',uc.mem_read(stack,8));assert (size,num,handle)==(1,1,stream)
       state['reads']+=1
       return # Execute original fread, refill, memcpy and low-level CRT read.
      elif kind=='close':state['buffer_capacity']=struct.unpack('<H',uc.mem_read(ds*16+extra+2,2))[0];state['closed']=True;state['fold']=uc.mem_read(ds*16+sp-11,1)[0];return # Execute original fclose and cleanup.
      else:state['error']=True;uc.emu_stop();return
      uc.reg_write(UC_X86_REG_IP,a-base+5)
     def intr(uc,num,_):
      assert num==0x21
      ax=uc.reg_read(UC_X86_REG_AX);state['dos_calls'].append(hex(ax))
      if (ax>>8)==0x3d:
       assert ax==0x3d00 and uc.reg_read(UC_X86_REG_DX)==0x9100;uc.reg_write(UC_X86_REG_AX,5);uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~1);return
      if ax==0x4400:
       assert uc.reg_read(UC_X86_REG_BX)==5;uc.reg_write(UC_X86_REG_DX,0);uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~1);return
      if ax>>8==0x3e:
       assert uc.reg_read(UC_X86_REG_BX)==5;uc.reg_write(UC_X86_REG_AX,0);uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~1);return
      if ax==0x4300:
       assert uc.reg_read(UC_X86_REG_DX)==0x9100;uc.reg_write(UC_X86_REG_CX,0);uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~1);return
      assert (ax>>8)==0x3f,(v,num,hex(ax))
      assert uc.mem_read(ds*16+maxhandle+2+5,1)[0]==1

      assert uc.reg_read(UC_X86_REG_BX)==5
      count=uc.reg_read(UC_X86_REG_CX);dst=uc.reg_read(UC_X86_REG_DS)*16+uc.reg_read(UC_X86_REG_DX);pos=state['file_position'];chunk=data[pos:pos+count]
      if fault:
       state['dos_reads']+=1;uc.reg_write(UC_X86_REG_AX,5);uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)|1);return
      if chunk:uc.mem_write(dst,chunk)
      state['dos_reads']+=1;state['file_position']+=len(chunk);uc.reg_write(UC_X86_REG_AX,len(chunk));uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~1)
     u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_CODE,hook);u.emu_start(base+entry,0x600,count=100000)
     if fault and limit==0:
      flags=u.mem_read(ds*16+stream+6,1)[0];assert flags&0x20 and not flags&0x10 and state['dos_reads']>100 and not state['closed'] and not state['error']
      results.append(dict(build=v,allocator_failure=alloc_fail,dos_read_error=True,limit=0,initial_local_byte=seed,instruction_budget=100000,stream_flags=flags,outcome='budget exhausted in repeated read-error loop',**state,passed=True));continue
     assert u.mem_read(ds*16+stream+6,1)[0]==0 and u.mem_read(ds*16+maxhandle+7,1)[0]==0
     assert state['freed_buffers']==([0x9400] if count and not alloc_fail else [])
     assert state['buffer_capacity']==(0 if count==0 else (1 if alloc_fail else 512)),state
     assert state['allocation_calls']==(0 if count==0 else 1),state
     assert state['reads']==count and state['fold']==fold and state['closed'] and not state['error'],(v,data,limit,seed,state,fold)
     assert u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_CS)==0
     results.append(dict(build=v,allocator_failure=alloc_fail,data_hex=data.hex(),dos_read_error=fault,limit=limit,initial_local_byte=seed,**state,passed=True))
(out/'checksum_close_emulation.json').write_text(json.dumps(dict(scope='Original validator + fread + refill + memcpy + low-level CRT read. Original fopen and buffer initialization. Original low-level open executed; allocator/free mocked; original fclose/cleanup executed; DOS INT21 open/IOCTL/attributes/read mocked. Allocation success/failure exercised. No DOSBox/full game.',cases=len(results),results=results),indent=2))
(out/'checksum_close_locations.json').write_text(json.dumps(locations,indent=2))
print(len(results),'passed')
