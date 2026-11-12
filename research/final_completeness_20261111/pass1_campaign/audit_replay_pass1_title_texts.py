"""python audit_replay_pass1_title_texts.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);instructions=[]
for i in Decoder(16,b[0x83d8:0x84fd],ip=8):
    assert not i.is_invalid;raw=b[0x83d0+i.ip:0x83d0+i.next_ip];assert lookup[(0x83d,i.ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0x83d,ip=i.ip,image_offset=0x83d0+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
assert instructions[-1]['ip']==0x12c
fields=[]
for off,name in [(0x139e,'title_name'),(0x13aa,'title_version'),(0x13af,'title_distributed_by'),(0x13be,'title_registered'),(0x13d2,'title_shareware'),(0x13e4,'title_copyright')]:
    a=0x27710+off;e=b.index(0,a)+1;assert all(32<=c<127 for c in b[a:e-1])
    fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type='NUL_ASCII_title_text',status='PARTIAL',range_sha256=sha(b[a:e])))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];draws=[]
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0x83d;ds=load+0x2771
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    targets={load*16+0x28f8:'resource',load*16+0x1f9a:'background',load*16+0xd3fa:'selection',load*16+0xd3a6:'draw',load*16+0xad9a:'query'}
    for a in targets:u.mem_write(a,b'\xcb')
    state={}
    def hook(uc,a,size,data):
        if a not in targets:return
        name=targets[a];sp=uc.reg_read(UC_X86_REG_SP);args=struct.unpack('<6H',uc.mem_read(0x50000+sp+4,12));state['calls'].append(name)
        if name=='resource':uc.reg_write(UC_X86_REG_AX,0x100+args[0])
        elif name=='selection':state['selections'].append(args[0])
        elif name=='query':
            state['queries'].append(args[0]);assert args[0] in (1,2)
            uc.reg_write(UC_X86_REG_AX,0x9000 if args[0]==2 else state['registered']);uc.reg_write(UC_X86_REG_DX,ds if args[0]==2 else 0)
        elif name=='draw':
            x,y,off,seg,value,style=args;assert x==65535 and seg==ds and style==1
            raw=bytes(uc.mem_read(seg*16+off,128));text=raw[:raw.index(0)].decode('ascii')
            state['draws'].append((y,off,text));draws.append(dict(load_segment=load,predicate_nonzero=state['registered'],y_word=y,text_offset=off,text_segment=seg,resource_value=value,style_word=style,text=text))
    u.hook_add(UC_HOOK_CODE,hook);u.mem_write(ds*16+0x9000,b'SEEDED DISTRIBUTOR\0')
    for registered in (0,1):
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x5ff00,struct.pack('<HH',0x4000,cs));state.clear();state.update(registered=registered,calls=[],draws=[],queries=[],selections=[])
        u.emu_start(cs*16+8,cs*16+0x4000,count=1000)
        expected=[(40,0x139e),(60,0x13aa),(100,0x13af),(115,0x9000),(140,0x13be if registered else 0x13d2),(160,0x13e4)]
        assert [(y,off) for y,off,text in state['draws']]==expected and state['queries']==[2,1] and state['selections']==[2,1,0]
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_DS)==ds
        cases.append(dict(load_segment=load,predicate_nonzero=registered,draw_count=len(state['draws']),queries='2 1',selections='2 1 0',passed=True))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('instructions',instructions),('data_fields',fields),('cases',cases),('draw_arguments',draws)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),function_start=0x83d8,function_end_exclusive=0x84fd,instruction_bytes=293,instructions=len(instructions),typed_bytes=sum(r['length'] for r in fields),cases=len(cases),failures=0,scope='original title wrapper; five dependencies mocked; query 1 seeded zero/nonzero; query 2 seeded FAR text',natural_query_semantics_closed=False,renderer_behavior_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
