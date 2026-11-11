"""Byte-backed local WORX dataflow catalog; does not claim exhaustive xrefs.
Usage: python audit_worx_dataflow.py IMAGE INSTRUCTIONS_JSON OUT_DIR
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

def csvout(path, rows):
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def main():
    image_path, inventory_path, out=map(Path,sys.argv[1:])
    image=image_path.read_bytes(); inventory=json.loads(inventory_path.read_text())
    image_hash=hashlib.sha256(image).hexdigest()
    if image_hash!='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297':
        raise ValueError('image identity mismatch')
    def checked(row):
        a=row['image_offset'];code=bytes.fromhex(row['bytes'])
        if image[a:a+len(code)]!=code or a!=row['cs']*16+row['ip']:
            raise ValueError('inventory mismatch '+hex(a))
        return row
    out.mkdir(parents=True,exist_ok=True)
    functions=[]
    for name,start,end in [('counted_to_asciiz',0x18a46,0x18a66),('counted_mode_setter',0x18a66,0x18a6d),('container_open',0x18ef2,0x18f4b),('container_close',0x18f4b,0x18f6b),('callback_locate',0x17e08,0x17e39)]:
        rows=sorted((checked(r) for r in inventory if start<=r['image_offset']<end),key=lambda r:r['image_offset'])
        cursor=start; gaps=[]
        for row in rows:
            a=row['image_offset']
            if a<cursor:raise ValueError('overlapping function '+name)
            if a>cursor:gaps.append(dict(start=cursor,end_exclusive=a,hex=image[cursor:a].hex(),status='UNKNOWN'))
            cursor=a+len(bytes.fromhex(row['bytes']))
        if cursor!=end:
            raise ValueError('incomplete function '+name)
        csvout(out/(name+'.csv'),rows)
        functions.append(dict(name=name,start=start,end_exclusive=end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),inventory_gaps=gaps,instructions=len(rows),range_sha256=hashlib.sha256(image[start:end]).hexdigest(),status='PARTIAL',pass320_membership='UNKNOWN'))
    xrefs=[]
    slots=[0x20c4,0x21c6,0x21c8,0x21ca,0x2c0c,0x2df3,0x2df5,0x2e10,0x312d]
    for row in inventory:
        if row['cs']!=0x15bf or 'cs:[' not in row['operands']:
            continue
        for slot in slots:
            if '0x%x]'%slot in row['operands']:
                checked(row)
                xrefs.append(dict(slot_cs_offset=slot,slot_image_offset=0x15bf0+slot,instruction_image_offset=row['image_offset'],bytes=row['bytes'],mnemonic=row['mnemonic'],operands=row['operands'],scope='direct literal CS access in supplied historical inventory only'))
    csvout(out/'direct_xrefs.csv',xrefs)
    data=[]
    for offset,length,role in [(0x21c6,2,'word assigned from incoming BX saved across callback AH=0'),(0x21c8,4,'FAR callback: BX offset, ES segment after INT2F AX4310'),(0x2c0c,1,'counted-string conversion enable'),(0x2df3,2,'DOS file handle; FFFF sentinel'),(0x2df5,2,'container record count loaded by DOS read request of 2 bytes'),(0x2e10,1,'container-open mode flag')]:
        a=0x15bf0+offset
        data.append(dict(start=a,end_exclusive=a+length,length=length,cs='15BF',offset=offset,initial_hex=image[a:a+length].hex(),range_sha256=hashlib.sha256(image[a:a+length]).hexdigest(),role=role,status='PARTIAL',pass320_membership='UNKNOWN'))
    csvout(out/'data_intervals.csv',data)
    result=dict(image_sha256=image_hash,inventory_sha256=hashlib.sha256(inventory_path.read_bytes()).hexdigest(),functions=functions,data_intervals=data,xref_count=len(xrefs),xref_exhaustiveness='NOT_PROVEN',new_deep_verified_bytes=0,runtime_tests=0)
    (out/'dataflow_evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'functions':functions,'xref_count':len(xrefs),'new_deep_verified_bytes':0},indent=2))

if __name__=='__main__':main()
