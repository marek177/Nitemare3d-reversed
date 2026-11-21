from pathlib import Path
import json,csv,struct,hashlib
R=Path.cwd();O=R/'outputs/bsf_version_scan_20261107';s=json.loads((O/'scan.json').read_text());inv={x['id']:x for x in json.loads((R/'outputs/evidence/binary_inventory.json').read_text())};rows=list(csv.DictReader((R/'outputs/evidence/function_inventory.csv').open(encoding='utf-8-sig')));out=[]
for x in s['rows']:
 hit=x['candidate_hits'][0];matches=[r for r in rows if r['binary_id']==x['binary_id'] and int(r['file_offset'],0)==hit['file_offset']];assert len(matches)==1;rec=json.loads((R/'outputs/evidence'/matches[0]['record']).read_text());cfg=json.loads((R/'outputs/evidence'/rec['cfg']).read_text());b=Path(inv[x['binary_id']]['source_path']).read_bytes();assert hashlib.sha256(b).hexdigest()==x['sha256'];entry=int(matches[0]['entry'].split(':')[1],16);expected={}
 for i in cfg['instructions']:
  delta=i['offset']-entry
  if 0<=delta<62:assert b[hit['file_offset']+delta:hit['file_offset']+delta+len(bytes.fromhex(i['bytes']))]==bytes.fromhex(i['bytes']);expected[delta]=i['bytes']
 assert len(expected)==29
 row={'binary_id':x['binary_id'],'sha256':x['sha256'],'function_id':matches[0]['function_id'],'file_offset':hit['file_offset'],'key_near_offset':hit['key_near_offset'],'matched_instructions':29,'boundary_status':matches[0]['boundary_status'],'key_segment_provenance':'OPEN'}
 if x['kind']=='NE':
  ne=int.from_bytes(b[0x3c:0x40],'little');shift=int.from_bytes(b[ne+0x32:ne+0x34],'little');table=ne+int.from_bytes(b[ne+0x22:ne+0x24],'little');segments=[]
  for j in range(int.from_bytes(b[ne+0x1c:ne+0x1e],'little')):
   sector,length,flags,minimum=struct.unpack_from('<4H',b,table+8*j);start=sector<<shift;length=length or 65536
   if start<=hit['file_offset']<start+length:segments.append({'segment_index':j+1,'offset':hit['file_offset']-start,'flags':flags})
  assert len(segments)==1;row['NE_segment_mapping']=segments[0];assert segments[0]['offset']==entry
 out.append(row)
(O/'function_mapping.json').write_text(json.dumps({'status':'VERIFIED_BOUNDED_CODE_MEMBERSHIP_AND_NE_FILE_MAPPING','rows':out,'scope':'All13 exact inventory entries/29 instructions; only keydisplacement varied. Key contents/SS provenance, whole boundaries, nativeWin16 and remake parity remainopen.'},indent=2));print(json.dumps([(x['binary_id'],x['function_id']) for x in out]))
