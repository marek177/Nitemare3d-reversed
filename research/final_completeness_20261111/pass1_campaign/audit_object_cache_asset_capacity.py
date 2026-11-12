"""GAME_DIR RAW_RECORD_CSV OUT: inspect actual object header areas vs3072B slot payload."""
import csv,hashlib,json,sys
from pathlib import Path
game,catalog,out=map(Path,sys.argv[1:]);out.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();rows=[];images={ep:(game/('IMG.'+str(ep))).read_bytes() for ep in (1,2,3)}
for r in csv.DictReader(catalog.open(encoding='utf-8')):
 if r['kind']!='object':continue
 ep=int(r['episode']);pos=int(r['metadata_file']);v=images[ep];header=v[pos:pos+10];assert sha(header)==r['raw10_sha256'];w,h=header[:2];area=w*h;rounded=((area+1023)//1024)*1024;assert (w,h,area)==(int(r['width']),int(r['height']),int(r['area_unsigned']))
 pixels=int(r['pixels_file']);assert pixels==pos+10 and pixels+area==int(r['pixels_end_exclusive']) and sha(v[pixels:pixels+area])==r['pixels_sha256']
 rows.append(dict(episode=ep,codes=r['codes'],group_payload=int(r['group_payload']),image_index=int(r['image_index']),metadata_file=pos,width=w,height=h,logical_bytes=area,XMS_rounded_bytes=rounded,slot_payload_capacity=3072,fits_logical=area<=3072,fits_rounded=rounded<=3072,pixel_sha256=r['pixels_sha256']))
assert rows and all(r['fits_logical'] and r['fits_rounded'] and r['logical_bytes']>0 for r in rows)
synthetic=[]
for w,h in ((0,0),(48,64),(49,64),(128,255),(129,255),(255,255)):
 area=w*h;signed=(area+32768)%65536-32768;rounded=((area+1023)//1024)*1024;synthetic.append(dict(width=w,height=h,logical_bytes=area,signed_area=signed,original_indexer_object_area_check_passes=signed<=3072,XMS_rounded_bytes=rounded,fits_payload=rounded<=3072,scope='Synthetic arithmetic/argument deduction,not native execution or shipped-asset finding'))
for name,rs in [('actual_object_capacity',rows),('synthetic_capacity_conditions',synthetic)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
s=dict(object_records_checked=len(rows),max_logical_bytes=max(r['logical_bytes'] for r in rows),max_rounded_bytes=max(r['XMS_rounded_bytes'] for r in rows),all_supplied_catalog_object_records_fit3072=True,native_tests_added=0,status_changes=0,new_deep_verified_bytes=0,scope='Actual IMG1/2/3 bytes verified against pinned raw-record catalog;rows may alias physical assets and are not a file-byte union. Conditional signed-area/high-bit capacity gap retained separately,not reproduced natively.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in [catalog,Path(__file__)]+[game/('IMG.'+str(ep)) for ep in (1,2,3)]]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
