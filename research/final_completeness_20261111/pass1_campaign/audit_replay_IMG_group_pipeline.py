"""python audit_replay_IMG_group_pipeline.py IMAGE INVENTORY DECODER EMULATOR GAME_DIR GROUP_CSV OUT
Original0584/045C/03CA/cachetag/XMSappend/wrapper over every actual resource group.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,game,group_csv,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);assets={n:(game/('IMG.'+str(n))).read_bytes() for n in (1,2,3)};groups=list(csv.DictReader(group_csv.open(encoding='utf-8-sig')));rel=list(csv.DictReader((image.parent/'relocations.csv').open()));runtimes={};cases=[]
for load in (0x824,0x1000):
 r=bytearray(b)
 for x in rel:struct.pack_into('<H',r,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 runtimes[load]=bytes(r)
for load in (0x824,0x1000):
 for mode in ('file_index','cache_all','cache_no_capacity'):
  for group in groups:
   ep=int(group['episode']);wall=group['kind']=='wall';code=int(group['codes'].split(';')[0]);count=int(group['image_count']);payload=int(group['start']);blob=assets[ep];descriptor_off=0x800+90*(code+(0 if wall else 256));header90=blob[descriptor_off:descriptor_off+90];assert header90[2]==count
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,runtimes[load]);ds=load+0x2771;record=0x9000;header=0x7000;handle=7;src_off,src_seg=0x1000,0x6000;far=src_off|src_seg<<16;manager=0x80100;request_seg=load+0x1be7;request_ptr=request_seg*16+0x200;dg=bytearray(0xe030);dg[0x3cce]=mode!='file_index';struct.pack_into('<HHH',dg,0x3506,1,0 if mode=='cache_no_capacity' else 65535,0);struct.pack_into('<HH',dg,0x350e,0x100,0x8000);struct.pack_into('<H',dg,0x2560,request_seg);expected=bytearray(dg);expected[header:header+90]=header90
   cursor=payload;chunks_total=0;expected_pixels=[];expected_moves=[]
   for n in range(count):
    raw10=blob[cursor:cursor+10];w,h=raw10[:2];area=w*h;pos=cursor+10;pixels=blob[pos:pos+area];assert len(pixels)==area;rec=bytearray(raw10);cached=mode=='cache_all';offset=chunks_total*1024
    struct.pack_into('<I',rec,2,(-offset)&0xffffffff if cached else pos);struct.pack_into('<I',rec,6,0);expected[record+10*n:record+10*(n+1)]=rec;expected_pixels.append(pixels)
    if cached:expected_moves.append(struct.pack('<IHIHI',((area+1023)//1024)*1024,0,far,1,offset));chunks_total+=(area+1023)//1024
    cursor=pos+area
   assert cursor==int(group['end_exclusive']);struct.pack_into('<H',expected,0x350a,chunks_total);stat=(0xe010 if wall else 0xe01c) if mode=='cache_all' else (0xe00e if wall else 0xe01a);struct.pack_into('<H',expected,stat,count)
   u.mem_write(ds*16,bytes(dg));u.mem_write(src_seg*16+src_off,b'\xaa'*65536);u.mem_write(request_ptr,b'\x5a'*16);u.mem_write(manager,b'\xcb');frame=struct.pack('<9H',0x100,0x5000,handle,payload&65535,payload>>16,code,8,header,int(wall));u.mem_write(ds*16+0xf000,frame)
   for q,value in [(UC_X86_REG_CS,load+0x277),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(q,value)
   state=dict(cursor=0,far_reads=0,frees=0,moves=0);done=[]
   targets={(load+0x11ee)*16+0x1bd6:'seek',(load+0x11ee)*16+0x1e14:'near_read',(load+0x11ee)*16+0x2898:'tell',(load+0x11ee)*16+0x3ccf:'near_allocate',(load+0x11ee)*16+0x2065:'far_allocate',(load+0x11ee)*16+0x2052:'far_free',(load+0xfba)*16+0x9e:'far_read',(load+0xfba)*16+0xc:'error',manager:'manager'}
   def hook(emu,address,size,data):
    if address==0x50100:done.append(True);emu.emu_stop();return
    if address not in targets:return
    name=targets[address];assert name!='error',(ep,code,wall,mode);sp=emu.reg_read(UC_X86_REG_SP)
    def args(n):return struct.unpack('<'+'H'*n,bytes(emu.mem_read(ds*16+sp+4,2*n)))
    if name=='manager':
     n=state['moves'];assert mode=='cache_all' and bytes(emu.mem_read(request_ptr,16))==expected_moves[n];assert bytes(emu.mem_read(src_seg*16+src_off,len(expected_pixels[n])))==expected_pixels[n];state['moves']+=1;emu.reg_write(UC_X86_REG_AX,1);emu.reg_write(UC_X86_REG_BL,0);return
    if name=='seek':
     h,lo,hi,whence=args(4);assert h==handle and whence in (0,1);offset=lo|hi<<16;offset=offset if offset<0x80000000 else offset-0x100000000;state['cursor']=offset+(state['cursor'] if whence else 0);assert 0<=state['cursor']<=len(blob);emu.reg_write(UC_X86_REG_AX,state['cursor']&65535);emu.reg_write(UC_X86_REG_DX,state['cursor']>>16)
    elif name=='near_read':
     h,dest,n=args(3);assert h==handle and n in (10,90);data=blob[state['cursor']:state['cursor']+n];assert len(data)==n;emu.mem_write(ds*16+dest,data);state['cursor']+=n;emu.reg_write(UC_X86_REG_AX,n)
    elif name=='tell':assert args(1)==(handle,);emu.reg_write(UC_X86_REG_AX,state['cursor']&65535);emu.reg_write(UC_X86_REG_DX,state['cursor']>>16)
    elif name=='near_allocate':assert args(1)==(count*10,);emu.reg_write(UC_X86_REG_AX,record)
    elif name=='far_allocate':assert args(1)==(len(expected_pixels[state['far_reads']]),);emu.reg_write(UC_X86_REG_AX,src_off);emu.reg_write(UC_X86_REG_DX,src_seg)
    elif name=='far_free':assert args(2)==(src_off,src_seg);state['frees']+=1
    else:
     h,off,seg,n=args(4);assert (h,off,seg)==(handle,src_off,src_seg);data=blob[state['cursor']:state['cursor']+n];assert data==expected_pixels[state['far_reads']];emu.mem_write(seg*16+off,data);state['cursor']+=n;state['far_reads']+=1;emu.reg_write(UC_X86_REG_AX,n)
    ret,rcs=struct.unpack('<HH',bytes(emu.mem_read(ds*16+sp,4)));emu.reg_write(UC_X86_REG_SP,sp+4);emu.reg_write(UC_X86_REG_CS,rcs);emu.reg_write(UC_X86_REG_IP,ret)
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+0x277)*16+0x584,0xfffff,count=30000);assert done
   assert bytes(u.mem_read(ds*16,len(dg)))==expected and state['cursor']==cursor
   assert state['far_reads']==state['frees']==(0 if mode=='file_index' else count) and state['moves']==(count if mode=='cache_all' else 0)
   assert u.reg_read(UC_X86_REG_AX)==record and u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_DS)==u.reg_read(UC_X86_REG_SS)==ds
   cases.append(dict(load=load,mode=mode,episode=ep,kind=group['kind'],code=code,count=count,group_start=payload,group_end=cursor,XMS_KiB=chunks_total,manager_calls=state['moves'],decoded_records_sha256=sha(bytes(expected[record:record+10*count])),status='PASS'))
with (out/'cases.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(cases[0]));w.writeheader();w.writerows(cases)
inputs=[image,inventory,image.parent/'relocations.csv',group_csv,Path(__file__)]+[game/('IMG.'+str(ep)) for ep in (1,2,3)]
s=dict(functions=[],cases=len(cases),groups_per_mode=len(groups),records_per_mode=sum(int(g['image_count']) for g in groups),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='all supplied actualgroups/records per load/mode; original0584/045C/03CA/cachetag/XMSappend/wrapper; only externalIO/heap/XMSmanager fixtures; fullDGROUP/metadata/positions/counters/logicalpixelprefix matched; no physicalXMS/readback/render layout/malformed-domain completeness',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in inputs])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
