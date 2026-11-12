"""python audit_replay_secondary_class_search.py IMAGE INVENTORY DECODER EMULATOR MAP_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,mapdir,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
todo=[0x4e];decoded={};edges=[]
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0x4e<=ip<0x83;i=Decoder(16,b[0xf70+ip:0xff3],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0xf70+ip:0xf70+i.next_ip];assert lookup[(0xf7,ip)]['bytes']==raw.hex();rows.append(dict(cs=0xf7,ip=ip,image_offset=0xf70+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('secondary_class_suffix_search',rows);save('cfg_edges',edges)
assets=[];tables={};domains=[]
for ep in (1,2,3):
    p=mapdir/('MAP.%d'%ep);raw=p.read_bytes();assert len(raw)>=514;table=raw[258:514];tables[ep]=table
    assets.append(dict(episode=ep,path=str(p.resolve()),bytes=len(raw),sha256=sha(raw),secondary_sha256=sha(table)))
    for key in sorted(set(table)):
        ids=[i for i,v in enumerate(table) if v==key];domains.append(dict(episode=ep,secondary_class=key,first=ids[0],last=ids[-1],count=len(ids),contiguous=ids==list(range(ids[0],ids[-1]+1)),maximum_relative_id=ids[-1]-ids[0],relative_ids=';'.join(str(i-ids[0]) for i in ids)))
save('assets',assets);save('class_domains',domains)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];state={};visited=set()
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);ds=load+0x2771;cs=load+0xf7
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    error=load*16+0xfbac;u.mem_write(error,b'\xcb')
    def hook(uc,a,size,data):
        if cs*16+0x4e<=a<cs*16+0x83:visited.add(a-cs*16)
        if a==error:
            sp=uc.reg_read(UC_X86_REG_SP);assert struct.unpack('<HH',uc.mem_read(0x50000+sp+4,4))==(0xf2,state['key']);state['errors']+=1;uc.reg_write(UC_X86_REG_AX,0xbeef)
    u.hook_add(UC_HOOK_CODE,hook)
    for ep,table in tables.items():
        u.mem_write(ds*16+0xd40e,table)
        for key in list(range(256))+[0x100,0xffff]:
            for start in (0,1,127,255,256,511,65535):
                match=next((i for i in range(start&255,256) if table[i]==key),None);expected=0xbeef if match is None else match
                state.clear();state.update(key=key,errors=0)
                for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x3333),(UC_X86_REG_SS,0x5000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
                u.mem_write(0x5ff00,struct.pack('<HHHH',0x6000,cs,key,start));u.emu_start(cs*16+0x4e,cs*16+0x6000,count=5000)
                assert u.reg_read(UC_X86_REG_AX)==expected and state['errors']==int(match is None),(ep,key,start)
                assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_DS)==ds
                cases.append(dict(load=load,episode=ep,key=key,start_word=start,effective_start=start&255,found=match is not None,result=expected,error_calls=state['errors'],passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='secondary_class_suffix_search',start=0xfbe,end_exclusive=0xff3,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],cases=len(cases),failures=0,visited_instruction_starts=len(visited),static_instruction_starts=len(decoded),unvisited_instruction_starts=sorted(set(decoded)-visited),scope='original lookup with actual three MAP secondary headers; only error reporter mocked returning BEEF; no natural map-instance reachability or full caller domain proof',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
