"""python audit_pass1_ui_strings.py IMAGE PRIOR_MAP OUTPUTS_ROOT OUT"""
import collections,csv,hashlib,json,struct,sys
from pathlib import Path
image,prior,root,out=map(Path,sys.argv[1:]);b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader((image.parent/'relocations.csv').open())}
fields={};refs=[]
for folder in ['pass1_menu_records','pass1_menu_records_more','pass1_menu_tail','pass1_ui_callbacks','pass1_grid_ui']:
    path=root/folder/'records.csv'
    for r in csv.DictReader(path.open()):
        if r['sentinel']=='True':continue
        p=int(r['start']);offset,segment=struct.unpack_from('<HH',b,p+14)
        assert segment==0x2771 and rel[p+16]==segment
        a=segment*16+offset;e=b.index(0,a)+1
        assert 0x27710<=a<e<=len(b) and all(32<=v<127 for v in b[a:e-1])
        fields[a]=dict(name='ui_text_'+hex(a)[2:],start=a,end_exclusive=e,length=e-a,type='NUL_terminated_ASCII',text=b[a:e-1].decode('ascii'),status='PARTIAL',range_sha256=sha(b[a:e]))
        refs.append(dict(source=folder,source_csv_sha256=sha(path.read_bytes()),record_start=p,pointer_start=p+14,relocation_site=p+16,text_start=a,text_end_exclusive=e,scope='initial FAR field and generic UI consumer; natural DS and renderer closure open'))
fields=sorted(fields.values(),key=lambda f:f['start']);covered={}
for f in fields:
    for p in range(f['start'],f['end_exclusive']):assert p not in covered;covered[p]=f['name']
states={}
for r in csv.DictReader(prior.open(encoding='utf-8-sig')):
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    for p in range(a,e):assert p not in states;states[p]=r
assert set(covered)<=set(states) and len(states)==57295
updated=[];promoted=collections.Counter()
for r in csv.DictReader(prior.open(encoding='utf-8-sig')):
    a,e=int(r['start']),int(r['end_exclusive']);cuts=sorted({a,e}|{p for f in fields for p in (f['start'],f['end_exclusive']) if a<p<e})
    for x,y in zip(cuts,cuts[1:]):
        n=dict(r);n.update(start=x,end_exclusive=y,length=y-x,range_sha256=sha(b[x:y]),ui_string='')
        if x in covered:
            if r['status']!='PARTIAL':promoted[r['status']]+=y-x
            n.update(status='PARTIAL',ui_string=covered[x])
        updated.append(n)
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('data_fields',fields),('text_references',refs),('noncode_intervals',updated)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n')
c=collections.Counter()
for r in updated:c[r['status']]+=int(r['length'])
assert sum(c.values())==57295
s=dict(image_sha256=sha(b),prior_sha256=sha(prior.read_bytes()),strings=len(fields),references=len(refs),text_bytes=len(covered),promoted_from=dict(promoted),status_bytes=dict(c),runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
