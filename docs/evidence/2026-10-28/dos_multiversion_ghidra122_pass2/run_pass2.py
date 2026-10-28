from pathlib import Path
import os,subprocess,concurrent.futures
root=Path.cwd()
def run(v):
 d=root/'pass2/evidence'/('DOS'+v);env=os.environ.copy();env['JAVA_HOME']='/workspace/scratch/1e1f47e04734/runtime/java/jdk-25.0.2'
 args=['/workspace/scratch/d559743f674a/runtime/ghidra_12.2_PUBLIC_20261016/support/analyzeHeadless',str(root/'pass2/projects'),'DOS'+v,'-process','DOS'+v+'.exe','-noanalysis','-scriptPath',str(root/'scripts'),'-postScript','N3DGuardedSwitchAudit.java',str(d/'switch_specs.tsv'),str(d/'switch_repair'),'-postScript','N3DNearRepair.java',str(d/'near_specs.tsv'),str(d/'near_repairs.tsv'),'-postScript','N3DPass2FullAudit.java',str(root/'pass2/audit'/('DOS'+v)),'-max-cpu','2']
 with (root/'pass2'/('DOS'+v+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT)
 print(v,r.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['10','11','12','15','17','18']))
