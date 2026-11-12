"""python catalog_img90_descriptors.py GAME_DIR OUT
Direct resource/header census, keep payload aliases and discrepancies explicit.
"""
import collections,csv,hashlib,json,struct,sys
from pathlib import Path
source,out=map(Path,sys.argv[1:]);out.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();rows=[];groups=[];inputs=[]
for episode in (1,2,3):
 p=source/('IMG.'+str(episode));b=p.read_bytes();assert len(b)>=0xbc00;inputs.append(dict(path=str(p.resolve()),bytes=len(b),sha256=sha(b)))
 for kind in (0,1):
  aliases=collections.defaultdict(list)
  for code in range(256):
   index=kind*256+code;key=struct.unpack_from('<I',b,index*4)[0];off=0x800+90*index;header=b[off:off+90];assert len(header)==90
   row=dict(episode=episode,kind='object' if kind else 'wall',code=code,offset_table_file=index*4,payload_offset=key,payload_in_file=key<len(b) if key else None,header_file=off,header_length=90,header_WORD0=struct.unpack_from('<H',header)[0],image_count_BYTE2=header[2],bank_present_BYTE3=header[3],header_sha256=sha(header),directional_rows48_sha256=sha(header[4:52]),remaining38_sha256=sha(header[52:90]),status='PARTIAL',scope='exact fixed header, decoder payload semantics unclosed')
   rows.append(row)
   if key:aliases[key].append(row)
  for key,rs in aliases.items():
   if len(rs)>1:groups.append(dict(episode=episode,kind='object' if kind else 'wall',payload_offset=key,codes=';'.join(str(r['code']) for r in rs),members=len(rs),distinct_header_SHA256=len(set(r['header_sha256'] for r in rs)),distinct_image_counts=len(set(r['image_count_BYTE2'] for r in rs)),distinct_bank_flags=len(set(r['bank_present_BYTE3'] for r in rs))))
for name,rs in [('descriptors',rows),('nonzero_payload_aliases',groups)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]) if rs else ['episode','kind','payload_offset']);w.writeheader();w.writerows(rs)
s=dict(episodes=3,descriptors=len(rows),descriptor_bytes=len(rows)*90,offset_table_bytes=3*0x800,nonzero_payloads=sum(bool(r['payload_offset']) for r in rows),nonzero_payloads_outside_file=sum(r['payload_in_file'] is False for r in rows),alias_groups=len(groups),alias_groups_different_headers=sum(r['distinct_header_SHA256']>1 for r in groups),alias_groups_different_counts=sum(r['distinct_image_counts']>1 for r in groups),alias_groups_different_bank_flags=sum(r['distinct_bank_flags']>1 for r in groups),runtime_tests=0,new_deep_verified_bytes=0,original_NONCODE_bytes_added=0,scope='DOS2 supplied IMG1/2/3 fixed512DWORDoffsets+512x90BYTEheaders; file identity/payload alias census, not full payload decode or resource equality across game versions',files=inputs+[dict(path=str(Path(__file__).resolve()),sha256=sha(Path(__file__).read_bytes()))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
