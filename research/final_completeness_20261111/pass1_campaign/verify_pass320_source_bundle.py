"""Validate supplied PASS320 source bundle, without executing its generator."""
import hashlib,json,sys,zipfile
from pathlib import Path
p,out=map(Path,sys.argv[1:]);out.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(p) as z:
    prefix='Nitemare3D_PASS320_bundle/'
    manifest=z.read(prefix+'MANIFEST_SHA256.txt').decode('utf-8')
    checks=[]
    for line in manifest.splitlines():
        if not line.strip():continue
        expected,name=line.split(None,1);name=name.strip().lstrip('*')
        actual=sha(z.read(prefix+name));assert actual==expected
        checks.append(dict(member=name,sha256=actual))
    source=z.read(prefix+'podklady/build_pass320.py').decode('utf-8')
    assert "shutil.copy(prior,O/'deep_byte_ranges320.csv')" in source
    assert "N3D_PASS319_INT63_ALIAS_WRITES_FLAGS/deep_byte_ranges319.csv" in source
    ledger=[n for n in z.namelist() if n.lower().endswith('.csv')]
    result=dict(archive=str(p),archive_sha256=sha(p.read_bytes()),manifest_verified=checks,csv_members=ledger,generator_executed=False,ledger_operation='unchanged copy from PASS319',required_missing_predecessor='N3D_PASS319_INT63_ALIAS_WRITES_FLAGS/deep_byte_ranges319.csv',original_1488_intervals_verified=False,original_noncode_57295_boundaries_verified=False,scope='manifest and generator source lineage only; source assertions not executed')
(out/'source_lineage.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
