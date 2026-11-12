"""python prepare_guard_orientation_publication_tools.py OUTPUTS"""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'prepare_worx_bank_publication_20261112.py').read_text(encoding='utf-8')
s=s.replace('publication_worx_bank_20261112','publication_guard_orientation_20261112').replace('publication_remote_snapshot_worx_bank_20261112','publication_remote_snapshot_guard_orientation_20261112')
needle="raw=readme.encode('utf-8');"
s=s.replace(needle,"readme = '# Latest batch: original GUARD facing and relative frame selection\\n\\nSee [GUARD_ORIENTATION_REPORT.md](GUARD_ORIENTATION_REPORT.md). Original00B0 sets facing rather than coordinates; original012A+C0A selects relative directional frame.4666 no-stub controlled cases plus5184 movement+validator+facing cases. Native GUARD0/actor20 mode7 selects relative2/frame0400h with captured nearDSF200bank52B and exact2BYTE world delta; preliminary capture without bank is not counted. DOS10mode6strategy2 row24h versus laterrow04h proved256 separate version cases. Catalogue160functions/17373instructionB/1039085DOS2executions/30native scenarios. PASS1 unchanged, DEEP0. Prior sections historical.\\n\\n' + readme\n"+needle)
(r/'prepare_guard_orientation_publication_20261112.py').write_text(s,encoding='utf-8')
p=r/'render_campaign_status.py';s=p.read_text(encoding='utf-8').replace("else 'WORX_REGISTER_BANK_REPORT.md'","else 'GUARD_ORIENTATION_REPORT.md'")
needle="receipt_path=root/'CAMPAIGN_WORX_BANK_PUBLICATION_RECEIPT_20261112.json'"
if "receipt_path=root/'CAMPAIGN_GUARD_ORIENTATION_PUBLICATION_RECEIPT_20261112.json'" not in s:s=s.replace(needle,"receipt_path=root/'CAMPAIGN_GUARD_ORIENTATION_PUBLICATION_RECEIPT_20261112.json'\nif not receipt_path.exists():"+needle,1)
p.write_text(s,encoding='utf-8')
