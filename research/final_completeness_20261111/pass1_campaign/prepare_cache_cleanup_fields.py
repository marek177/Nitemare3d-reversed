"""OUTPUTS IMAGE INVENTORY DECODER: source caller contexts and RAM-seed field roles."""
import csv,hashlib,json,struct,sys
from pathlib import Path
r,image,inventory,decoder=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
from cache_reset_model import CacheResetModel
o=r/'cache_cleanup_fields';o.mkdir(exist_ok=True);s=json.loads((r/'dosbox_cache_reset_seed_runtime/summary.json').read_text());ds=s['load_segment']+0x2771;base=ds*16;ram=(r.parent/'work/dosboxx_cache_reset_seed_runtime/object_cache_00_cache_reset_RAM_seed.bin').read_bytes();model=CacheResetModel(ram,ds);model.cleanup()
def save(name,rows):
 with (o/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rows=[]
for name,a,role in [('cleanup_actor_count',0x6270,'signedWORD count of28B actors traversed via world selector,seed222'),('cleanup_wall_metadata_slots',0x6272,'signedWORD count of8B wall-record slots traversed,seed34'),('cleanup_object_metadata_slots',0x6274,'signedWORD count of8B object-record slots traversed,seed28')]:
 rows.append(dict(name=name,ds_start=a,ds_end_exclusive=a+2,image_start=0x27710+a,image_end_exclusive=0x27710+a+2,length=2,type=role,status='PARTIAL',runtime_sha256=hashlib.sha256(ram[base+a:base+a+2]).hexdigest(),outside_original_file_image=True,original_NONCODE_bytes_added=0))
save('external_bss_tables',rows);roles=[]
for record,a,n,role in [('image_record10',6,4,'mode2 clears resident FAR reference for wall/object owner records'),('wall_cache_slot',0,4,'mode2 zeroes timestamp'),('wall_cache_slot',4,2,'mode2 zeroes near-owner after clearing record buffer'),('object_cache_slot',0,2,'mode2 zeroes near-owner after clearing record buffer'),('sound_cache_slot',0,4,'mode2 zeroes timestamp'),('sound_cache_slot',4,2,'mode2 zeroes marker;does not treat it as image-record pointer'),('cache_control',0x350a,2,'XMS used cursor reset0,not XMS backing-byte erase'),('cache_control',0xc9c,2,'cyclic index retained by mode2,seed1'),('class_record8',6,2,'metadata array near pointer passed to mark helper,not zeroed by cleanup'),('class_record8',4,2,'class bank near pointer marked then zeroed,avoids duplicate actor-class marking'),('near_heap_header',0,2,'mark helper ORs lowBYTE bit0,not physical release/coalescing'),('cleanup_counts',0x6270,2,'28B actor loop count,signed'),('cleanup_counts',0x6272,2,'8B wall metadata loop count,signed'),('cleanup_counts',0x6274,2,'8B object metadata loop count,signed')]:roles.append(dict(record=record,offset=a,width=n,role=role,consumer='0768mode2/0D29080E/original3CAE;PARTIAL'))
save('consumer_field_roles',roles)
effects=[]
for a,n,name in [(0xc9c,2,'cyclic_index'),(0x3504,2,'active_count'),(0x3506,2,'XMS_handle'),(0x350a,2,'XMS_used'),(0x350c,1,'XMS_initialized_flag'),(0x3cce,1,'XMS_enabled_flag'),(0x6270,2,'actor_count'),(0x6272,2,'wall_slots'),(0x6274,2,'object_slots')]:effects.append(dict(name=name,DS_offset=a,width=n,native_seed_value=int.from_bytes(ram[base+a:base+a+n],'little'),controlled_cleanup_value=int.from_bytes(model.ram[base+a:base+a+n],'little'),scope='Controlled original-code replay confirmed,not native cleanup execution'))
save('control_effects',effects);banks=[]
for cls in range(70):
 p=base+0x3d22+8*cls;old=int.from_bytes(ram[p:p+2],'little');new=int.from_bytes(model.ram[p:p+2],'little')
 if old!=new:banks.append(dict(class_index=cls,bank_pointer_before=old,bank_pointer_after=new,metadata_pointer_before=int.from_bytes(ram[p+2:p+4],'little'),metadata_pointer_after=int.from_bytes(model.ram[p+2:p+4],'little'),scope='RAM-seeded controlled cleanup,not native invocation'))
assert len(banks)==4;save('class_bank_cleanup',banks)
b=image.read_bytes();old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};fmt=Formatter(FormatterSyntax.INTEL);rows=[]
for cs,lo,hi in [(0xd29,0x95a,0x968),(0x476,0x12d,0x137),(0x476,0x1c4,0x1ce)]:
 for i in Decoder(16,b[cs*16+lo:cs*16+hi],ip=lo):
  p=cs*16+i.ip;raw=b[p:p+i.len];assert old[p]['bytes']==raw.hex();rows.append(dict(cs=cs,ip=i.ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
save('caller_contexts',rows)
