from pathlib import Path
import json,hashlib,struct
R=Path.cwd();O=R/'outputs/bsf_version_scan_20261107';maps=json.loads((O/'function_mapping.json').read_text());inv={x['id']:x for x in json.loads((R/'outputs/evidence/binary_inventory.json').read_text())};ref=Path(inv['nite3d20']['source_path']).read_bytes();start=int.from_bytes(ref[8:10],'little')*16;key=ref[start+0x2771*16+0x2045:start+0x2771*16+0x2045+52];rows=[]
for x in maps['rows']:
 b=Path(inv[x['binary_id']]['source_path']).read_bytes();assert hashlib.sha256(b).hexdigest()==x['sha256'];hits=[];p=0
 while True:
  p=b.find(key,p)
  if p<0:break
  hits.append(p);p+=1
 assert len(hits)==1
 row={'binary_id':x['binary_id'],'sha256':x['sha256'],'key52_sha256':hashlib.sha256(key).hexdigest(),'unique_key_file_offset':hits[0],'key_near_offset':x['key_near_offset']}
 if inv[x['binary_id']]['kind']=='DOS':
  origin=hits[0]-int.from_bytes(b[8:10],'little')*16-x['key_near_offset'];assert origin>=0 and origin%16==0;row['inferred_key_segment_paragraph']=origin//16;row['segment_status']='INFERRED_FROM_UNIQUE_KEY_LOCATION_NOT_GENERAL_SS_PROVENANCE'
 else:
  ne=int.from_bytes(b[0x3c:0x40],'little');table=ne+int.from_bytes(b[ne+0x22:ne+0x24],'little');auto=int.from_bytes(b[ne+0xe:ne+0x10],'little');shift=int.from_bytes(b[ne+0x32:ne+0x34],'little');sector,length,flags,minimum=struct.unpack_from('<4H',b,table+8*(auto-1));assert (sector<<shift)+x['key_near_offset']==hits[0];row['NE_auto_data_segment_index']=auto;row['NE_initial_SS_header']=int.from_bytes(b[ne+0x1a:ne+0x1c],'little');row['segment_status']='VERIFIED_KEY_IN_NE_AUTO_DATA_SEGMENT;NATIVE_SS_SELECTOR_UNPROVEN'
 rows.append(row)
(O/'key_mapping.json').write_text(json.dumps({'status':'VERIFIED_IDENTICAL_KEY_BYTES_IN_ALL13_IMAGES','rows':rows,'scope':'Same key bytes and bounded instruction skeleton. NativeSS provenance for otherDOS/Win16, aliases, loader state and wholefunction parity remainopen.'},indent=2));print(json.dumps([(x['binary_id'],x.get('inferred_key_segment_paragraph',x.get('NE_auto_data_segment_index'))) for x in rows]))
