"""Read-only hash-gated checks of bounded DOS20 VGA code; no game assets included."""
import argparse,json,hashlib,struct
from pathlib import Path
SOURCE_SHA="5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3"
SPECS=[{'id': 'nite3d20:0156:008E', 'ranges': [[142, 167]], 'sha256': 'c18fa357741bf075c031e107ca444f124c719fb312479fc59d2a914ce482af30'}, {'id': 'nite3d20:0156:00A8', 'ranges': [[168, 215]], 'sha256': '14a45f1f399f5fd0ff96302ad5e3ce5a88eeb43e6fb9a8444f70c3710069dce8'}, {'id': 'nite3d20:0156:0A3A', 'ranges': [[2618, 2661]], 'sha256': '0523f7b98b5d0b3b0ba290decd9538460d4fa28342b001547935f341c89319bd'}, {'id': 'nite3d20:0156:0A66', 'ranges': [[2662, 2746]], 'sha256': '29af4920cb584a81f7fd4699ba2025f738e79a833a8dc43a07e85ec84c7de56c'}, {'id': 'nite3d20:0156:088C', 'ranges': [[2188, 2260]], 'sha256': 'b2e7d530698f1b72d4ccdebfbcab9e76ec5f4a90ac49349ac84091209aea5ade'}, {'id': 'nite3d20:0156:012A', 'ranges': [[298, 335]], 'sha256': 'ac3cea5fb3a21874a4de625a9a73ad3e214d4724b88a61766813c09458a3811b'}, {'id': 'nite3d20:0156:0150', 'ranges': [[336, 365]], 'sha256': '61ef05717d924d9122b0bd01fca14f67442aa32973be68b1c9f3434d76e1dc07'}]
def verify(raw):
 if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError("Unknown source hash; no address claims permitted")
 image=raw[struct.unpack_from("<H",raw,8)[0]*16:]
 for s in SPECS:
  body=b"".join(image[0x156*16+a:0x156*16+b] for a,b in s["ranges"])
  if hashlib.sha256(body).hexdigest()!=s["sha256"]:raise ValueError("VGA body mismatch")
 if struct.unpack_from("<HH",image,0x2771*16+0x12c)!=(0xa000,0xa400):raise ValueError("Initial page words mismatch")
 pairs={(80*y+(x>>2),1<<(x&3)) for y in range(200) for x in range(320)}
 if len(pairs)!=64000:raise ValueError("Synthetic visible-coordinate alias")
 cx=768;writes=0
 while True:
  old=cx;cx=(cx-1)&65535
  if old==0:break
  writes+=1
 if writes!=768 or cx!=65535:raise ValueError("Palette loop contract mismatch")
 return {"bounded_VGA_bodies_verified":len(SPECS),"synthetic_coordinate_cases":64000,"palette_write_components":768,"palette_final_CX":"FFFF","scope":"local instruction contracts; coordinate tests are synthetic","raw_A000_alone_proves_image":False,"paired_renderer_parity_proven":False}
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("unpacked_exe");args=p.parse_args()
 try:print(json.dumps(verify(Path(args.unpacked_exe).read_bytes()),indent=2))
 except (ValueError,OSError) as e:p.exit(2,str(e)+"\n")

