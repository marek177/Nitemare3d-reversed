from pathlib import Path
import json,zipfile,functools,operator,hashlib
root=Path(__file__).resolve().parent.parent;z=zipfile.ZipFile(root/'inputs/all-nite3d.zip');out=[]
for r in json.loads((root/'pass7/evidence/bsf_resources.json').read_text()):
 base=r['source'].rsplit('/',1)[0];h=bytes.fromhex(r['header_hex'])
 for name,field in [('n3d.exe',1),('map.1',2)]:
  path=next(p for p in z.namelist() if p.lower()==(base+'/'+name).lower());b=z.read(path);value=functools.reduce(operator.xor,b,0x7b);assert value==h[field];out.append(dict(build=r['build'],source=path,sha256=hashlib.sha256(b).hexdigest(),expected=h[field],xor_7b=value,last_byte=b[-1],passed=True))
(root/'pass7/evidence/header_file_checksums.json').write_text(json.dumps(out,indent=2));print(len(out),'file checksum comparisons passed')
