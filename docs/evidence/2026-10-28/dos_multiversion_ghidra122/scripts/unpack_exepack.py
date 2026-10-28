from pathlib import Path
import struct,json,hashlib,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/dosbox-n3d(10)/nite3/dos/N3D-E-20.EXE'); b=p.read_bytes();h=struct.unpack_from('<14H',b); start=h[4]*16; stub=start+h[11]*16
ip,cs,_,packsize,sp,ss,paras,sig=struct.unpack_from('<8H',b,stub);assert sig==0x4252
src=stub-1;out=bytearray(paras*16);dst=len(out)-1;commands=0
while b[src]==255:src-=1
while True:
 cmd=b[src];src-=1;count=struct.unpack_from('<H',b,src-1)[0];src-=2
 assert dst-count+1>=0
 if cmd&254==0xb0:
  out[dst-count+1:dst+1]=bytes([b[src]])*count;src-=1
 elif cmd&254==0xb2:
  out[dst-count+1:dst+1]=b[src-count+1:src+1];src-=count
 else:raise ValueError((hex(cmd),src,dst))
 dst-=count;commands+=1
 if cmd&1:break
# EXEPACK leaves initial uncompressed bytes in place.
assert src-start==dst,(src-start,dst)
out[:dst+1]=b[start:src+1]
# Relocation groups from the offset encoded by MOV SI,imm16 in this stub.
assert b[stub+0xa1:stub+0xa4]==bytes.fromhex('be3201'),b[stub+0xa1:stub+0xa4].hex()
r=stub+0x132;rel=[]
for seg in range(16):
 n=struct.unpack_from('<H',b,r)[0];r+=2
 for j in range(n):
  off=struct.unpack_from('<H',b,r)[0];r+=2;rel.append((off,seg*0x1000))
assert r<=len(b)
headsize=(28+4*len(rel)+15)//16*16;size=headsize+len(out)
header=bytearray(headsize);struct.pack_into('<14H',header,0,0x5a4d,size%512,(size+511)//512,len(rel),headsize//16,h[5],h[6],ss,sp,0,ip,cs,28,0)
for i,(off,seg) in enumerate(rel):struct.pack_into('<HH',header,28+4*i,off,seg)
d=Path('analysis/inputs');d.mkdir(exist_ok=True);target=d/(sys.argv[2] if len(sys.argv)>2 else 'N3D20-unpacked.exe');target.write_bytes(header+out)
print(json.dumps({'packed_sha256':hashlib.sha256(b).hexdigest(),'unpacked_sha256':hashlib.sha256(header+out).hexdigest(),'payload_bytes':len(out),'relocations':len(rel),'entry':'%04x:%04x'%(cs,ip),'commands':commands,'remaining_raw_bytes':dst+1,'relocation_end':r,'source_bytes':len(b)},indent=2))
