from pathlib import Path
import subprocess,os,concurrent.futures
root=Path.cwd()
def run(v):
 env=os.environ.copy();env['JAVA_HOME']='/workspace/scratch/1e1f47e04734/runtime/java/jdk-25.0.2'
 a=['/workspace/scratch/d559743f674a/runtime/ghidra_12.2_PUBLIC_20261016/support/analyzeHeadless',str(root/'pass2/projects'),'DOS'+v,'-process','DOS'+v+'.exe','-noanalysis','-scriptPath',str(root/'scripts'),'-postScript','N3DFlowExport.java',str(root/'pass2/audit'/('DOS'+v))]
 with (root/'pass2'/('flow_DOS'+v+'.log')).open('w') as f:r=subprocess.run(a,env=env,stdout=f,stderr=subprocess.STDOUT)
 print(v,r.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['10','11','12','15','17','18']))
