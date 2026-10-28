from pathlib import Path
import os,json,subprocess,concurrent.futures
root=Path.cwd()
def run(v):
 d=root/'pass4/evidence'/('DOS'+v);b=json.loads((d/'boundary.json').read_text());env=os.environ.copy();env['JAVA_HOME']='/workspace/scratch/1e1f47e04734/runtime/java/jdk-25.0.2'
 args=['/workspace/scratch/d559743f674a/runtime/ghidra_12.2_PUBLIC_20261016/support/analyzeHeadless',str(root/'pass4/projects'),'DOS'+v,'-process','DOS'+v+'.exe','-noanalysis','-scriptPath',str(root/'scripts'),'-postScript','N3DPass4Repair.java',str(d/'repair'),str(d/'flow_specs.tsv'),b['start'],b['end'],b['function'],'-postScript','N3DFunctionExport.java',str(root/'pass4/audit'/('DOS'+v)),'-postScript','N3DFlowExport.java',str(root/'pass4/audit'/('DOS'+v)),'-max-cpu','2']
 with (root/'pass4'/('repair_full_DOS'+v+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT)
 print(v,r.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['15','18']))
