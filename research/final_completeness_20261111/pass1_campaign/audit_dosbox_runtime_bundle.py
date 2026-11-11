"""python audit_dosbox_runtime_bundle.py ZIP OUT; read-only bundle/environment probe."""
import csv,hashlib,json,shutil,struct,subprocess,sys,zipfile
from pathlib import Path
p,out=map(Path,sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();rows=[];exe=[]
with zipfile.ZipFile(p) as z:
    for i in z.infolist():
        if i.is_dir():continue
        data=z.read(i) # zipfile checks member CRC
        rows.append(dict(name=i.filename,length=len(data),sha256=sha(data),crc32='%08x'%i.CRC))
        if data[:4]==b'\x7fELF':exe.append(dict(name=i.filename,elf_class=data[4],elf_endianness=data[5],elf_machine=struct.unpack_from('<H',data,18)[0]))
probes={}
for args in [['wsl.exe','--list','--quiet'],['wsl.exe','--status']]:
    try:
        r=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
        def dec(b):return b.decode('utf-16-le' if b'\0' in b else 'utf-8',errors='replace')
        probes[' '.join(args)]={'exit_code':r.returncode,'stdout':dec(r.stdout),'stderr':dec(r.stderr)}
    except (OSError,subprocess.TimeoutExpired) as e:probes[' '.join(args)]={'error':str(e)}
out.mkdir(parents=True,exist_ok=True)
with (out/'members.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(zip_path=str(p),zip_length=p.stat().st_size,zip_sha256=sha(p.read_bytes()),verified_file_members=len(rows),elf_members=exe,windows_dosbox_on_path={n:shutil.which(n) for n in ['dosbox-x.exe','dosbox.exe']},environment_probes=probes,original_game_runtime_tests=0,bundle_instructions_executed=False)
(out/'summary.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(s,ensure_ascii=True,indent=2))
