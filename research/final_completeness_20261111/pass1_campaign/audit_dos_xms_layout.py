"""Typed XMS-adapter fields and bounded operand xrefs, not runtime certification.
Usage: python audit_dos_xms_layout.py IMAGE OLD_INSTRUCTIONS DECODER_DIR OUT_DIR
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,old,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,InstructionInfoFactory,MemorySizeExt,Register
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;fmt=Formatter(FormatterSyntax.INTEL);factory=InstructionInfoFactory();refs=[]
for r in json.loads(old.read_text(encoding='utf-8')):
    if r['cs']!=0x15bf:continue
    a=r['image_offset'];raw=bytes.fromhex(r['bytes']);assert base+r['ip']==a and b[a:a+len(raw)]==raw
    ins=Decoder(16,raw,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(raw)
    for m in factory.info(ins).used_memory():
        if m.segment==Register.CS and 0x20c4<=m.displacement<0x21dc:
            refs.append(dict(image_offset=a,cs=r['cs'],ip=r['ip'],bytes=raw.hex(),instruction=fmt.format(ins),displacement=m.displacement,width=MemorySizeExt.size(m.memory_size),base_register=m.base,index_register=m.index,access_enum=m.access,address_kind='indexed_base_not_resolved' if m.base or m.index else 'fixed_CS',status='PARTIAL'))
fields=[]
for start,size,name,typ in [(0x20c4,2,'resource_counter','WORD'),(0x21c6,2,'allocated_xms_handle','WORD'),(0x21c8,4,'xms_control_entry','FAR16'),(0x21cc,4,'move_length','DWORD'),(0x21d0,2,'move_source_handle','WORD'),(0x21d2,4,'move_source_offset','DWORD_or_FAR16_when_handle_zero'),(0x21d6,2,'move_dest_handle','WORD'),(0x21d8,4,'move_dest_offset','DWORD_or_FAR16_when_handle_zero'),(0x2249,256,'service49_transfer_buffer','BYTE[256]')]:
    raw=b[base+start:base+start+size]
    fields.append(dict(name=name,cs=0x15bf,start=start,end_exclusive=start+size,image_start=base+start,image_end_exclusive=base+start+size,size=size,type=typ,initial_bytes=raw.hex(),range_sha256=hashlib.sha256(raw).hexdigest(),status='PARTIAL',pass320_membership='UNKNOWN'))
critical={0x17f4d:'bf4922',0x17f50:'0e',0x17f51:'07',0x17f97:'bb0001',0x17f9a:'e8810d',0x17e09:'b81043',0x17e0c:'cd2f',0x17e20:'b409',0x17fa2:'2ea3cc21',0x17faa:'b40b',0x17fac:'2eff1ec821',0x17fb3:'2ea1cc21',0x17fc0:'2e0187ca20',0x17fc5:'2e8397cc2000'}
for a,raw in critical.items():assert b[a:a+len(bytes.fromhex(raw))]==bytes.fromhex(raw)
aliases=[]
for n in (0,1,62,63,64,0x3fe9):
    lo=(0x20ca+4*n)&65535;hi=(0x20cc+4*n)&65535
    aliases.append(dict(counter=n,indexed_write_low=lo,indexed_write_high=hi,overlapping_named_fields=';'.join(f['name'] for f in fields if any(f['start']<=p<f['end_exclusive'] for p in (lo,lo+1,hi,hi+1))),scope='address arithmetic only; counter reachability not proven'))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('data_fields.csv',fields),('cs_operand_xrefs.csv',refs),('counter_metadata_aliases.csv',aliases)]:
    with (out/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
result=dict(image_sha256=h,instruction_inventory_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),typed_fields=len(fields),typed_field_bytes=sum(f['size'] for f in fields),move_structure_start=base+0x21cc,move_structure_end_exclusive=base+0x21dc,move_structure_bytes=16,cs_operand_references=len(refs),fixed_references=sum(r['address_kind']=='fixed_CS' for r in refs),indexed_references=sum(r['address_kind']!='fixed_CS' for r in refs),counter63_aliases_xms_metadata=True,counter_reachability_proven=False,global_xrefs_complete=False,typed_bytes_are_not_additive_to_campaign_catalog=True,original_pass320_ledger_imported=False,new_deep_verified_bytes=0,runtime_tests=0)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
