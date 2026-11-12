"""Derive this batch publication/render wrappers from retained prior versions."""
from pathlib import Path
import sys
r=Path(sys.argv[1]);p=r/'prepare_guard_move_publication_20261112.py';s=p.read_text(encoding='utf-8')
s=s.replace('publication_guard_move_20261112','publication_guard_validator_20261112').replace('publication_remote_snapshot_guard_move_20261112','publication_remote_snapshot_guard_validator_20261112')
needle="raw=readme.encode('utf-8');"
s=s.replace(needle,"readme = '# Latest batch: original GUARD validator and door predicates\\n\\nSee [GUARD_VALIDATOR_REPORT.md](GUARD_VALIDATOR_REPORT.md). Four newly bounded functions, 10472 controlled cases without failure, one sparse native allowed/blocked return scenario. Catalogue150 functions/15846 instruction bytes/1013689 controlled cases/27 native scenarios; BSS tables4566 bytes. PASS1 unchanged: PARTIAL57118, CLASSIFIED ONLY149, UNKNOWN28, DEEP0. Two 256-byte classification tables are BSS, not new original NONCODE coverage. Blocked snapshot door7 state2 does not establish its entry state or interaction transition. Prior sections below are historical.\\n\\n' + readme\n"+needle)
(r/'prepare_guard_validator_publication_20261112.py').write_text(s,encoding='utf-8')
p=r/'render_campaign_status.py';s=p.read_text(encoding='utf-8').replace("else 'GUARD_MAP_WRITER_REPORT.md'","else 'GUARD_VALIDATOR_REPORT.md'")
s=s.replace("receipt_path=root/'CAMPAIGN_GUARD_MOVE_PUBLICATION_RECEIPT_20261112.json'","receipt_path=root/'CAMPAIGN_GUARD_VALIDATOR_PUBLICATION_RECEIPT_20261112.json'\nif not receipt_path.exists():receipt_path=root/'CAMPAIGN_GUARD_MOVE_PUBLICATION_RECEIPT_20261112.json'")
lines=s.splitlines()
for i,line in enumerate(lines):
 if line.startswith('latest=(root/report)'):
  lines[i]="latest=(root/report).read_text(encoding='utf-8');table=latest[latest.index('## Coverage update: 13 areas'):latest.index('## Required next runtime tests')]"
p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
import json
p=r/'publication_remote_snapshot_guard_validator_20261112.json';d=json.loads(p.read_text(encoding='utf-8'));prefix=d['prefix']
d['files']=[dict(x,path=x['path'][len(prefix):] if x['path'].startswith(prefix) else x['path']) for x in d['files'] if x['path'].startswith(prefix) or not x['path'].startswith('research/')]
p.write_text(json.dumps(d),encoding='utf-8')
