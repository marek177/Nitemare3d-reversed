"""python acquire_dosboxx_windows.py WORKDIR METADATA_OUT"""
import hashlib,json,sys,urllib.request,zipfile
from pathlib import Path
work,out=map(lambda x:Path(x).resolve(),sys.argv[1:]);work.mkdir(parents=True,exist_ok=True);out.parent.mkdir(parents=True,exist_ok=True)
url='https://github.com/joncampbell123/dosbox-x/releases/download/dosbox-x-v2026.10.01/dosbox-x-vsbuild-win64-2026.10.01-portable.zip';archive=work/'dosbox-x-vsbuild-win64-2026.10.01-portable.zip';expected='3c50915e63aefe35777d65ebb4391a06b4a2c2342e4c75cbee6bbda4c6916e33'
raw=archive.read_bytes() if archive.exists() else urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex-N3D-evidence-audit'}),timeout=60).read();assert len(raw)==44575207 and hashlib.sha256(raw).hexdigest()==expected;archive.write_bytes(raw)
dest=work/'dosboxx-win64-20261001';dest.mkdir(exist_ok=True);files=[]
with zipfile.ZipFile(archive) as z:
    for name in ('dosbox-x.exe','README.txt','dosbox-x.reference.conf','dosbox-x.reference.full.conf'):
        data=z.read('bin/x64/Release SDL2/'+name);(dest/name).write_bytes(data);files.append(dict(name=name,path=str(dest/name),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
result=dict(release='dosbox-x-v2026.10.01',release_url='https://github.com/joncampbell123/dosbox-x/releases/tag/dosbox-x-v2026.10.01',archive_url=url,archive_sha256=expected,archive_bytes=len(raw),files=files,scope='portable official Windows SDL2 files only; no installer or driver installation')
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(release=result['release'],archive_sha256=expected,files=len(files))))
