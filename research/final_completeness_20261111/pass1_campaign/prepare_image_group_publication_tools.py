"""python prepare_image_group_publication_tools.py OUTPUTS"""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'prepare_guard_orientation_publication_20261112.py').read_text(encoding='utf-8')
s=s.replace('publication_guard_orientation_20261112','publication_image_group_20261112').replace('publication_remote_snapshot_guard_orientation_20261112','publication_remote_snapshot_image_group_20261112')
needle="raw=readme.encode('utf-8');"
s=s.replace(needle,"readme = '# Latest batch: IMG90 descriptors and native class-bank provenance\\n\\nSee [IMAGE_GROUP_DESCRIPTOR_REPORT.md](IMAGE_GROUP_DESCRIPTOR_REPORT.md). Whole0277:0584wrapper1464controlledcases,uncheckedshortread preserved. Native0277:09C1..09D7 copies90B IMG1 object81h descriptor file8F5Ah toDSF200h, binds class8fourWORDrecord and prior52B frame consumer; copy block not wholemaploader.1536headers/116aliasgroups across3episodes,allaliasheaders equal. DOS10separatewall/object decoder ABI differs from laterunified decoder;144separatecontrolledcases,no decoder-output parity. Catalogue161functions/17629instructionB/1040549DOS2executions/31native scenarios/BSS5088B. PASS1 unchanged,DEEP0. Prior sections historical.\\n\\n' + readme\n"+needle)
(r/'prepare_image_group_publication_20261112.py').write_text(s,encoding='utf-8')
p=r/'render_campaign_status.py';s=p.read_text(encoding='utf-8').replace("else 'GUARD_ORIENTATION_REPORT.md'","else 'IMAGE_GROUP_DESCRIPTOR_REPORT.md'")
needle="receipt_path=root/'CAMPAIGN_GUARD_ORIENTATION_PUBLICATION_RECEIPT_20261112.json'"
if "receipt_path=root/'CAMPAIGN_IMAGE_GROUP_PUBLICATION_RECEIPT_20261112.json'" not in s:s=s.replace(needle,"receipt_path=root/'CAMPAIGN_IMAGE_GROUP_PUBLICATION_RECEIPT_20261112.json'\nif not receipt_path.exists():"+needle,1)
p.write_text(s,encoding='utf-8')
