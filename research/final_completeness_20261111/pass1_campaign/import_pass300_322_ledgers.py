"""Read supplied archives as evidence, never execute their generators/instructions.
Usage: python import_pass300_322_ledgers.py ZIP IMAGE CAMPAIGN_CSV OUT_DIR
"""
import collections,csv,hashlib,io,json,re,sys,zipfile
from pathlib import Path
archive,image,campaign,out=map(Path,sys.argv[1:]);b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
assert sha(archive.read_bytes())=='d54e2b05a9e5fb6c5091f804a2af14404df6c86c03b9057739f45ce199e9b27d'
out.mkdir(parents=True,exist_ok=True);source=out/'source_ledgers';source.mkdir(exist_ok=True)
archives=[];baseline=None;raw_ledgers={}
with zipfile.ZipFile(archive) as outer:
    for info in outer.infolist():
        if not info.filename.lower().endswith('.zip'):continue
        packed=outer.read(info);m=re.search(r'PASS(\d+)',info.filename);assert m
        with zipfile.ZipFile(io.BytesIO(packed)) as inner:
            names=[n for n in inner.namelist() if re.search(r'deep_byte_ranges\d+\.csv$',n)]
            assert len(names)==1,(info.filename,names)
            name=names[0];raw=inner.read(name);rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))));pos=0;counts=collections.Counter()
            for i,r in enumerate(rows):
                a=int(r['start_inclusive'],16);end=int(r['end_inclusive'],16)+1
                assert a==pos and end>a and end<=len(b) and end-a==int(r['bytes']),(info.filename,i,'bounds')
                assert sha(b[a:end])==r['range_sha256'],(info.filename,i,'range hash')
                counts[r['status']]+=end-a;pos=end
            assert pos==len(b)
            dest=source/(Path(info.filename).stem+'.csv');dest.write_bytes(raw)
            raw_ledgers[info.filename]=raw
            manifests=[n for n in inner.namelist() if 'manifest' in n.lower()]
            archives.append(dict(archive_member=info.filename,archive_sha256=sha(packed),ledger_member=name,ledger_sha256=sha(raw),intervals=len(rows),image_bytes_verified=pos,status_bytes=dict(counts),manifest_members=manifests))
            if m[1]=='320':assert baseline is None;baseline=rows;baseline_name=info.filename
assert baseline is not None and len(baseline)==1488
counts=collections.Counter()
for r in baseline:counts[r['status']]+=int(r['bytes'])
assert counts['NON-CODE PROVISIONAL']==57295
local=[]
for r in csv.DictReader(campaign.open(encoding='utf-8-sig')):local.append((int(r['start']),int(r['end_exclusive']),r))
assert local[0][0]==0 and local[-1][1]==len(b) and all(a[1]==c[0] for a,c in zip(local,local[1:]))
intersections=[];totals=collections.Counter();noncode=[]
for i,r in enumerate(baseline):
    if r['status']!='NON-CODE PROVISIONAL':continue
    a=int(r['start_inclusive'],16);end=int(r['end_inclusive'],16)+1
    noncode.append(dict(baseline_interval_id=i,start=a,end_exclusive=end,length=end-a,original_owner=r['owner'],original_status=r['status'],range_sha256=r['range_sha256'],historical_proof=r['proof'],reanalysis_status='UNKNOWN',semantic_type='UNRESOLVED',source_ledger_sha256=sha(raw_ledgers[baseline_name])))
    for la,le,lr in local:
        x,y=max(a,la),min(end,le)
        if x>=y:continue
        totals[lr['primary_type']]+=y-x
        intersections.append(dict(baseline_interval_id=i,start=x,end_exclusive=y,length=y-x,campaign_primary_type=lr['primary_type'],campaign_status=lr['status'],campaign_evidence=lr['evidence'],range_sha256=sha(b[x:y]),status='PARTIAL' if lr['status']=='PARTIAL' else 'UNKNOWN',scope='byte-range join only; original NON_CODE semantic correctness not presumed'))
assert sum(r['length'] for r in noncode)==57295 and sum(totals.values())==57295
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/(name+'.json')).write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
save('noncode_baseline',noncode);save('campaign_intersections',intersections)
(out/'archive_validations.json').write_text(json.dumps(archives,indent=2)+'\n',encoding='utf-8')
same={r['archive_member']:r['ledger_sha256']==sha(raw_ledgers[baseline_name]) for r in archives if any('PASS'+n+'_' in r['archive_member'] for n in ['319','320','321','322'])}
result=dict(archive=str(archive),archive_sha256=sha(archive.read_bytes()),image_sha256=sha(b),nested_archives_validated=len(archives),baseline_member=baseline_name,baseline_ledger_sha256=sha(raw_ledgers[baseline_name]),baseline_intervals=len(baseline),baseline_status_bytes=dict(counts),noncode_intervals=len(noncode),noncode_bytes=57295,noncode_join_current_campaign_bytes=dict(totals),pass319_322_byte_identical_ledgers=same,campaign_partition_sha256=sha(campaign.read_bytes()),generators_executed=False,manifest_presence_not_semantic_proof=True,reanalysis_complete=False,new_deep_verified_bytes=0,runtime_tests=0)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
