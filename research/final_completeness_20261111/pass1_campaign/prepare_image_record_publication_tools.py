"""python prepare_image_record_publication_tools.py OUTPUTS"""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'prepare_image_group_publication_20261112.py').read_text(encoding='utf-8')
s=s.replace('publication_image_group_20261112','publication_image_record_20261112').replace('publication_remote_snapshot_image_group_20261112','publication_remote_snapshot_image_record_20261112')
s=s.replace("folder.name!='campaign_catalog'","folder.name not in ('campaign_catalog','img_raw_records')")
needle="raw=readme.encode('utf-8');"
s=s.replace(needle,"readme = '# Latest batch: raw image records and original XMS tagging pipeline\\n\\nSee [IMAGE_RECORD_PIPELINE_REPORT.md](IMAGE_RECORD_PIPELINE_REPORT.md). Three original routines are raw loader/indexer/cache-tag adaptor,not pixel decompressors.728 component+3534 actual589group scenarios;1870raw assetrecords catalogued. Native firstwall128x64 pixels8192B match IMG1 and XMSsource/requestoffset0;used0to8/tag0/cachedwall+1/pointerclear. Currentmanagerreturn not trapped,prior identicalrequest AX1 proof rechecked;no XMSreadback/render parity.22of24version mappings compared,2DOS10 mappings remainUNKNOWN. Catalogue164functions/18121instructionB/1044811DOS2scenarios/32native/BSS5096B. PASS1 unchanged,DEEP0;original13area ledger preserved. Prior sections historical.\\n\\n' + readme\n"+needle)
(r/'prepare_image_record_publication_20261112.py').write_text(s,encoding='utf-8')
p=r/'render_campaign_status.py';s=p.read_text(encoding='utf-8').replace("else 'IMAGE_GROUP_DESCRIPTOR_REPORT.md'","else 'IMAGE_RECORD_PIPELINE_REPORT.md'")
needle="receipt_path=root/'CAMPAIGN_IMAGE_GROUP_PUBLICATION_RECEIPT_20261112.json'"
if "receipt_path=root/'CAMPAIGN_IMAGE_RECORD_PUBLICATION_RECEIPT_20261112.json'" not in s:s=s.replace(needle,"receipt_path=root/'CAMPAIGN_IMAGE_RECORD_PUBLICATION_RECEIPT_20261112.json'\nif not receipt_path.exists():"+needle,1)
p.write_text(s,encoding='utf-8')
