"""python export_guard_orientation_fields.py OUTPUTS"""
import csv,json,sys
from pathlib import Path
r=Path(sys.argv[1]);d=r/'guard_orientation_fields';d.mkdir(exist_ok=True)
items=[('record26',0,2,'selected frame WORD copied from class descriptor directional row'),('record26',15,1,'view helper flag:zero compares abs components;nonzero uses doubled-abs unsigned thresholds'),('record26',17,1,'facing code0..7 set by signed dx/dy; zero vector preserves'),('record26',18,1,'cached relative octant; equal plus lowforceBYTE0 skips frame update'),('record26',10,1,'strategy2 selects mode6 row04h rather than24h in DOS11+'),('record28',3,1,'lowBYTE of selected frame WORD'),('record28',4,1,'class index:nearDS pointer is WORD[3D22h+8*BYTE]'),('nearDS_class_descriptor',4,48,'three eight-WORD directional rows at+04h/+14h/+24h; header4B and producer open')]
with (d/'consumer_field_roles.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['record','offset','width','role','consumer']);w.writeheader()
 for record,offset,width,role in items:w.writerow(dict(record=record,offset=offset,width=width,role=role,consumer='04C7:00B0/012A and0AEA:0C0A;PARTIAL, native mode7 initialization plus controlled other modes'))
(d/'field_summary.json').write_text(json.dumps(dict(rows=len(items),original_NONCODE_bytes_added=0,new_deep_verified_bytes=0,status='PARTIAL'),indent=2)+'\n',encoding='utf-8')
