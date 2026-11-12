"""OUTPUTS: deepen existing512B PASS1 vector/cursor, retain new field roles and DOS audit."""
import csv,hashlib,sys
from pathlib import Path
r=Path(sys.argv[1]);o=r/'object_cache_fields';o.mkdir(exist_ok=True);work=r.parent/'work/dosboxx_object_cache_draw_runtime';p='object_cache_00_';dg=(work/(p+'DGROUP_after.bin')).read_bytes()
def save(name,rows):
 with (o/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rows=[]
for name,a,z,role in [('object_cache_active_count',0x3504,0x3506,'signedWORD active prefix count,uppercap128,native62'),('object_cache_eviction_count',0xe012,0xe016,'DWORD old-owner invalidation count,controlled wrap;nativeunchanged0'),('allocation_probe_KiB_snapshot',0x3cb4,0x3cb6,'WORD storedFBA0058 probe result,native257;not currentfreeRAM')]:
 raw=dg[a:z];rows.append(dict(name=name,ds_start=a,ds_end_exclusive=z,image_start=0x27710+a,image_end_exclusive=0x27710+z,length=z-a,type=role,status='PARTIAL',runtime_sha256=hashlib.sha256(raw).hexdigest(),outside_original_file_image=True,original_NONCODE_bytes_added=0))
save('external_bss_tables',rows)
save('runtime_field_intervals',[dict(start=0x1be70,end_exclusive=0x1c070,length=512,type='mutableFAR16[128],native62active/66zero,preserved512B across04D8,selectorrelocationverified'),dict(start=0x283ac,end_exclusive=0x283ae,length=2,type='mutableWORD cyclic index DS0C9C,native0to1,not newtypedcoverage')])
rows=[]
for record,a,n,role in [('object_cache_slot',0,2,'nearDS owner record;old owner buffer cleared on replacement'),('object_cache_slot',2,3072,'pixel storage after2Bowner;allocation request3074,not fullheap/lifecycleproof'),('object_cache_control',0xc9c,2,'mutable cyclic index,postincrement with signedcount bound'),('object_cache_control',0x3504,2,'signedWORD active vector count,native62,cap128'),('object_cache_control',0xe012,4,'DWORD old-owner eviction counter'),('object_cache_control',0x3cb4,2,'allocation probe KiB snapshot,not currentfreeRAM'),('image_record10',6,4,'resident cyclic-slot pixel FAR;helperDXAX is not this FAR pointer'),('raw_object_image_pixels',0,600,'native30x20 column-major x*height+y,pixel1Ftransparent;oneactualdraw plusprior syntheticmatrix')]:
 rows.append(dict(record=record,offset=a,width=n,role=role,consumer='0768:04D8/0156:05DE;PARTIAL'))
save('consumer_field_roles',rows)
s=(r/'audit_image_record_versions.py').read_text(encoding='utf-8').replace('audit_image_record_versions.py','audit_object_cache_versions.py')
s=s.replace("('558bec566a0a66ff7606','c80200005756803e','c8040000578b7e068a4501')","('c806000057568e06',)").replace("refcs=0x768 if f['name']=='image_record_tag_XMS_offset' else 0x277","refcs=0x768").replace('DOS10split not forced to unified function','objectcache counterparts bounded by retained owners; no allocation/XMS environment equivalence')
(r/'audit_object_cache_versions.py').write_text(s,encoding='utf-8')
