"""Byte-pinned error-path evidence and conditional default-DS text objects.
Usage: python audit_pass1_error_path.py IMAGE PRIOR_MAP DECODER_DIR OUT
"""
import collections,csv,hashlib,json,sys
from pathlib import Path
image,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
for p,h in {0xb842:'685e01',0xb845:'68ad16',0xb848:'9a0c00ba0f',0xb8e9:'6a64',0xb8eb:'68c216',0xb8ee:'9a0c00ba0f',0xfbcc:'6a01',0xfbce:'9aeb01ee11',0x120ce:'33c9',0x1214a:'b44c',0x1214c:'cd21'}.items():
    assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h),hex(p)
texts=[(0x28dbd,b'MAXOBJ exceeded (%d)\0','object_limit_format'),(0x28dd2,b'MAXGUARD exceeded (%d)\0','guard_limit_format'),(0x2974a,b'.\n\0','error_suffix')]
fields=[]
for a,s,name in texts:
    assert b[a:a+len(s)]==s
    fields.append(dict(name=name,start=a,end_exclusive=a+len(s),length=len(s),type='NUL_terminated_ASCII',status='PARTIAL',text=repr(s),range_sha256=sha(s),condition='incoming default DS; formatting helper contract incomplete'))
rows=list(csv.DictReader(prior.open(encoding='utf-8-sig')));updated=[];added=0
for r in rows:
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    cuts=sorted({a,e}|{p for f in fields for p in [f['start'],f['end_exclusive']] if a<p<e})
    for x,y in zip(cuts,cuts[1:]):
        n=dict(r);n.update(start=x,end_exclusive=y,length=y-x,range_sha256=sha(b[x:y]),error_text='')
        for f in fields:
            if f['start']<=x<f['end_exclusive']:
                added+=y-x if r['status']!='PARTIAL' else 0;n.update(status='PARTIAL',error_text=f['name'])
        updated.append(n)
insns=[];fmt=Formatter(FormatterSyntax.INTEL)
for name,a,e,cs in [('error_helper',0xfbac,0xfbd5,0xfba),('exit_entry',0x120cb,0x120d2,0x11ee),('exit_shared',0x120ec,0x12152,0x11ee),('cleanup_indirect',0x12152,0x1217e,0x11ee),('format_wrapper',0x1473a,0x14777,0x11ee)]:
    pos=a
    for ins in Decoder(16,b[a:e],ip=a-cs*16):
        assert not ins.is_invalid;insns.append(dict(block=name,image_offset=pos,cs=cs,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==e
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('evidence_instructions',insns),('noncode_intervals',updated)]:
    with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n')
c=collections.Counter()
for r in updated:c[r['status']]+=int(r['length'])
assert sum(c.values())==57295
s=dict(image_sha256=sha(b),prior_sha256=sha(prior.read_bytes()),text_bytes=sum(f['length'] for f in fields),new_partial_bytes=added,status_bytes=dict(c),exit_code_argument=1,dos_termination_instruction=0x1214c,cleanup_indirect_targets_closed=False,unconditional_noreturn_proven=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
