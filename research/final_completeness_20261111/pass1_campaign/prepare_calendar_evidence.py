"""OUTPUTS IMAGE INVENTORY DECODER: retain the caller/month provenance and version audit."""
import csv,hashlib,json,sys
from pathlib import Path
r,image,inventory,decoder=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};fmt=Formatter(FormatterSyntax.INTEL);o=r/'crt_calendar_fields';o.mkdir(exist_ok=True)
def save(name,rows):
 with (o/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rows=[]
for lo,hi in ((0x2b3f,0x2b82),(0x2b9d,0x2bb9),(0x3a0a,0x3a23),(0x3a24,0x3a3d)):
 for ins in Decoder(16,b[0x11ee0+lo:0x11ee0+hi],ip=lo):
  p=0x11ee0+ins.ip;raw=b[p:p+ins.len];assert old[p]['bytes']==raw.hex()
  rows.append(dict(cs=0x11ee,ip=ins.ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(ins)))
save('month_provenance_instructions',rows)
roles=[]
for off,role in [(4,'hour WORD;used for boundary-hour comparison'),(8,'month WORD zero-based;3/9 boundaries'),(10,'year WORD relative1900;gate67,rule branch86'),(14,'day-of-year WORD;compared to computed boundary')]:
 roles.append(dict(record='calendar_tm_like_partial',offset=off,width=2,role=role,consumer='11EE:2D00;PARTIAL,not full struct tm'))
save('consumer_field_roles',roles)
summary=dict(month_provenance='DOS-date wrapper AH2A stores DH at date+1; caller zero-extends that BYTE and passes unchanged month to2DC0. Native month11 observed; normal1..12 domain in replay is explicit,not validated by converter.',remaining_leap_interval_start=0x29b7e,remaining_leap_interval_end_exclusive=0x29b98,leap_status='CLASSIFIED ONLY',normal_converter_lookup_range_start=0x29b98,normal_converter_lookup_range_end_exclusive=0x29bb0,zero_month_would_read_last_leap_WORD=True,status_changes=0,new_deep_verified_bytes=0,files=[dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (image,inventory,Path(__file__))])
(o/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
s=(r/'audit_image_record_versions.py').read_text(encoding='utf-8').replace('audit_image_record_versions.py','audit_crt_calendar_versions.py')
s=s.replace("('558bec566a0a66ff7606','c80200005756803e','c8040000578b7e068a4501')","('558bec83ec0457568b7606837c0a43','558bec83ec1657568b76068b5e08','558bec535733ff8b46080bc0')")
s=s.replace("refcs=0x768 if f['name']=='image_record_tag_XMS_offset' else 0x277","refcs=0x11ee").replace('DOS10split not forced to unified function','calendar/remainder counterparts bounded by retained owners; no timezone-configuration equivalence')
(r/'audit_crt_calendar_versions.py').write_text(s,encoding='utf-8')
