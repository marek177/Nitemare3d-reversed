"""VERSION_ROOT VERSION_CSV DECODER EMULATOR GAME OUT: original kind44 helper acrossversions,local cache scenarios; no callee fixtures,not wholeepisode transition."""
import csv,hashlib,json,struct,sys
from pathlib import Path
root,versiondir,decoder,emulator,game,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Register,Mnemonic,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
vr=list(csv.DictReader((versiondir/'versions.csv').open()));ins=list(csv.DictReader((versiondir/'instructions.csv').open()));out.mkdir(exist_ok=True);sha=lambda x:hashlib.sha256(x).hexdigest();map1=(game/'MAP.1').read_bytes();map2=(game/'MAP.2').read_bytes();cases=[];files=[];bindings=[]
for v in ('10','11','12','15','17','18','19','20'):
 image=root/('N3D-'+v)/'unpacked_image.bin';b=image.read_bytes();f=next(x for x in vr if x['version']==v and x['function']=='terrain_kind44_variant');r=[x for x in ins if x['version']==v and x['function'] in ('terrain_kind44_variant','terrain_kind_search')];allow=set();decoded=[]
 for x in r:
  p=int(x['image_offset']);raw=bytes.fromhex(x['bytes']);assert b[p:p+len(raw)]==raw;allow.add(p);i=Decoder(16,raw,ip=int(x['ip'])).decode();decoded.append((x,i))
 entry=int(f['start']);cs=int(next(x for x in r if int(x['image_offset'])==entry)['cs']);ip=entry-cs*16;mode='episode_WORD' if b[entry+4]==0xa1 else 'zero_BYTE';assert mode=='episode_WORD' or b[entry+4:entry+6]==bytes.fromhex('803e')
 basecache=next(i.memory_displacement for x,i in decoded if x['function']=='terrain_kind44_variant' and bytes.fromhex(x['bytes'])[0]==0xa2);classbase=next(i.memory_displacement for x,i in decoded if x['function']=='terrain_kind44_variant' and i.mnemonic==Mnemonic.CMP and i.memory_base==Register.BX);search=int(next(x['start'] for x in vr if x['version']==v and x['function']=='terrain_kind_search'));episodenum=episodecache=None
 if mode=='episode_WORD':
  seq=[i for x,i in decoded if x['function']=='terrain_kind44_variant'];episodenum=seq[1].memory_displacement;episodecache=seq[2].memory_displacement
 bindings.append(dict(version=v,mode=mode,cache_BYTE=basecache,class_table=classbase,current_episode_WORD=episodenum,cached_episode_WORD=episodecache))
 for split in (False,True):
  for scenario in ('cold','retained_cross_episode','same_episode_changed_header','zero_kind_base_repeat'):
   ds=0x5000;ss=0x6000 if split else ds;db=ds*16;sp=0xf000;sl,sh=ss*16+sp-64,ss*16+sp+16;ram=bytearray(b'\xa5'*0x200000);ram[:len(b)]=b;values=bytearray(map1[2:258] if scenario=='cold' else map2[2:258]);initial=0 if scenario in ('cold','zero_kind_base_repeat') else 186;ep=2 if scenario=='retained_cross_episode' else 1;cached=0xffff if scenario in ('cold','zero_kind_base_repeat') else 1;celltype=186 if scenario=='cold' else 192
   if scenario=='zero_kind_base_repeat':values=bytearray(256);values[0]=68;celltype=0
   ram[db+classbase:db+classbase+256]=values;ram[db+basecache]=initial
   if mode=='episode_WORD':struct.pack_into('<H',ram,db+episodenum,ep);struct.pack_into('<H',ram,db+episodecache,cached)
   ram[0x70100]=celltype;frame=struct.pack('<4H',0x200,0x4e00,0x100,0x7000);ram[ss*16+sp:ss*16+sp+8]=frame;expected=bytearray(ram);want=[];searches=0;repeat=2 if scenario=='zero_kind_base_repeat' else 1;base=initial
   for j in range(repeat):
    refresh=base==0 if mode=='zero_BYTE' else cached!=ep
    if refresh:
     if mode=='episode_WORD':cached=ep;struct.pack_into('<H',expected,db+episodecache,ep);want.append((db+episodecache,2,ep))
     base=next(k for k,x in enumerate(values) if x==68);searches+=1;expected[db+basecache]=base;want.append((db+basecache,1,base))
   result=(celltype-base)&65535;u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));writes=[];seen=[];done=[]
   def code(e,a,n,data):
    if a==0x4e200:done.append(True);e.emu_stop();return
    assert a in allow,hex(a)
    if a==search:seen.append(True)
   def write(e,access,a,n,value,data):
    if not(sl<=a and a+n<=sh):writes.append((a,n,value&((1<<(8*n))-1)))
   u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
   for j in range(repeat):
    u.mem_write(ss*16+sp,frame)
    for reg,z in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,z)
    u.emu_start(entry,0x1fffff,count=6000);assert done and u.reg_read(UC_X86_REG_AX)==result
    for reg,z in ((UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)):assert u.reg_read(reg)==z
   assert writes==want and len(seen)==searches,(v,scenario,writes,want,len(seen),searches);actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:]
   cases.append(dict(version=v,split_SS_DS=split,scenario=scenario,mode=mode,repeats=repeat,initial_cache=initial,final_cache=base,return_AX=result,original_search_calls=len(seen),original_nonstack_stores=len(writes),status='PASS'))
 files.append(dict(path=str(image.resolve()),sha256=sha(b)))
def save(n,rows):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('cases',cases);save('cache_bindings',bindings);s=dict(cases_separate=len(cases),failures=0,versions=8,runtime_tests=0,new_deep_verified_bytes=0,scope='Whole original per-version helper+search under local retained-cache/header/episode scenarios,no fixtures. RealMAP1/2headers as testdata,not wholehistoricalasset/episode transition parity;other caller cache invalidation open. Full2MiB except80controlstackB.',files=files+[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (versiondir/'versions.csv',versiondir/'instructions.csv',game/'MAP.1',game/'MAP.2',Path(__file__))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'}))
