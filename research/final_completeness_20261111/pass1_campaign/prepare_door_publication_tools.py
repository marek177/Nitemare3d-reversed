"""python prepare_door_publication_tools.py OUTPUTS; prepare fresh delta wrapper."""
import sys
from pathlib import Path
r=Path(sys.argv[1]);s=(r/'prepare_guard_validator_publication_20261112.py').read_text(encoding='utf-8')
s=s.replace('publication_guard_validator_20261112','publication_door_interaction_20261112').replace('publication_remote_snapshot_guard_validator_20261112','publication_remote_snapshot_door_interaction_20261112')
needle="raw=readme.encode('utf-8');"
s=s.replace(needle,"readme = '# Latest batch: whole door interaction and real DOS version difference\\n\\nSee [DOOR_INTERACTION_REPORT.md](DOOR_INTERACTION_REPORT.md). Native whole original0598 call proves source door7 and neighbor6 state1-to2 with exact2BYTE world delta and unchanged57392B DGROUP. Original-code replay matches final registers/data without executed stubs.8192 DOS2 controlled cases/all126 instruction starts;64 separate cross-version cases prove early DOS10/11/12 propagate state4 while15/17/18/19/20 return early. Catalogue151 functions/16208 instruction bytes/1021881 DOS2 controlled cases/28 native scenarios. PASS1 unchanged; no new DEEP bytes. Prior sections are historical.\\n\\n' + readme\n"+needle)
(r/'prepare_door_interaction_publication_20261112.py').write_text(s,encoding='utf-8')
p=r/'render_campaign_status.py';s=p.read_text(encoding='utf-8').replace("else 'GUARD_VALIDATOR_REPORT.md'","else 'DOOR_INTERACTION_REPORT.md'")
needle="receipt_path=root/'CAMPAIGN_GUARD_VALIDATOR_PUBLICATION_RECEIPT_20261112.json'"
if "receipt_path=root/'CAMPAIGN_DOOR_INTERACTION_PUBLICATION_RECEIPT_20261112.json'" not in s:s=s.replace(needle,"receipt_path=root/'CAMPAIGN_DOOR_INTERACTION_PUBLICATION_RECEIPT_20261112.json'\nif not receipt_path.exists():"+needle,1)
p.write_text(s,encoding='utf-8')
