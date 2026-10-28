from pathlib import Path
import subprocess,os,concurrent.futures
root=Path.cwd()
def run(v):
 env=os.environ.copy();env['JAVA_HOME']='/workspace/scratch/1e1f47e04734/runtime/java/jdk-25.0.2';d=root/'pass5/evidence'/('DOS'+v)
 args=['/workspace/scratch/1e1f47e04734/runtime/ghidra/ghidra_12.2_PUBLIC_20261016/support/analyzeHeadless',str(root/'pass5/projects'),'DOS'+v,'-process','DOS'+v+'.exe','-noanalysis','-scriptPath',str(root/'scripts'),'-postScript','N3DMultiScopeEvidence.java',str(d/'scope_audit'),str(d/'scope.tsv'),'-postScript','N3DFlowExport.java',str(root/'pass5/audit'/('DOS'+v))]
 with (root/'pass5'/('verify_DOS'+v+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT)
 print(v,r.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['10','11','12','15','17','18']))
