"""Byte-backed mutable RIFF/WAVE-shaped header and three consumer ranges.
Usage: python audit_wave_header.py DECODER_DIR IMAGE INVENTORY OUT_DIR
Format-derived names are distinguished from instruction-proven uses.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path

def csvout(path,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    dep,ipath,hpath,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep))
    from iced_x86 import Decoder,Formatter,FormatterSyntax,Register,OpKind
    b=ipath.read_bytes();image_hash=hashlib.sha256(b).hexdigest()
    if image_hash!='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297':raise ValueError('wrong image')
    inv=json.loads(hpath.read_text());fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
    functions=[]
    for name,start,end in [('wave_timer_playback_init',0x19187,0x1923f),('wave_file_playback_init',0x1b8e6,0x1b95f),('wave_memory_playback_init',0x1b95f,0x1b9e2)]:
        rows=sorted((r for r in inv if start<=r['image_offset']<end),key=lambda r:r['image_offset']);cursor=start;gaps=[];independent=[]
        for r in rows:
            a=r['image_offset'];code=bytes.fromhex(r['bytes']);ins=Decoder(16,code,ip=r['ip']).decode()
            if a<cursor or b[a:a+len(code)]!=code or ins.is_invalid or ins.len!=len(code) or a!=r['cs']*16+r['ip']:raise ValueError('instruction mismatch')
            if a>cursor:gaps.append(dict(start=cursor,end_exclusive=a,hex=b[cursor:a].hex(),status='UNKNOWN'))
            cursor=a+len(code)
            independent.append(dict(image_offset=a,bytes=code.hex(),iced_text=fmt.format(ins)))
        if cursor!=end:raise ValueError('missing tail')
        csvout(out/(name+'.csv'),rows);csvout(out/(name+'_independent.csv'),independent)
        functions.append(dict(name=name,start=start,end_exclusive=end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows),inventory_gaps=gaps,status='PARTIAL',pass320_membership='UNKNOWN'))
    header=0x1b588
    if not (b[header:header+4]==b'RIFF' and b[header+8:header+16]==b'WAVEfmt ' and b[header+36:header+40]==b'data'):raise ValueError('marker layout mismatch')
    specs=[(0,4,'RIFF_marker','initial marker; overwritten by full header copy'),(4,4,'RIFF_size','format-derived; consumer not closed'),(8,4,'WAVE_marker','initial marker; overwritten by full header copy'),(12,4,'fmt_marker','initial marker; overwritten by full header copy'),(16,4,'fmt_size','format-derived; consumer not closed'),(20,2,'format_tag','format-derived; consumer not closed'),(22,2,'channels','format-derived; consumer not closed'),(24,4,'samples_per_second','format-derived DWORD; low WORD used by all three local consumers'),(28,4,'average_bytes_per_second','format-derived; consumer not closed'),(32,2,'block_align','format-derived; consumer not closed'),(34,2,'bits_per_sample','format-derived; consumer not closed'),(36,4,'data_marker','initial marker; no ASCIIZ consumer established'),(40,4,'data_size','DWORD consumed as two words at 59C0/59C2 by two local consumers; low word only by timer path')]
    fields=[]
    for offset,size,name,use in specs:
        a=header+offset
        fields.append(dict(name=name,start=a,end_exclusive=a+size,header_offset=offset,cs_offset=0x5998+offset,size=size,initial_hex=b[a:a+size].hex(),range_sha256=hashlib.sha256(b[a:a+size]).hexdigest(),use=use,status='PARTIAL',pass320_membership='UNKNOWN'))
    refs=[]
    for r in inv:
        a=r['image_offset'];code=bytes.fromhex(r['bytes']);ins=Decoder(16,code,ip=r['ip']).decode()
        if ins.is_invalid or ins.len!=len(code) or b[a:a+len(code)]!=code:raise ValueError('global inventory conflict')
        if not any(ins.op_kind(n)==OpKind.MEMORY for n in range(ins.op_count)):continue
        if ins.memory_segment!=Register.CS or ins.memory_base!=Register.NONE or ins.memory_index!=Register.NONE:continue
        target=r['cs']*16+ins.memory_displacement
        if header<=target<header+44:
            refs.append(dict(instruction_image_offset=a,bytes=code.hex(),instruction=fmt.format(ins),target_image_offset=target,header_offset=target-header,scope='literal CS references only; bulk copies tracked separately'))
    csvout(out/'header_fields.csv',fields);csvout(out/'header_direct_xrefs.csv',refs)
    result=dict(image_sha256=image_hash,inventory_sha256=hashlib.sha256(hpath.read_bytes()).hexdigest(),header_start=header,header_end_exclusive=header+44,header_sha256=hashlib.sha256(b[header:header+44]).hexdigest(),header_initial_hex=b[header:header+44].hex(),header_status='PARTIAL',functions=functions,field_count=len(fields),direct_xref_count=len(refs),new_deep_verified_bytes=0,runtime_tests=0,original_pass320_ledger_imported=False)
    (out/'wave_header_evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
