from pathlib import Path
import os,subprocess,concurrent.futures
root=Path.cwd()
def run(v):
 env=os.environ.copy();env['JAVA_HOME']='/workspace/scratch/1e1f47e04734/runtime/java/jdk-25.0.2'
 args=['/workspace/scratch/1e1f47e04734/runtime/ghidra/ghidra_12.2_PUBLIC_20261016/support/analyzeHeadless',str(root/'pass6/projects'),'DOS'+v,'-process','DOS'+v+'.exe','-noanalysis','-scriptPath',str(root/'scripts'),'-postScript','N3DMultiABIFix.java',str(root/'pass6/evidence'/('DOS'+v)/'abi_fix'),str(root/'pass6/evidence'/('DOS'+v)/'abi_spec.tsv'),'-postScript','N3DMultiRealModeProbe.java',str(root/'pass6/audit'/('DOS'+v)),str(root/'pass6/evidence'/('DOS'+v)/'scope.tsv'),'-postScript','N3DFlowExport.java',str(root/'pass6/audit'/('DOS'+v)),'-max-cpu','2']
 with (root/'pass6'/('DOS'+v+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT)
 print(v,r.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['10','11','12','15','17','18']))
