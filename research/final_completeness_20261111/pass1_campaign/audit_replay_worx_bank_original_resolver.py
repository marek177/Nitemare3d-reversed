"""IMAGE RELOCS EMULATOR OUT: original WORX bank loader with original ES:DI normalizer; no substituted resolver."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,relocs,emulator,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(emulator.resolve()))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_INTR
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);root=out.parent;sources=[root/'worx_register_bank_replay/worx_bank_load_128x11.csv',root/'worx_leafs/normalize_es_di.csv'];allowed=set()
for source in sources:
 for row in csv.DictReader(source.open()):
  p=int(row['image_offset']);raw=bytes.fromhex(row['bytes']);assert b[p:p+len(raw)]==raw;allowed.add(p)
rel=list(csv.DictReader(relocs.open()));cases=[]
for load,seg,off,df,good_signature in itertools.product((0x824,0x1000),(0x5000,0x6000),(0,1,15,16,0xfff0,0xffff),(0,1),(False,True)):
 raw=bytearray(b)
 for x in rel:struct.pack_into('<H',raw,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 cs=load+0x15bf;ss=0x9000;stack=0xf000;lo,hi=ss*16+stack-64,ss*16+stack+8;ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;source_pointer=seg*16+off;payload=bytearray((j*73+load+df)&255 for j in range(3204));payload[:4]=b'IBK\x1a' if good_signature else b'XXXX';ram[source_pointer:source_pointer+len(payload)]=payload;frame=struct.pack('<H',0x6000);ram[ss*16+stack:ss*16+stack+2]=frame;expected=bytearray(ram);dst=cs*16+0x2513;projection=b''.join(payload[4+16*j:4+16*j+11] for j in range(128));expected[dst:dst+1408]=projection
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));done=[];writes=[];steps=[]
 for reg,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,cs),(UC_X86_REG_SS,ss),(UC_X86_REG_ES,seg),(UC_X86_REG_DI,off),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_AX,0x2345),(UC_X86_REG_DX,0x3456),(UC_X86_REG_EFLAGS,2|(df<<10))]:u.reg_write(reg,value)
 def code(e,p,n,d):
  if p==cs*16+0x6000:done.append(True);e.emu_stop();return
  assert p-load*16 in allowed;steps.append(p-load*16)
 def write(e,access,p,n,v,d):
  if not(lo<=p and p+n<=hi):writes.append((p,n,v))
 def intr(e,n,d):raise AssertionError('no external API or resolver fixture')
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+0x5973,0x1fffff,count=20000);assert done and writes==[(dst+j,1,x) for j,x in enumerate(projection)];actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo]==expected[:lo] and actual[hi:]==expected[hi:]
 for reg,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,cs),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,stack+2),(UC_X86_REG_BP,0x1234),(UC_X86_REG_AX,0),(UC_X86_REG_DX,0x3456),(UC_X86_REG_BX,128),(UC_X86_REG_CX,0),(UC_X86_REG_SI,0x2a93),(UC_X86_REG_ES,seg+(off>>4)),(UC_X86_REG_DI,(off&15)+4+2048)]:assert u.reg_read(reg)==value
 assert bytes(u.mem_read(ss*16+stack,2))==frame and bool(u.reg_read(UC_X86_REG_EFLAGS)&0x400)==bool(df)
 cases.append(dict(case=len(cases),load=load,source_segment=seg,source_offset=off,input_DF=df,IBK_prefix=good_signature,source_header_validated_by_loader=False,original_instructions=len(steps),byte_stores=len(writes),whole_RAM_bytes_checked=len(ram)-(hi-lo),status='PASS'))
with (out/'cases.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(cases[0]));w.writeheader();w.writerows(cases)
s=dict(functions=[],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='Wholeoriginal5973bankloader+4630normalizer,noresolver/APIstub.96cases real-modeoffsetnormalization,DF0/1,good/bad4Bprefix,two loads.1408orderedBYTEstores/full2MiBRAMexcept72controlstackB/frames/registers checked. DS=CS;invalidaliases/unmappedsource/ES0rollover notclaimed. Prefix is skipped,not validated.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in [image,relocs,Path(__file__)]+sources]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
