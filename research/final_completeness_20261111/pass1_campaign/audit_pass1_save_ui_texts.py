"""python audit_pass1_save_ui_texts.py IMAGE INVENTORY DECODER OUT"""
import csv,hashlib,json,re,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,OpKind
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
spec=[(0x29597,[0x1e56],'selected_message_fragment'),(0x2959f,[0x1e5c],'selected_message_fragment'),(0x295a6,[0x1e60],'format_two_near_strings'),(0x295b0,[0x2199],'cheat_notice'),(0x29612,[0x224c],'save_filename'),(0x2961b,[0x2265],'empty_slot_copy_27B'),(0x29636,[0x232a],'save_filename'),(0x2963f,[0x2393],'save_filename'),(0x29648,[0x23ac],'empty_slot_copy_27B'),(0x29663,[0x2401],'save_filename'),(0x2966c,[0x243a],'save_filename'),(0x29675,[0x244d],'save_action_label'),(0x2967a,[0x2450],'save_confirmation_format'),(0x296a7,[0x2476],'save_filename'),(0x296b0,[0x24a6],'save_filename'),(0x296b9,[0x24b9],'load_action_label'),(0x296be,[0x24bc],'load_confirmation_format'),(0x296eb,[0x24dd],'save_filename'),(0x296f4,[0x25c1],'save_filename'),(0x296fd,[0x25f3],'save_filename'),(0x29706,[0x2629],'map_name_prefix'),(0x2970b,[0x262c],'map_name_format'),(0x29710,[0x269f],'map_name_prefix'),(0x29715,[0x26a2],'map_name_format'),(0x2971a,[0x2741],'weapon_jam_message'),(0x2973c,[0x2899],'quit_confirmation')]
fields=[];catalog=[];refs=[]
for index,(a,ips,role) in enumerate(spec):
    e=b.index(0,a)+1;raw=b[a:e];assert e==(spec[index+1][0] if index+1<len(spec) else 0x29749);text=raw[:-1].decode('ascii')
    for ip in ips:
        r=lookup[(0xd29,ip)];iraw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(iraw)]==iraw;i=Decoder(16,iraw,ip=ip).decode();assert not i.is_invalid and i.len==len(iraw)
        assert any(i.op_kind(k)==OpKind.IMMEDIATE16 for k in range(i.op_count)) and i.immediate16==a-0x27710
        refs.append(dict(field_start=a,cs=0xd29,ip=ip,image_offset=r['image_offset'],bytes=iraw.hex(),instruction=fmt.format(i),scope='specific literal operand; downstream selected context in contexts.csv'))
    fields.append(dict(name='ui_'+role+'_'+format(a,'05x'),start=a,end_exclusive=e,length=e-a,type='NUL_ASCII_'+role,status='PARTIAL',range_sha256=sha(raw)))
    catalog.append(dict(start=a,end_exclusive=e,text=text,role=role,reference_ips=';'.join('0D29:%04X'%ip for ip in ips),format_tokens=';'.join(re.findall(r'%[sd]',text))))
assert sum(f['length'] for f in fields)==434 and b[0x29749]==0
for a,ip in [(0x2961b,0x2265),(0x29648,0x23ac)]:
    assert len(b[a:b.index(0,a)+1])==27
    assert lookup[(0xd29,ip+8)]['bytes']=='66b906000000'
    assert lookup[(0xd29,ip+14)]['bytes']=='f366a5' and lookup[(0xd29,ip+17)]['bytes']=='a5' and lookup[(0xd29,ip+18)]['bytes']=='a4'
contexts=[]
for r in old:
    if r['cs']!=0xd29 or not any(ip-8<=r['ip']<=ip+30 for _,ips,_ in spec for ip in ips):continue
    raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw)
    contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i),scope='selected caller context; not full functions or all CFG branches'))
for name,rows in [('data_fields',fields),('text_catalog',catalog),('literal_references',refs),('contexts',contexts)]:save(name,rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=434,fields=len(fields),verified_context_instructions=len(contexts),scope='exact literal operands and selected consumers; two 27B copies proven statically; no original file I/O, UI, sprintf or SAVE format execution',save_format_closed=False,load_behavior_closed=False,trailing_zero_padding_proven=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
