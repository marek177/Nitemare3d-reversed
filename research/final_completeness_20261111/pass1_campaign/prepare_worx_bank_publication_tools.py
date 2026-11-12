"""python prepare_worx_bank_publication_tools.py OUTPUTS"""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'prepare_classification_publication_20261112.py').read_text(encoding='utf-8')
s=s.replace('publication_classification_20261112','publication_worx_bank_20261112').replace('publication_remote_snapshot_classification_20261112','publication_remote_snapshot_worx_bank_20261112')
needle="raw=readme.encode('utf-8');"
s=s.replace(needle,"readme = '# Latest batch: remaining-reference context and WORX register bank\\n\\nSee [WORX_REGISTER_BANK_REPORT.md](WORX_REGISTER_BANK_REPORT.md). Raw1812D mask-reference candidate lies across sound-bank record boundaries; original128x11 loader/consumer validated.6166 controlled calls cover five functions, two previously owned helpers retained without duplicate count. Three new functions140instructions/283B,1435new filedataB outside originalNONCODE.40DOS CFG/normalized comparisons and8whole-bank byte matches. Catalogue157functions/16840instructionB/59469filedataB/1029235controlled executions,29native scenarios. No native audio test added; PASS1 unchanged,DEEP0. Prior sections historical.\\n\\n' + readme\n"+needle)
(r/'prepare_worx_bank_publication_20261112.py').write_text(s,encoding='utf-8')
p=r/'render_campaign_status.py';s=p.read_text(encoding='utf-8').replace("else 'CLASSIFICATION_PRODUCERS_REPORT.md'","else 'WORX_REGISTER_BANK_REPORT.md'")
needle="receipt_path=root/'CAMPAIGN_CLASSIFICATION_PUBLICATION_RECEIPT_20261112.json'"
if "receipt_path=root/'CAMPAIGN_WORX_BANK_PUBLICATION_RECEIPT_20261112.json'" not in s:s=s.replace(needle,"receipt_path=root/'CAMPAIGN_WORX_BANK_PUBLICATION_RECEIPT_20261112.json'\nif not receipt_path.exists():"+needle,1)
p.write_text(s,encoding='utf-8')
