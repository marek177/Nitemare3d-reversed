"""Read-only ZIP central-directory search; bounded nested ZIP inspection.
Usage: python search_pass_archives.py OUT_DIR ROOT [ROOT ...]
No archive members are executed or extracted to disk.
"""
import csv,io,json,os,re,sys,zipfile
from pathlib import Path

def main():
    out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
    roots=list(map(Path,sys.argv[2:]));stats=dict(archives=0,members=0,nested_archives=0)
    matches=[];errors=[];skipped=[];archives=[]
    prune={'.git','node_modules','.venv','venv','__pycache__','site-packages','work'}
    pattern=re.compile(r'pass[ _-]*0*(319|320|321)|deep.?byte|non.?code|byte.?ranges|byte.?coverage|classification|classified.?ranges',re.I)
    def inspect(source,label,depth):
        try:
            with zipfile.ZipFile(source) as z:
                stats['archives']+=1;items=z.infolist();stats['members']+=len(items)
                archives.append(dict(path=label,depth=depth,members=len(items)))
                for item in items:
                    name=item.filename
                    if pattern.search(name):matches.append(dict(archive=label,member=name,size=item.file_size,crc32='%08x'%item.CRC,depth=depth))
                    if name.lower().endswith('.zip'):
                        if depth>=32 or item.file_size>32*1024*1024:
                            skipped.append(dict(archive=label,member=name,size=item.file_size,reason='depth>=32 or uncompressed size>32MiB'));continue
                        stats['nested_archives']+=1
                        inspect(io.BytesIO(z.read(item)),label+'::'+name,depth+1)
        except Exception as e:errors.append(dict(path=label,error=repr(e)))
    seen=set()
    for root in roots:
        if root.is_file():paths=[root]
        else:
            paths=[]
            for base,dirs,files in os.walk(root,onerror=lambda e:errors.append(dict(path=str(root),error=repr(e)))):
                dirs[:]=[d for d in dirs if d not in prune]
                paths.extend(Path(base)/n for n in files if n.lower().endswith('.zip'))
        for p in paths:
            key=str(p.resolve()).lower()
            if key not in seen:seen.add(key);inspect(p,str(p),0)
    for name,rows,fields in [('matches',matches,['archive','member','size','crc32','depth']),('archives',archives,['path','depth','members']),('skipped',skipped,['archive','member','size','reason']),('errors',errors,['path','error'])]:
        with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    result=dict(roots=list(map(str,roots)),statistics=stats,matches=len(matches),errors=len(errors),skipped_nested=len(skipped),scope='ZIP member-name search only; nested <=32MiB and depth<=32; no content-wide negative claim')
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
