from pathlib import Path
import os,subprocess,concurrent.futures
root=Path.cwd()
def run(v):
 env=os.environ.copy();env['JAVA_HOME']='/workspace/scratch/1e1f47e04734/runtime/java/jdk-25.0.2'
 args=['/workspace/scratch/1e1f47e04734/runtime/ghidra/ghidra_12.2_PUBLIC_20261016/support/analyzeHeadless',str(root/'pass5/projects'),'DOS'+v,'-process','DOS'+v+'.exe','-noanalysis','-scriptPath',str(root/'scripts'),'-postScript','N3DMultiRealModeProbe.java',str(root/'pass5/audit'/('DOS'+v)),str(root/'pass5/evidence'/('DOS'+v)/'scope.tsv'),'-max-cpu','2']
 with (root/'pass5'/('DOS'+v+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT)
 print(v,r.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['10','11','12','15','17','18']))
