"""Derive bounded DOS door comparison, preserving semantic MOV immediates."""
import sys
from pathlib import Path
r=Path(sys.argv[1]);s=(r/'audit_guard_validator_dos_versions.py').read_text(encoding='utf-8')
lines=s.splitlines()
for i,line in enumerate(lines):
 if line.startswith('definitions='):lines[i]="definitions=[('door_interaction',0x598,0x704,bytes.fromhex('c80800005756803e'))]"
s='\n'.join(lines)+'\n';s=s.replace('off in (0x50,0x5b)','off in (0xc6,0x12a)').replace("if i.len==3 and raw[off] in (0xb8,0xb9):","if False and i.len==3 and raw[off] in (0xb8,0xb9):")
s=s.replace('values[1]-values[0]==256','values[1]==values[0]')
s=s.replace('assert len(flag_bases)==16','assert len(flag_bases)==10')
s=s.replace("values=[int(x['original']) for x in flag_bases if x['version_label']==label];assert values[1]==values[0]","values=[int(x['original']) for x in flag_bases if x['version_label']==label];assert not values or (len(values)==2 and values[1]==values[0])")
s=s.replace('4functions x8DOSlabels/7images','1function x8DOSlabels/7images').replace('and address-likeMOVAX/CX immediates and twoidentifiedindexedclassificationtable bases','and two identified indexed tile-flag bases; semantic MOV immediates retained')
(r/'audit_door_interaction_dos_versions.py').write_text(s,encoding='utf-8')
