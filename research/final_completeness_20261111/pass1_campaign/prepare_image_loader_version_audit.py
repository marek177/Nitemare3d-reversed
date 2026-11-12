"""python prepare_image_loader_version_audit.py OUTPUTS"""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'audit_guard_orientation_versions.py').read_text(encoding='utf-8')
s=s.replace('audit_guard_orientation_versions.py','audit_image_group_loader_versions.py')
s=s.replace("patterns=[bytes.fromhex(x) for x in ('558bec568b560a0bd2','c804000057568b7e0a8b7606ff760c','c80800005756c44e088bd9')]","patterns=[bytes.fromhex('c8080000575666837e0800')]")
s=s.replace("cs=(0xaea if f['name']=='actor_to_player_view_octant' else 0x4c7)","cs=0x277")
s=s.replace('bounded3function byte/CFG comparisons','bounded1function byte/CFG comparisons; string PUSH addresses retained')
(r/'audit_image_group_loader_versions.py').write_text(s,encoding='utf-8')
