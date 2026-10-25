from pathlib import Path
import json,hashlib,struct,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];D=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'outputs/evidence/runtime/clean_run_c/paused_display';v=json.loads((D/'host_VGA_capture.json').read_text());f=v['decoded_fields'];c=f['config'];draw=f['draw_prefix'];crtc=f['crtc'];dac=(D/'host_VGA_dac.bin').read_bytes();rgb=(D/'host_VGA_DAC_768.bin').read_bytes();vram=(D/'host_VGA_vram_256k.bin').read_bytes()
assert v['selected_fields_and_VRAM_stable'] and v['A000_matching_interleaved_planes']==[0]
assert v['emulator_sha256']=='78fd1926272de172c2a87b9456aafce5eb54ea928ad1e5103a6d943bc26f0f57'
assert hashlib.sha256(vram).hexdigest()==v['vram_sha256'] and hashlib.sha256(rgb).hexdigest()==v['DAC_sha256']
assert dac[32:800]==rgb
assert c['chained']==0 and c['read_map_select']==0 and c['display_start']==0 and c['real_start']==0
assert c['pel_panning']==0 and c['bytes_skip']==0 and c['hlines_skip']==0
assert draw['width']==320 and draw['height']==400 and draw['address_add']==320 and draw['address_line_total']==2 and draw['split_line']>=400
assert f['seq']['memory_mode']&8==0 and crtc['offset']==40 and crtc['mode_control']&0x40 and crtc['underline_location']&0x40==0
assert f['dac']['bits']==6 and f['dac']['pel_mask']==255
assert f['attr']['mode_control']&0x40 and f['gfx']['mode']&0x40
layout=v['RGB_entry_layout'];assert [(m['name'],m['offset']) for m in layout['fields']]==[('red',0),('green',1),('blue',2)]
xlat=struct.unpack('<256I',dac[1312:2336]);expected=[]
for i in range(256):
 r,g,b=rgb[3*i:3*i+3];r=(r<<2)|(r>>4);g=(g<<2)|(g>>4);b=(b<<2)|(b>>4);expected.append((r<<16)|(g<<8)|b)
assert all((a&0xffffff)==e for a,e in zip(xlat,expected))
pixels=bytes(vram[4*(80*y+(x>>2))+(x&3)] for y in range(200) for x in range(320));assert pixels==vram[:64000]
expanded=bytes(channel for index in pixels for channel in [(xlat[index]>>16)&255,(xlat[index]>>8)&255,xlat[index]&255])
(D/'decoded_indexed_320x200.bin').write_bytes(pixels);Image.frombytes('RGB',(320,200),expanded).save(D/'decoded_320x200.png')
record={'status':'VERIFIED_RUNTIME','capture_source':'PDB-matched read-only emulator VGA backing state','capture_revision':v['revision'],'index_sha256':hashlib.sha256(pixels).hexdigest(),'DAC_sha256':hashlib.sha256(rgb).hexdigest(),'PNG_sha256':hashlib.sha256((D/'decoded_320x200.png').read_bytes()).hexdigest(),'logical_dimensions':[320,200],'physical_scanline_dimensions':[320,400],'projection':'index(x,y)=vram[4*(80*y+(x>>2))+(x&3)] under explicitly validated zero-start, no-panning, no-split conditions','palette_validation':'all256 DAC6->RGB8 entries match captured emulator xlat32 channel order','frame_boundary_aligned':False,'paired_remake_snapshot':False,'whole_renderer_parity_proven':False,'limits':['Decoder intentionally rejects nonzero display_start/real_start and unsupported panning/split layouts','This is reconstruction from frozen original emulator state, not a native-window screenshot','No gameplay-stage or whole-engine completeness claim']}
(D/'decoded_capture_proof.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))

