"""Independent INT63 dispatcher decode and typed lookup-window extraction.
Usage: python audit_int63_window.py DECODER_DIR IMAGE OUT_DIR
The 256-word addressable window is not asserted to be one 256-entry table.
"""
import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

def csvout(path,rows):
    with path.open('w',encoding='utf-8',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    decoder,image_path,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder))
    from iced_x86 import Decoder,Formatter,FormatterSyntax
    image=image_path.read_bytes();h=hashlib.sha256(image).hexdigest()
    if h!='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297':raise ValueError('wrong image')
    base=0x15bf0;fmt=Formatter(FormatterSyntax.INTEL);rows=[]
    for ins in Decoder(16,image[0x18cd6:0x18d19],ip=0x30e6):
        if ins.is_invalid:raise ValueError('invalid dispatcher instruction')
        a=base+ins.ip
        rows.append(dict(image_offset=a,cs=0x15bf,ip=ins.ip,length=ins.len,bytes=image[a:a+ins.len].hex(),instruction=fmt.format(ins)))
    if rows[-1]['image_offset']!=0x18d18 or rows[-1]['bytes']!='cf':raise ValueError('expected IRET boundary')
    # Critical dispatch operations are checked as exact bytes, separately from decoder text.
    expected={0x18ce6:'fc',0x18ce9:'50',0x18cea:'86e0',0x18cec:'32e4',0x18cee:'d1e0',0x18cf0:'8bf0',0x18cf2:'58',0x18cf3:'2eff942020'}
    for a,code in expected.items():
        if image[a:a+len(bytes.fromhex(code))]!=bytes.fromhex(code):raise ValueError('critical byte assumption mismatch at '+hex(a))
    slots=[]
    for selector in range(256):
        offset=0x2020+2*selector;a=base+offset;value=struct.unpack_from('<H',image,a)[0]
        role='candidate_initialized_service_slot' if selector<82 else 'addressable_neighbor_not_proven_table'
        if selector==0x52:role='counter_word_CS20C4_not_service_slot'
        if selector in (0xd4,0xd5):role='FAR_callback_word_not_service_slot'
        slots.append(dict(selector=selector,cs_word_offset=offset,image_start=a,image_end_exclusive=a+2,initial_word=value,effective_near_call_image=base+value,role=role,status='PARTIAL',pass320_membership='UNKNOWN'))
    if slots[0x49]['effective_near_call_image']!=0x17f39:raise ValueError('service49 target mismatch')
    if image[0x17f39:0x17f3f]!=bytes.fromhex('bb0000e87b0e'):raise ValueError('service49 prefix mismatch')
    # CALL displacement is relative to current segment IP, with 16-bit wrapping.
    helper=base+((0x17f3f-base+struct.unpack_from('<h',image,0x17f3d)[0])&65535)
    if helper!=0x18dba:raise ValueError('service49 helper mismatch')
    out.mkdir(parents=True,exist_ok=True)
    csvout(out/'dispatcher_instructions.csv',rows);csvout(out/'lookup_window.csv',slots)
    result=dict(image_sha256=h,dispatcher_start=0x18cd6,dispatcher_end_exclusive=0x18d19,dispatcher_bytes=67,dispatcher_instructions=len(rows),selector_expression='SI=2*incoming_AH, unsigned 8-bit selector',lookup_start=base+0x2020,lookup_end_exclusive=base+0x2220,lookup_bytes=512,candidate_table_start=base+0x2020,candidate_table_end_exclusive=base+0x20c4,candidate_table_bytes=164,candidate_slots=82,zero_words_in_candidate_slots=[r['selector'] for r in slots[:82] if r['initial_word']==0],counter_alias_selector=0x52,callback_alias_selectors=[0xd4,0xd5],service49_target=0x17f39,service49_helper=helper,dispatcher_executes_cld=True,global_selector_bounds_proven=False,status='PARTIAL',original_pass320_ledger_imported=False,new_deep_verified_bytes=0,runtime_tests=0)
    (out/'int63_evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
