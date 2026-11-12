"""python audit_sound_directory_producer.py IMAGE INVENTORY DECODER SND RUNTIME WORK OUT"""
import collections,csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,sound,runtime,work,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();asset=sound.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';assert sha(asset)=='f3434984d315531602d32285cb8ff55990bba786f5fb37f53710e88379388614';proof=json.loads((runtime/'independent_verification.json').read_text());assert proof['sound_directory_runtime_verified']
for item in proof['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
captured=(work/'sound_directory_runtime.bin').read_bytes();assert captured==asset[192:666]
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};fmt=Formatter(FormatterSyntax.INTEL);rows=[];pos=0x3250
for i in Decoder(16,b[0x3250:0x32b0],ip=0xae0):
 assert not i.is_invalid and lookup[pos]['bytes']==b[pos:pos+i.len].hex();rows.append(dict(cs=0x277,ip=i.ip,image_offset=pos,bytes=b[pos:pos+i.len].hex(),instruction=fmt.format(i)));pos+=i.len
assert pos==0x32b0 and rows[-1]['bytes']=='cb' and b[0x27c64:0x27c6c]==b'snd.dat\0'
def save(name,rs):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
save('sound_directory_init',rows);records=[]
for n in range(79):
 length,offset=struct.unpack_from('<HI',captured,n*6);assert 0<=offset<=len(asset) and offset+length<=len(asset)
 records.append(dict(sound_id=n,file_record_index=32+n,record_file_start=192+6*n,record_file_end_exclusive=198+6*n,ds_start=0x3f64+6*n,length=length,payload_start=offset,payload_end_exclusive=offset+length,payload_sha256=sha(asset[offset:offset+length]),header16_hex=asset[offset:offset+min(16,length)].hex(),status='PARTIAL_metadata_and_bounds; payload_algorithm_open'))
save('runtime_directory_records',records);aliases=[]
for pair in sorted({(r['payload_start'],r['length']) for r in records if r['length']}):
 ids=[r['sound_id'] for r in records if (r['payload_start'],r['length'])==pair]
 if len(ids)>1:aliases.append(dict(payload_start=pair[0],length=pair[1],sound_ids=';'.join(map(str,ids)),payload_sha256=sha(asset[pair[0]:pair[0]+pair[1]])))
save('shared_payload_aliases',aliases)
contexts=[]
for r in old:
 if (r['cs']==0x277 and 0xb40<=r['ip']<0xb72) or (r['cs']==0xc2b and 0x39e<=r['ip']<0x3d6):
  raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert i.len==len(raw) and not i.is_invalid;contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
save('consumer_contexts',contexts)
save('external_bss_tables',[dict(name='sound_directory_WORD_length_DWORD_offset_79',ds_start=0x3f64,ds_end_exclusive=0x413e,image_start=0x2b674,image_end_exclusive=0x2b84e,length=474,type='79_records_WORD_payload_length_DWORD_file_offset',status='PARTIAL',runtime_sha256=sha(captured),outside_original_file_image=True,original_NONCODE_bytes_added=0)])
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),sound_path=str(sound.resolve()),sound_sha256=sha(asset),sound_bytes=len(asset),runtime_proof_sha256=sha((runtime/'independent_verification.json').read_bytes()),functions=[dict(name='sound_directory_init',start=0x3250,end_exclusive=0x32b0,instruction_bytes=96,instructions=len(rows))],records=79,empty_records=sum(r['length']==0 for r in records),nonempty_records=sum(r['length']!=0 for r in records),max_payload_length=max(r['length'] for r in records),nonempty_alias_groups=len(aliases),runtime_directory_sha256=sha(captured),bss_table_bytes=474,runtime_tests=0,new_deep_verified_bytes=0,scope='static producer and actual SND474B-to-BSS capture; source metadata bounds, not complete payload/audio/WORX decoder semantics; session counted separately')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
