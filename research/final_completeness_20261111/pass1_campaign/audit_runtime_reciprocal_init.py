"""python audit_runtime_reciprocal_init.py IMAGE INVENTORY DECODER RUNTIME_OUT WORK OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,runtime,work,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';proof=json.loads((runtime/'independent_verification.json').read_text());assert proof['initialization_checks_passed']
for f in proof['files']:assert sha(Path(f['path']).read_bytes())==f['sha256']
lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);todo=[0];decoded={};rows=[]
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0<=ip<0x2f;i=Decoder(16,b[0x1560+ip:0x158f],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
for ip,i in sorted(decoded.items()):
    raw=b[0x1560+ip:0x1560+i.next_ip];assert lookup[(0x156,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x156,ip=ip,image_offset=0x1560+ip,bytes=raw.hex(),instruction=fmt.format(i)))
out.mkdir(parents=True,exist_ok=True)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
save('renderer_reciprocal_init',rows);raw=(work/'vga_reciprocal_runtime.bin').read_bytes();values=struct.unpack('<511I',raw);assert list(values)==[0x400000//n for n in range(1,512)]
save('runtime_values',[dict(index=n-1,denominator=n,ds_offset=0x2656+4*(n-1),image_relative=0x27710+0x2656+4*(n-1),observed=value,expected=0x400000//n,passed=True) for n,value in enumerate(values,1)])
save('external_bss_tables',[dict(name='renderer_reciprocal_DWORD511',ds_start=0x2656,ds_end_exclusive=0x2e52,image_start=0x29d66,image_end_exclusive=0x2a562,length=2044,type='DWORD511_little_endian_floor_400000h_div_n_n1_to511',status='PARTIAL',runtime_sha256=sha(raw),outside_original_file_image=True,original_NONCODE_bytes_added=0)])
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),runtime_proof_sha256=sha((runtime/'independent_verification.json').read_bytes()),functions=[dict(name='renderer_reciprocal_init',start=0x1560,end_exclusive=0x158f,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],runtime_values_verified=511,bss_table_bytes=2044,scope='static fixed initializer plus actual DOSBox runtime table; session counted separately by runtime importer, table outside original file and PASS320 baseline',runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
