"""Byte-match two leafs; arithmetic examples are synthetic, not runtime tests.
Usage: python audit_worx_leafs.py IMAGE OLD_INSTRUCTIONS_JSON OUT_DIR
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

def main():
    image_path, inventory_path, out = map(Path, sys.argv[1:])
    image = image_path.read_bytes()
    expected = 'e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
    if hashlib.sha256(image).hexdigest() != expected:
        raise ValueError('image identity mismatch')
    inventory = json.loads(inventory_path.read_text())
    catalog = []
    out.mkdir(parents=True, exist_ok=True)
    for name, start, end in [('normalize_es_di',0x1a220,0x1a25a), ('uppercase_asciiz_in_place',0x1a49f,0x1a4c9)]:
        rows = sorted((r for r in inventory if start <= r['image_offset'] < end), key=lambda r:r['image_offset'])
        cursor, gaps = start, []
        for row in rows:
            code = bytes.fromhex(row['bytes']); a = row['image_offset']
            if a < cursor or image[a:a+len(code)] != code or row['cs']*16 != 0x15bf0 or a != row['cs']*16+row['ip']:
                raise ValueError('range/bytes/segment mismatch at '+hex(a))
            if a > cursor:
                gaps.append(dict(start=cursor,end_exclusive=a,hex=image[cursor:a].hex(),status='UNKNOWN'))
            cursor = a+len(code)
        if cursor != end or rows[-1]['bytes'] != 'c3':
            raise ValueError('incomplete function range')
        with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as stream:
            writer = csv.DictWriter(stream,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        catalog.append(dict(name=name,start=start,end_exclusive=end,span_bytes=end-start,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows),inventory_gaps=gaps,range_sha256=hashlib.sha256(image[start:end]).hexdigest(),status='PARTIAL',pass320_membership='UNKNOWN'))
    examples = []
    for es in (0,1,0x15bf,0x8000,0xffff):
        for di in (0,1,15,16,0x7fff,0xffff):
            ax, dx = es, 0
            if es:
                for _ in range(4):
                    carry=ax>>15; ax=(ax<<1)&65535; dx=((dx<<1)|carry)&65535
                total=ax+di; ax=total&65535; dx=(dx+(total>>16))&65535
                new_di=ax&15
                for _ in range(4):
                    carry=dx&1; dx>>=1; ax=(ax>>1)|(carry<<15)
                actual=(ax,new_di); simplified=((es+(di>>4))&65535,di&15)
            else:
                actual=simplified=(es,di)
            if actual != simplified:
                raise ValueError('arithmetic discrepancy')
            examples.append(dict(es=es,di=di,new_es=actual[0],new_di=actual[1],kind='synthetic_arithmetic_only'))
    result=dict(image_sha256=expected,inventory_sha256=hashlib.sha256(inventory_path.read_bytes()).hexdigest(),functions=catalog,instruction_bytes=sum(r['instruction_bytes'] for r in catalog),arithmetic_examples=examples,new_deep_verified_bytes=0,runtime_tests=0)
    (out/'leaf_evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'functions':catalog,'arithmetic_examples':len(examples),'new_deep_verified_bytes':0},indent=2))

if __name__ == '__main__':
    main()
