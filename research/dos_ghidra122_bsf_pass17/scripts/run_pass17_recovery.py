from pathlib import Path
import csv,json,struct,shutil,os,subprocess,concurrent.futures
root=Path(__file__).resolve().parent.parent;pr=root/'pass17/projects';pr.mkdir(parents=True,exist_ok=True)
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];shutil.copy2(root/'pass16/projects'/('DOS'+v+'.gpr'),pr/('DOS'+v+'.gpr'));shutil.copytree(root/'pass16/projects'/('DOS'+v+'.rep'),pr/('DOS'+v+'.rep'),dirs_exist_ok=True)
 entry=next(x for x in json.loads((root/'pass15/evidence/bsf_callers.json').read_text()) if x['build']==v)['dynamic_caller_entry'];d=root/'pass17/audit'/('DOS'+v);d.mkdir(parents=True,exist_ok=True);(d/'type_spec.tsv').write_text(entry)
def run(v):
 d=root/'pass17/audit'/('DOS'+v);env=os.environ.copy();env['JAVA_HOME']=str(root/'runtime/jdk-25.0.2')
 args=[str(root/'runtime/ghidra_12.2_PUBLIC_20261016/support/analyzeHeadless'),str(pr),'DOS'+v,'-process','DOS'+v+'.exe','-noanalysis','-scriptPath',str(root/'scripts'),'-postScript','N3DBsfViewerRecovery.java',str(d),str(d/'type_spec.tsv'),'-max-cpu','2']
 with (d/'ghidra.log').open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(v,r.returncode);assert (d/'inventory.tsv').exists(),v;print(v,'saved',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['10','11','12','15','17','18']))
