"""Byte-check historical ASM records and reconstruct direct helper CFG.
Run: python audit_worx_helper.py IMAGE INSTRUCTIONS_JSON OUT_DIR
Mnemonic text is historical; relative control-flow targets below come from bytes.
"""
import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

def main():
    image_path, inventory_path, out = map(Path, sys.argv[1:])
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != 'e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297':
        raise ValueError('image identity mismatch')
    source = json.loads(inventory_path.read_text())
    start, end, base = 0x18dba, 0x18ef2, 0x15bf0
    rows = sorted((x for x in source if start <= x['image_offset'] < end), key=lambda x:x['image_offset'])
    cursor, edges, gaps = start, [], []
    for row in rows:
        address, code = row['image_offset'], bytes.fromhex(row['bytes'])
        if address < cursor or image[address:address+len(code)] != code:
            raise ValueError('overlap or mismatching bytes at '+hex(address))
        if address > cursor:
            gaps.append(dict(start=cursor,end_exclusive=address,hex=image[cursor:address].hex(),status='UNKNOWN'))
        if row['cs']*16 != base or row['cs']*16+row['ip'] != address:
            raise ValueError('segment context mismatch')
        cursor = address + len(code)
        opcode = code[0]
        if opcode in (0xe8, 0xe9):
            target = base + ((row['ip']+len(code)+struct.unpack_from('<h', code, 1)[0]) & 0xffff)
            edges.append(dict(source=address,target=target,kind='near_call' if opcode==0xe8 else 'jump'))
            if opcode == 0xe9:
                continue
        elif opcode == 0xeb or 0x70 <= opcode <= 0x7f or opcode == 0xe3:
            target = base + ((row['ip']+len(code)+struct.unpack_from('<b', code, 1)[0]) & 0xffff)
            edges.append(dict(source=address,target=target,kind='jump' if opcode==0xeb else 'conditional_taken'))
            if opcode == 0xeb:
                continue
        elif opcode == 0xc3:
            edges.append(dict(source=address,target=None,kind='near_return'))
            continue
        elif opcode == 0xcd:
            edges.append(dict(source=address,target=code[1],kind='interrupt_vector'))
        edges.append(dict(source=address,target=cursor,kind='fallthrough_or_call_continuation'))
    if cursor != end:
        raise ValueError('helper end not covered')
    boundaries = {r['image_offset'] for r in rows}
    for edge in edges:
        if edge['kind'] in ('jump','conditional_taken') and edge['target'] not in boundaries:
            raise ValueError('internal edge does not target a decoded boundary')
    intervals=[]
    for offset,length,role in [(0x2df3,2,'DOS handle candidate'),(0x2df5,2,'record count candidate'),(0x2df7,25,'record read buffer: DWORD at +0, DWORD at +8, NUL string at +12'),(0x3129,4,'saved ES:DI pointer'),(0x312d,1,'memory/file mode flag')]:
        a=base+offset
        intervals.append(dict(start=a,end_exclusive=a+length,cs='15BF',offset=offset,length=length,initial_hex=image[a:a+length].hex(),sha256=hashlib.sha256(image[a:a+length]).hexdigest(),role=role,status='PARTIAL',pass320_membership='UNKNOWN'))
    out.mkdir(parents=True,exist_ok=True)
    for name,items in [('instructions.csv',rows),('cfg_edges.csv',edges),('data_intervals.csv',intervals)]:
        with (out/name).open('w',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(items[0]));writer.writeheader();writer.writerows(items)
    result=dict(image_sha256=hashlib.sha256(image).hexdigest(),asm_inventory_sha256=hashlib.sha256(inventory_path.read_bytes()).hexdigest(),start=start,end_exclusive=end,span_bytes=end-start,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instruction_count=len(rows),byte_mismatches=0,inventory_gaps=gaps,edges=edges,data_intervals=intervals,status='PARTIAL',external_call_semantics_closed=False,pass320_membership='UNKNOWN',new_deep_verified_bytes=0,runtime_tests=0)
    (out/'helper_evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('edges','data_intervals')},indent=2))

if __name__=='__main__':
    main()
