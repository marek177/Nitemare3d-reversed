from pathlib import Path
import os,subprocess,concurrent.futures
root=Path.cwd()
def run(v):
 env=os.environ.copy();env['JAVA_HOME']=str(root/'runtime/jdk-25.0.2');d=root/'pass7/evidence'/('DOS'+v)
 args=[str(root/'runtime/ghidra_12.2_PUBLIC_20261016/support/analyzeHeadless'),str(root/'pass7/projects'),'DOS'+v,'-process','DOS'+v+'.exe','-noanalysis','-scriptPath',str(root/'scripts'),'-postScript','N3DBsfTypes.java',str(d/'types'),str(d/'type_spec.tsv'),'-postScript','N3DMultiRealModeProbe.java',str(root/'pass7/audit'/('DOS'+v)),str(d/'scope.tsv'),'-postScript','N3DFlowExport.java',str(root/'pass7/audit'/('DOS'+v)),'-max-cpu','2']
 with (root/'pass7'/('DOS'+v+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT)
 print(v,r.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['10','11','12','15','17','18']))
