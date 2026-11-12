"""python export_door_field_roles.py OUTPUTS; consumer evidence, not whole record closure."""
import csv,json,sys
from pathlib import Path
r=Path(sys.argv[1]);d=r/'door_interaction_fields';d.mkdir(exist_ok=True)
rows=[dict(record=record,offset=off,width=width,role=role,consumer='0000:0598..0704; PARTIAL, controlled whole function and native state1to2 only') for record,off,width,role in [('record18_door',2,2,'second near DS descriptor pointer, flag+5 marked on state3'),('descriptor_near_DS',1,1,'direction value compared for kinds3Dh/3Eh'),('descriptor_near_DS',5,1,'bit01h OR on source/neighbor state3 branch'),('record18_door',16,1,'request cleared only state0/2 branch; retained state1/3 branch')]]
with (d/'consumer_field_roles.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(d/'summary.json').write_text(json.dumps(dict(field_evidence_rows=4,original_NONCODE_bytes_added=0,new_deep_verified_bytes=0,status='PARTIAL'),indent=2)+'\n',encoding='utf-8')
