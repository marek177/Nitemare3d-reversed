"""OUTPUTS: ftime record roles,BSS cache evidence and DOS counterpart audit."""
import csv,hashlib,sys
from pathlib import Path
r=Path(sys.argv[1]);o=r/'crt_ftime_fields';o.mkdir(exist_ok=True);work=r.parent/'work/dosboxx_ftime_runtime_v2'
def save(name,rows):
 with (o/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
roles=[]
for record,off,width,role in [('timeb10',0,4,'DWORD calendar seconds,32-bit wrap'),('timeb10',4,2,'WORD milliseconds=10*DOS hundredths'),('timeb10',6,2,'signed WORD timezone minutes,truncate seconds/60 then lowWORD'),('timeb10',8,2,'WORD DST predicate flag0/1,gated by daylight enable'),('DOS_date5',0,1,'day BYTE from DL'),('DOS_date5',1,1,'month BYTE from DH'),('DOS_date5',2,2,'year WORD from CX'),('DOS_date5',4,1,'weekday BYTE from AL'),('DOS_time4',0,1,'hour BYTE from CH'),('DOS_time4',1,1,'minute BYTE from CL'),('DOS_time4',2,1,'second BYTE from DH'),('DOS_time4',3,1,'hundredths BYTE from DL'),('game_clock_scratch14',10,4,'outside10B ftime output;native stale tail preserved,not a defined timeb member')]:
 roles.append(dict(record=record,offset=off,width=width,role=role,consumer='original11EE2AEA/3A0A/3A24 and0BDE0018;PARTIAL'))
save('consumer_field_roles',roles)
raw=(work/'ftime_00_DS64_after.bin').read_bytes()[0x3ca8:0x3caa];assert raw==b'\x01\x00'
save('external_bss_tables',[dict(name='crt_timezone_cached_initialized',ds_start=0x3ca8,ds_end_exclusive=0x3caa,image_start=0x27710+0x3ca8,image_end_exclusive=0x27710+0x3caa,length=2,type='WORD cold-init gate,0to1 native;original2BF4 tests and increments',status='PARTIAL',runtime_sha256=hashlib.sha256(raw).hexdigest(),outside_original_file_image=True,original_NONCODE_bytes_added=0)])
s=(r/'audit_image_record_versions.py').read_text(encoding='utf-8').replace('audit_image_record_versions.py','audit_crt_ftime_versions.py')
s=s.replace("('558bec566a0a66ff7606','c80200005756803e','c8040000578b7e068a4501')","('558bec83ec2256','558becb42acd21','558becb42ccd218b5e06882f884f01887702')").replace("refcs=0x768 if f['name']=='image_record_tag_XMS_offset' else 0x277","refcs=0x11ee").replace('DOS10split not forced to unified function','ftime/date/time counterparts bounded by retained owners; no OS/timezone equivalence')
(r/'audit_crt_ftime_versions.py').write_text(s,encoding='utf-8')
