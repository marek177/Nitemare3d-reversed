"""Rebuild field-role CSV and integrate independently checked validator evidence."""
import csv,json,sys
from pathlib import Path
r=Path(sys.argv[1]);p=r/'independent_decode_and_catalog.py';s=p.read_text(encoding='utf-8')
s=s.replace("'palette_effect_replay','guard_cell_move_replay'):","'palette_effect_replay','guard_cell_move_replay','guard_validator_replay'):")
s=s.replace("'palette_effect_replay','guard_cell_move_replay'])","'palette_effect_replay','guard_cell_move_replay','guard_validator_replay','guard_move_original_validator_replay'])")
s=s.replace("'dosbox_map_writers_runtime'):","'dosbox_map_writers_runtime','dosbox_validator_branches_runtime'):")
s=s.replace("root/'font1_keyboard_fields/external_bss_tables.csv'):","root/'font1_keyboard_fields/external_bss_tables.csv',root/'guard_validator_partial/external_bss_tables.csv'):")
line="    refinement_paths.append(root/'guard_collision_fields/consumer_field_roles.csv')"
if line not in s:s=s.replace("    records=[]\n",line+"\n    records=[]\n")
p.write_text(s,encoding='utf-8')
items=[('record18_door',0,2,'near DS descriptor pointer'),('record18_door',4,4,'exact offset/segment cell key'),('record18_door',8,2,'state WORD: predicates one and zero-or-four'),('record18_door',12,2,'coordinate0 origin plus32 alignment'),('record18_door',14,2,'coordinate1 origin plus32 alignment'),('record18_door',16,1,'interaction request flag set1 for mode6'),('descriptor_near_DS',6,1,'kind range33h..3Ch bypasses active interaction'),('descriptor_near_DS',7,1,'axis selector2 versus other'),('record26',6,2,'timer reset32 for strategy1'),('record26',10,1,'strategy1 gates position/velocity transition'),('record26',11,1,'mode6 request, mode17 after transition'),('record26',19,1,'signed coordinate0 velocity -8/0/8'),('record26',20,1,'signed coordinate1 velocity -8/0/8'),('record28',16,2,'coordinate0 alignment'),('record28',18,2,'coordinate1 alignment')]
out=r/'guard_collision_fields';out.mkdir(exist_ok=True)
with (out/'consumer_field_roles.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['record','offset','width','role','consumer'])
 for record,offset,width,role in items:w.writerow([record,offset,width,role,'04C7:0254; PARTIAL; motion/transition/interaction callees not closed'])
(out/'summary.json').write_text(json.dumps(dict(field_evidence_rows=len(items),status='PARTIAL',original_NONCODE_bytes_added=0,new_deep_verified_bytes=0,scope='consumer roles, not unique-field or whole-record semantic closure'),indent=2)+'\n',encoding='utf-8')
