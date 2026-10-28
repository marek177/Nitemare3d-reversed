from pathlib import Path
import csv,json,struct,shutil,os,subprocess,concurrent.futures
root=Path(__file__).resolve().parent.parent;pr=root/'pass20/projects';pr.mkdir(parents=True,exist_ok=True)
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];shutil.copy2(root/'pass19/projects'/('DOS'+v+'.gpr'),pr/('DOS'+v+'.gpr'));shutil.copytree(root/'pass19/projects'/('DOS'+v+'.rep'),pr/('DOS'+v+'.rep'),dirs_exist_ok=True)
 scan=next(x for x in json.loads((root/'pass20/evidence/original_scanf.json').read_text())['locations'] if x['build']==v)['entry'];parser=next(x for x in json.loads((root/'pass19/evidence/bsf_commands.json').read_text())['locations'] if x['build']==v)['entry'];d=root/'pass20/audit'/('DOS'+v);d.mkdir(parents=True,exist_ok=True);(d/'type_spec.tsv').write_text('\t'.join([scan,parser]))
def run(v):
 d=root/'pass20/audit'/('DOS'+v);env=os.environ.copy();env['JAVA_HOME']=str(root/'runtime/jdk-25.0.2')
 args=[str(root/'runtime/ghidra_12.2_PUBLIC_20261016/support/analyzeHeadless'),str(pr),'DOS'+v,'-process','DOS'+v+'.exe','-noanalysis','-scriptPath',str(root/'scripts'),'-postScript','N3DBsfScanfTypes.java',str(d),str(d/'type_spec.tsv'),'-max-cpu','2']
 with (d/'ghidra.log').open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(v,r.returncode);assert (d/'typed_functions.tsv').exists(),v;print(v,'saved',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['10','11','12','15','17','18']))
