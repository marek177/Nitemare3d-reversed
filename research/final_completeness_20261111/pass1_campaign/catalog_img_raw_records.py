"""python catalog_img_raw_records.py GAME_DIR DESCRIPTOR_CSV OUT
Parse width/height+10BYTE headers and exact area-byte payloads per original03CA/045C.
"""
import csv,hashlib,json,sys
from pathlib import Path
source,descriptors,out=map(Path,sys.argv[1:]);out.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();headers=list(csv.DictReader(descriptors.open(encoding='utf-8-sig')));images=[];groups=[];seen={};files=[]
for ep in (1,2,3):
 p=source/('IMG.'+str(ep));blob=p.read_bytes();files.append(dict(path=str(p.resolve()),sha256=sha(blob)))
 for h in (r for r in headers if int(r['episode'])==ep and int(r['payload_offset'])!=0):
  key=(ep,h['kind'],int(h['payload_offset']),int(h['image_count_BYTE2']));seen.setdefault(key,[]).append(h['code'])
 for (episode,kind,start,count),codes in (x for x in seen.items() if x[0][0]==ep):
  cursor=start;bad=False;begin=len(images)
  for index in range(count):
   assert cursor+10<=len(blob),(ep,kind,cursor);raw=blob[cursor:cursor+10];w,hh=raw[:2];area=w*hh;pixel=cursor+10;end=pixel+area;assert end<=len(blob),(ep,kind,cursor,w,hh)
   signed=area if area<32768 else area-65536;valid=(hh==64 and w in (64,128)) if kind=='wall' else signed<=3072;bad|=not valid
   images.append(dict(episode=ep,kind=kind,codes=';'.join(codes),group_payload=start,image_index=index,metadata_file=cursor,pixels_file=pixel,pixels_end_exclusive=end,width=w,height=hh,area_unsigned=area,area_signed=signed,original_dimension_check_passes=valid,raw10_sha256=sha(raw),pixels_sha256=sha(blob[pixel:end]),status='PARTIAL',scope='exact byte stream,not renderer layout or acoustic/image-output parity'))
   cursor=end
  groups.append(dict(episode=ep,kind=kind,codes=';'.join(codes),start=start,end_exclusive=cursor,image_count=count,validation_failures=sum(not r['original_dimension_check_passes'] for r in images[begin:]),group_sha256=sha(blob[start:cursor])))
for name,rs in [('raw_image_records',images),('payload_groups',groups)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
s=dict(groups=len(groups),records=len(images),pixel_bytes_with_aliases=sum(r['area_unsigned'] for r in images),dimension_check_failures=sum(not r['original_dimension_check_passes'] for r in images),signed_area_highbit_records=sum(r['area_unsigned']>=32768 for r in images),zero_area_records=sum(r['area_unsigned']==0 for r in images),episodes=3,runtime_tests=0,new_deep_verified_bytes=0,original_NONCODE_bytes_added=0,scope='unique(ep,kind,payload,count) groups; payload byte sum may overlap across groups,not a file-byte union; original metadata rules and bounds; no decoded visible image/Win16 parity',files=files+[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (descriptors,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
