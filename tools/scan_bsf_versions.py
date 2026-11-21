from pathlib import Path
import json,hashlib
R=Path.cwd();inv=json.loads((R/'outputs/evidence/binary_inventory.json').read_text());base=next(x for x in inv if x['id']=='nite3d20');raw=Path(base['source_path']).read_bytes();im=raw[int.from_bytes(raw[8:10],'little')*16:];sig=im[0xfba*16+0x1b2:0xfba*16+0x1f0];assert sig[39:44]==bytes.fromhex('368a874520');rows=[]
for x in inv:
 b=Path(x['source_path']).read_bytes();assert hashlib.sha256(b).hexdigest()==x['sha256'];hits=[];start=0
 while True:
  p=b.find(sig[:39],start)
  if p<0:break
  chunk=b[p:p+62]
  if len(chunk)==62 and chunk[:42]+chunk[44:]==sig[:42]+sig[44:]:hits.append({'file_offset':p,'key_near_offset':int.from_bytes(chunk[42:44],'little'),'exact_all62_bytes':chunk==sig})
  start=p+1
 rows.append({'binary_id':x['id'],'sha256':x['sha256'],'kind':x['kind'],'candidate_hits':hits,'status':'BOUNDED_CODE_SKELETON_CANDIDATE' if hits else 'NO_MATCH_FOR_THIS_SIGNATURE','scope':'Only key displacement varied; no function-boundary, key bytes/segment provenance, relocation or ABI/version equivalence claim.'})
O=R/'outputs/bsf_version_scan_20261107';O.mkdir(exist_ok=True);(O/'scan.json').write_text(json.dumps({'signature_source_sha256':base['sha256'],'signature_bytes':62,'masked_offsets':[42,43],'rows':rows},indent=2));print(json.dumps([(r['binary_id'],len(r['candidate_hits'])) for r in rows]))
