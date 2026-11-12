"""OUTPUTS: field catalogs and version-audit derivation (not native captures)."""
import csv,hashlib,sys
from pathlib import Path
r=Path(sys.argv[1]);o=r/'image_retrieval_fields';o.mkdir(exist_ok=True);w=r.parent/'work/dosboxx_image_retrieval_runtime';prefix='image_retrieval_00_'
def save(name,rows):
 with (o/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
  ww=csv.DictWriter(f,fieldnames=list(rows[0]));ww.writeheader();ww.writerows(rows)
rows=[]
for name,a,z,typ,fn in [('image_cache_slot_pointers',0x34cc,0x34f4,'FAR16[10] slot pointer vector','slot_pointers'),('image_cache_evictions',0xe006,0xe00a,'DWORD replacement counter; native unchanged,controlled wrap checked','stats_before'),('image_cache_fallbacks',0xe00a,0xe00e,'DWORD no-strictly-older fallback counter; native unchanged,controlled wrap checked','stats_before'),('image_cache_current_tick',0x4540,0x4544,'DWORD unsigned ordering value consumed by0402; producer semantics not closed','tick_before')]:
 raw=(w/(prefix+fn+'.bin')).read_bytes()
 if fn=='stats_before':raw=raw[a-0xe006:z-0xe006]
 assert len(raw)==z-a
 rows.append(dict(name=name,ds_start=a,ds_end_exclusive=z,image_start=0x27710+a,image_end_exclusive=0x27710+z,length=z-a,type=typ,status='PARTIAL',runtime_sha256=hashlib.sha256(raw).hexdigest(),outside_original_file_image=True,original_NONCODE_bytes_added=0))
save('external_bss_tables',rows)
rows=[]
for record,off,width,role in [('image_cache_slot',0,4,'unsigned timestamp compared with DS4540; overwritten at fill'),('image_cache_slot',4,2,'near DS owner record,old owner buffer invalidated'),('image_cache_slot',6,8192,'pixel destination passed as FAR16,8192-byte request; allocation bound still open'),('image_record10',2,4,'signed positive file offset,nonpositive negated XMS offset including zero'),('image_record10',6,4,'resident cache slot pixel FAR pointer; assigned0402,cleared on slot eviction; complements temporary raw load pointer')]:
 rows.append(dict(record=record,offset=off,width=width,role=role,consumer='0768:0402/0350;PARTIAL'))
save('consumer_field_roles',rows)
s=(r/'audit_image_record_versions.py').read_text(encoding='utf-8')
s=s.replace('audit_image_record_versions.py','audit_image_retrieval_versions.py').replace("('558bec566a0a66ff7606','c80200005756803e','c8040000578b7e068a4501')","('c80400006668000400008b460e2bd2','c80a0000575633c0998bf88956f8')")
s=s.replace("refcs=0x768 if f['name']=='image_record_tag_XMS_offset' else 0x277","refcs=0x768")
s=s.replace('DOS10split not forced to unified function','counterparts bounded by retained owners, not inferred gameplay parity')
(r/'audit_image_retrieval_versions.py').write_text(s,encoding='utf-8')
