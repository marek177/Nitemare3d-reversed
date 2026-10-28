from pathlib import Path
import os,subprocess,json,concurrent.futures
root=Path.cwd();prior=json.loads((root/'pass2/evidence/validation.json').read_text())
def run(v):
 d=root/'pass3/evidence'/('DOS'+v);env=os.environ.copy();env['JAVA_HOME']='/workspace/scratch/1e1f47e04734/runtime/java/jdk-25.0.2'
 entries=','.join(next(x for x in prior if x['build']==v)['remaining_failures'])
 args=['/workspace/scratch/d559743f674a/runtime/ghidra_12.2_PUBLIC_20261016/support/analyzeHeadless',str(root/'pass3/projects'),'DOS'+v,'-process','DOS'+v+'.exe','-noanalysis','-scriptPath',str(root/'scripts'),'-postScript','N3DGuardedSwitchAudit.java',str(d/'switch_specs.tsv'),str(d/'switch_repair'),'-postScript','N3DPass3FullAudit.java',str(root/'pass3/audit'/('DOS'+v)),'-postScript','N3DResidualProbe.java',str(d/'residual'),entries,'-postScript','N3DFlowExport.java',str(root/'pass3/audit'/('DOS'+v)),'-max-cpu','2']
 with (root/'pass3'/('DOS'+v+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT)
 print(v,r.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['10','11','12','15','17','18']))
