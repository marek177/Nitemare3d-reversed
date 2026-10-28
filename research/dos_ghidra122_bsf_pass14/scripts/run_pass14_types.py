from pathlib import Path
import csv,json,struct,shutil,os,subprocess,concurrent.futures
root=Path(__file__).resolve().parent.parent;pr=root/'pass14/projects';pr.mkdir(parents=True,exist_ok=True)
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];shutil.copy2(root/'pass7/projects'/('DOS'+v+'.gpr'),pr/('DOS'+v+'.gpr'));shutil.copytree(root/'pass7/projects'/('DOS'+v+'.rep'),pr/('DOS'+v+'.rep'),dirs_exist_ok=True)
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));cs,entry=[int(x,16) for x in q['loader_entry'].split(':')];fc=[r for r in rows if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<entry+0x98 and r['bytes'].startswith('9a')];values=[]
 for i in [2,4]:
  off,seg=struct.unpack_from('<HH',bytes.fromhex(fc[i]['bytes']),1);values.append(f'{seg:04x}:{off:04x}')
 d=root/'pass14/audit'/('DOS'+v);d.mkdir(parents=True,exist_ok=True);(d/'type_spec.tsv').write_text('\t'.join(values+[q['loader_entry']]))
def run(v):
 d=root/'pass14/audit'/('DOS'+v);env=os.environ.copy();env['JAVA_HOME']=str(root/'runtime/jdk-25.0.2')
 args=[str(root/'runtime/ghidra_12.2_PUBLIC_20261016/support/analyzeHeadless'),str(pr),'DOS'+v,'-process','DOS'+v+'.exe','-noanalysis','-scriptPath',str(root/'scripts'),'-postScript','N3DAllocatorSeekTypes.java',str(d),str(d/'type_spec.tsv'),'-max-cpu','2']
 with (d/'ghidra.log').open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(v,r.returncode);assert (d/'typed_functions.tsv').exists(),v;print(v,'saved',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['10','11','12','15','17','18']))
