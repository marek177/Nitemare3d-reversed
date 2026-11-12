"""python audit_bsf_assets_native_codec.py IMAGE PATH_LIST EMULATOR OUT"""
import csv,hashlib,json,struct,sys,functools,operator
from pathlib import Path
image,pathlist,emu,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(emu.resolve()))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
key=b[0x29755:0x29789];assert len(key)==52;out.mkdir(parents=True,exist_ok=True)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
assets=[];resources=[];inputs=[];headers=[]
for name in pathlist.read_text(encoding='utf-8-sig').splitlines():
    p=Path(name);raw=p.read_bytes();assert len(raw)>=54;head=bytes(v^key[i%52] for i,v in enumerate(raw[:54]));offsets=struct.unpack_from('<3I',head,36);lengths=struct.unpack_from('<3H',head,48)
    exact=offsets[0]==54 and offsets[1]==offsets[0]+lengths[0] and offsets[2]==offsets[1]+lengths[1] and offsets[2]+lengths[2]==len(raw)
    assert exact,(name,len(raw),offsets,lengths)
    assets.append(dict(path=str(p),bytes=len(raw),sha256=sha(raw),header_encoded_sha256=sha(raw[:54]),header_decoded_sha256=sha(head),header_input_xor=functools.reduce(operator.xor,raw[:54],0),byte_1=head[1],byte_2=head[2],byte_3=head[3],name_bytes_hex=head[4:36].hex(),exact_resource_partition=exact))
    headers.append(dict(path=str(p),file_sha256=sha(raw),decoded_header_hex=head.hex()))
    inputs.append((str(p),'header',raw[:54],head))
    for idx,(off,n) in enumerate(zip(offsets,lengths)):
        encoded=raw[off:off+n];decoded=bytes(v^key[i%52] for i,v in enumerate(encoded));assert len(encoded)==n
        resources.append(dict(path=str(p),slot=idx,dispatcher_mode=(4,3,5)[idx],file_offset=off,length=n,end_exclusive=off+n,encoded_sha256=sha(encoded),decoded_sha256=sha(decoded),input_xor=functools.reduce(operator.xor,encoded,0),decoded_nuls=decoded.count(0),decoded_first_32_hex=decoded[:32].hex()))
        inputs.append((str(p),'slot_'+str(idx),encoded,decoded))
save('assets',assets);save('resources',resources);(out/'decoded_headers.json').write_text(json.dumps(headers,indent=2)+'\n')
cases=[];rel=list(csv.DictReader((image.parent/'relocations.csv').open()))
for load in (0,0x1000):
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,b);cs=load+0xfba;ss=load+0x2771
    for r in rel:u.mem_write(load*16+int(r['image_offset']),struct.pack('<H',(int(r['original_word'])+load)&65535))
    for name,kind,encoded,decoded in inputs:
        assert len(encoded)<65536;u.mem_write(0x61000,encoded+b'\xa5\x5a')
        for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_SS,ss),(UC_X86_REG_DS,ss),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x9abc),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
        u.mem_write(ss*16+0xff00,struct.pack('<HHHHH',0x6000,cs,0x1000,0x6000,len(encoded)));u.emu_start(cs*16+0x1b2,cs*16+0x6000,count=2000000)
        assert bytes(u.mem_read(0x61000,len(encoded)+2))==decoded+b'\xa5\x5a' and u.reg_read(UC_X86_REG_AL)==functools.reduce(operator.xor,encoded,0)
        assert u.reg_read(UC_X86_REG_SP)==0xff04 and u.reg_read(UC_X86_REG_DS)==ss and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x9abc
        cases.append(dict(load=load,path=name,kind=kind,length=len(encoded),decoded_sha256=sha(decoded),passed=True))
save('cases',cases)
s=dict(image_sha256=sha(b),path_list_sha256=sha(pathlist.read_bytes()),assets=len(assets),unique_file_sha256=len({a['sha256'] for a in assets}),exact_resource_partitions=sum(a['exact_resource_partition'] for a in assets),zero_header_xor=sum(a['header_input_xor']==0 for a in assets),resources=len(resources),cases=len(cases),failures=0,scope='actual BSF bytes partitioned by decoded 54B header; DOS native XOR executed for headers and three blocks at two load bases; Windows paths tested as data only, no natural file I/O or full resource semantics',runtime_tests=0,new_deep_verified_bytes=0,cases_sha256=sha((out/'cases.csv').read_bytes()))
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
