"""Project a validated planar VRAM page, without claiming an actual scanout frame."""
from pathlib import Path
import hashlib,json,struct,sys
from PIL import Image

def decode(folder,selector):
    d=Path(folder);v=json.loads((d/'host_VGA_capture.json').read_text())
    f=v['decoded_fields'];c=f['config'];draw=f['draw_prefix'];crtc=f['crtc']
    assert selector in ('programmed','latched')
    assert v['selected_fields_and_VRAM_stable'] and v['A000_matching_interleaved_planes']==[0]
    assert v['emulator_sha256']=='78fd1926272de172c2a87b9456aafce5eb54ea928ad1e5103a6d943bc26f0f57'
    rgb=(d/'host_VGA_DAC_768.bin').read_bytes();dac=(d/'host_VGA_dac.bin').read_bytes();ram=(d/'host_VGA_vram_256k.bin').read_bytes()
    assert len(ram)==262144 and len(rgb)==768 and dac[32:800]==rgb
    assert hashlib.sha256(ram).hexdigest()==v['vram_sha256'] and hashlib.sha256(rgb).hexdigest()==v['DAC_sha256']
    assert c['chained']==0 and c['read_map_select']==0 and c['addr_shift']==0
    assert c['pel_panning']==c['bytes_skip']==c['hlines_skip']==0
    assert draw['width']==320 and draw['height']==400 and draw['address_add']==320 and draw['address_line_total']==2 and draw['split_line']>=400
    assert draw['panning']==draw['bytes_skip']==0
    assert f['seq']['memory_mode']&8==0 and crtc['offset']==40 and crtc['mode_control']&0x40 and crtc['underline_location']&0x40==0
    assert f['dac']['bits']==6 and f['dac']['pel_mask']==255
    assert f['attr']['mode_control']&0x40 and f['gfx']['mode']&0x40
    assert [(m['name'],m['offset']) for m in v['RGB_entry_layout']['fields']]==[('red',0),('green',1),('blue',2)]
    assert c['display_start']==(crtc['start_address_high']<<8|crtc['start_address_low'])
    start=c['display_start' if selector=='programmed' else 'real_start']
    # Only the game's two currently established pages; no address wrap accepted.
    assert start in (0,0x4000) and 4*(start+16000)<=len(ram)
    xlat=struct.unpack('<256I',dac[1312:2336]);expected=[]
    for i in range(256):
        r,g,b=rgb[3*i:3*i+3];assert max(r,g,b)<64
        r=(r<<2)|(r>>4);g=(g<<2)|(g>>4);b=(b<<2)|(b>>4)
        expected.append((r<<16)|(g<<8)|b)
    assert all((a&0xffffff)==b for a,b in zip(xlat,expected))
    pixels=bytes(ram[4*(start+80*y+(x>>2))+(x&3)] for y in range(200) for x in range(320))
    assert pixels==ram[4*start:4*start+64000]
    image=bytes(ch for i in pixels for ch in ((xlat[i]>>16)&255,(xlat[i]>>8)&255,xlat[i]&255))
    stem=f'page_projection_{selector}'
    (d/(stem+'.bin')).write_bytes(pixels);Image.frombytes('RGB',(320,200),image).save(d/(stem+'.png'))
    proof={'status':'VERIFIED_RUNTIME_PAGE_CONTENT_PROJECTION','selector':selector,'page_start':start,'programmed_start':c['display_start'],'latched_start':c['real_start'],'capture_revision':v['revision'],'dimensions':[320,200],'formula':'VRAM[4*(page_start+80*y+(x>>2))+(x&3)]','index_sha256':hashlib.sha256(pixels).hexdigest(),'DAC_sha256':hashlib.sha256(rgb).hexdigest(),'PNG_sha256':hashlib.sha256((d/(stem+'.png')).read_bytes()).hexdigest(),'actual_scanout_frame_proven':False,'frame_boundary_aligned':False,'paired_remake_snapshot':False,'limits':['Page content under captured addressing registers and one frozen DAC palette; not an assembled raster frame','Programmed and latched starts can differ; in-progress scanout timing is not reconstructed','Only starts 0 and 0x4000; panning, wrap and in-image split rejected']}
    (d/(stem+'.json')).write_text(json.dumps(proof,indent=2));return proof

if __name__=='__main__':
    print(json.dumps(decode(sys.argv[1],sys.argv[2])))

