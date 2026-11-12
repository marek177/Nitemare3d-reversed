"""OUTPUTS_DIR: all PASS320 intervals at verified native initialization endpoints.
New endpoint comparison, not reads/same-value-store tracing or status promotion.
"""
import csv,json,hashlib,struct,sys
from pathlib import Path
r=Path(sys.argv[1]).resolve();out=r/'pass1_cache_init_endpoints';out.mkdir(exist_ok=True);sha=lambda x:hashlib.sha256(x).hexdigest();native=r/'dosbox_cache_initialization_runtime';proof=json.loads((native/'independent_verification.json').read_text());assert proof['verified']
for f in proof['files']:assert sha(Path(f['path']).read_bytes())==f['sha256']
summary=json.loads((native/'summary.json').read_text());load=summary['load_segment']
before_path=next(Path(f['path']) for f in proof['files'] if Path(f['path']).name=='init_before_RAM.bin');after_path=next(Path(f['path']) for f in proof['files'] if Path(f['path']).name=='init_after_RAM.bin');before=before_path.read_bytes();after=after_path.read_bytes();image=r/'unpack/reproduced_image.bin';b=image.read_bytes();map_path=r/'pass1_xms_move_request/noncode_intervals.csv';assert sha(map_path.read_bytes())=='497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe'
rows=[];deltas=[];owned=set();remaining=set();changed=set();counts={}
for index,x in enumerate(csv.DictReader(map_path.open(encoding='utf-8-sig'))):
 a,e=int(x['start']),int(x['end_exclusive']);assert sha(b[a:e])==x['range_sha256'];assert not(owned&set(range(a,e)));owned.update(range(a,e));counts[x['status']]=counts.get(x['status'],0)+e-a
 if x['status'] in ('UNKNOWN','CLASSIFIED ONLY'):remaining.update(range(a,e))
 p=load*16+a;q=load*16+e;first,last=before[p:q],after[p:q];assert len(first)==len(last)==e-a
 local=[a+j for j in range(e-a) if first[j]!=last[j]];changed.update(local)
 for pos in local:deltas.append(dict(interval_id=index,image_offset=pos,physical=load*16+pos,before=before[load*16+pos],after=after[load*16+pos],status=x['status']))
 rows.append(dict(interval_id=index,start=a,end_exclusive=e,length=e-a,status=x['status'],original_sha256=x['range_sha256'],before_sha256=sha(first),after_sha256=sha(last),changed_byte_positions=len(local),changed_positions_hex=';'.join('%05X'%x for x in local),status_promoted=False,evidence_scope='two native endpoints only; not read/same-write/transient/nonuse proof'))
def save(name,data):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
save('interval_profiles',rows);save('byte_deltas',deltas);(out/'interval_profiles.json').write_text(json.dumps(rows,indent=2)+'\n')
alloc=list(csv.DictReader((native/'allocation_records.csv').open()));vectors=[]
for index,x in enumerate(alloc[14:]):
 a=0x1be70+4*index;p=load*16+a;off,seg=struct.unpack_from('<HH',after,p);assert (off,seg)==(int(x['offset']),int(x['segment']));assert owned.issuperset(range(a,a+4));address=seg*16+off;assert after[address:address+2]==b'\0\0'
 vectors.append(dict(index=index,image_start=a,image_end_exclusive=a+4,offset=off,segment=seg,physical_buffer=address,allocation_request_bytes=int(x['size']),final_owner_word=0,status='PARTIAL',evidence='native whole-init allocation return + final vector/header equality; same-value-store events not directly trapped'))
save('active_object_vector_records',vectors)
s=dict(intervals=len(rows),original_noncode_bytes=len(owned),full_interval_endpoint_samples=2*len(rows),changed_intervals=sum(bool(x['changed_byte_positions']) for x in rows),changed_byte_positions=len(changed),active_vector_changed_byte_positions=len(changed&set(range(0x1be70,0x1bf68))),other_changed_byte_positions=sorted(changed-set(range(0x1be70,0x1bf68))),remaining177_changed_positions=sorted(remaining&changed),active_vector_records=len(vectors),active_vector_bytes=4*len(vectors),inactive_capacity_bytes=512-4*len(vectors),status_bytes=counts,new_deep_verified_bytes=0,runtime_tests=0,scope='Separate two-endpoint profile for one alreadycounted nativeinit; previous52capture profile frozen. All57295Bcompared,not semantic closure/nonuse. No addednativecase/statuspromotion.',files=[dict(path=str(p),sha256=sha(p.read_bytes())) for p in (image,map_path,native/'independent_verification.json',before_path,after_path,native/'allocation_records.csv',Path(__file__).resolve())])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
