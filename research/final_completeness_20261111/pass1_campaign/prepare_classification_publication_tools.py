"""python prepare_classification_publication_tools.py OUTPUTS"""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'prepare_door_interaction_publication_20261112.py').read_text(encoding='utf-8')
s=s.replace('publication_door_interaction_20261112','publication_classification_20261112').replace('publication_remote_snapshot_door_interaction_20261112','publication_remote_snapshot_classification_20261112')
needle="raw=readme.encode('utf-8');"
s=s.replace(needle,"readme = '# Latest batch: MAP classification producers and omitted RTC target\\n\\nSee [CLASSIFICATION_PRODUCERS_REPORT.md](CLASSIFICATION_PRODUCERS_REPORT.md). Two original no-argument table generators retain local bit80h;1088 controlled calls check278528 entries. Separate native run verifies MAP1header514B identity and512generated flags with inherited seeds0/7. Second call additionally has cached clockDWORD+1; original RTC handler identified and controlled-tested100cases, but native writerPC is not captured. Handler20instruction starts were absent from old inventory and outside original NONCODE.24DOS CFG/normalized comparisons match. Catalogue154functions/16557instructionB/1023069DOS2cases/29native scenarios/BSS5080B. PASS1 unchanged, DEEP0. Prior sections are historical.\\n\\n' + readme\n"+needle)
(r/'prepare_classification_publication_20261112.py').write_text(s,encoding='utf-8')
p=r/'render_campaign_status.py';s=p.read_text(encoding='utf-8').replace("else 'DOOR_INTERACTION_REPORT.md'","else 'CLASSIFICATION_PRODUCERS_REPORT.md'")
needle="receipt_path=root/'CAMPAIGN_DOOR_INTERACTION_PUBLICATION_RECEIPT_20261112.json'"
if "receipt_path=root/'CAMPAIGN_CLASSIFICATION_PUBLICATION_RECEIPT_20261112.json'" not in s:s=s.replace(needle,"receipt_path=root/'CAMPAIGN_CLASSIFICATION_PUBLICATION_RECEIPT_20261112.json'\nif not receipt_path.exists():"+needle,1)
p.write_text(s,encoding='utf-8')
