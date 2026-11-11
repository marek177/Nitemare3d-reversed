"""Decode sample IRQ and mutable operands as overlays, not disjoint DATA bytes.
Usage: python audit_dos_sample_irq.py IMAGE INSTRUCTIONS DECODER_DIR OUT_DIR
"""
import csv,hashlib,json,sys
from pathlib import Path
image,old,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,InstructionInfoFactory,MemorySizeExt,Register
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;start=0x19241;end=0x192d2;fmt=Formatter(FormatterSyntax.INTEL);instructions=[];owners={};edges=[]
for ins in Decoder(16,b[start:end],ip=start-base):
    a=base+ins.ip;raw=b[a:a+ins.len];assert not ins.is_invalid
    instructions.append(dict(image_offset=a,cs=0x15bf,ip=ins.ip,bytes=raw.hex(),instruction=fmt.format(ins)))
    for pos in range(a,a+ins.len):owners[pos]=(a,ins)
assert instructions[-1]['bytes']=='cf' and instructions[-1]['image_offset']==end-1
fields=[]
for offset,name,kind in [(0x364f,'fractional_accumulator','standalone_DATA'),(0x366c,'end_offset','EMBEDDED_CODE_OPERAND'),(0x3675,'fractional_step','EMBEDDED_CODE_OPERAND'),(0x367c,'integer_step','EMBEDDED_CODE_OPERAND'),(0x367f,'sample_segment','EMBEDDED_CODE_OPERAND'),(0x3684,'sample_offset','EMBEDDED_CODE_OPERAND'),(0x3691,'lookup_address','EMBEDDED_CODE_OPERAND')]:
    a=base+offset;owner=owners.get(a)
    if kind.startswith('EMBEDDED'):
        assert b[a:a+2]==bytes.fromhex('5555') and owners[a]==owners[a+1]
        # Ask a decoder for encoded immediate/displacement locations independently.
        d=Decoder(16,b[owner[0]:owner[0]+15],ip=owner[0]-base);ins=d.decode();c=d.get_constant_offsets(ins)
        locations=[(owner[0]+c.immediate_offset,c.immediate_size,'immediate'),(owner[0]+c.displacement_offset,c.displacement_size,'displacement')]
        matching=[typ for pos,size,typ in locations if pos==a and size==2];assert len(matching)==1
    else:matching=['standalone']
    fields.append(dict(name=name,cs=0x15bf,offset=offset,image_start=a,image_end_exclusive=a+2,type=kind,encoded_role=matching[0],owner_instruction_image=owner[0] if owner else '',initial_bytes=b[a:a+2].hex(),status='PARTIAL',pass320_membership='UNKNOWN'))
refs=[];factory=InstructionInfoFactory()
for r in json.loads(old.read_text()):
    if r['cs']!=0x15bf:continue
    raw=bytes.fromhex(r['bytes']);a=r['image_offset'];assert b[a:a+len(raw)]==raw
    ins=Decoder(16,raw,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(raw)
    for mem in factory.info(ins).used_memory():
        if mem.segment!=Register.CS or mem.base!=Register.NONE or mem.index!=Register.NONE:continue
        for f in fields:
            if mem.displacement<f['offset']+2 and mem.displacement+MemorySizeExt.size(mem.memory_size)>f['offset']:
                refs.append(dict(field=f['name'],image_offset=a,bytes=raw.hex(),instruction=fmt.format(ins),access_enum=mem.access,status='PARTIAL'))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('sample_irq.csv',instructions),('operand_overlays.csv',fields),('fixed_cs_xrefs.csv',refs)]:
    with (out/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
r=dict(image_sha256=h,functions=[dict(name='sample_irq',start=start,end_exclusive=end,instruction_bytes=end-start,instructions=len(instructions))],overlay_bytes=12,standalone_data_intervals=[dict(start=base+0x364f,end_exclusive=base+0x3651)],fixed_cs_references=len(refs),new_deep_verified_bytes=0,runtime_tests=0,scope='mutable code operands are overlays and must not be added to disjoint DATA totals')
(out/'summary.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
