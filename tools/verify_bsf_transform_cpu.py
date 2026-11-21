"""Original 0FBA:01B2 transform/checksum with separate sequential-memory oracle."""
import sys,json,hashlib,struct,base64,functools
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'goal-x20/work/deps'))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();H=lambda b:hashlib.sha256(b).hexdigest();assert H(raw)=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:];code=im[0xfba*16+0x1b2:0xfba*16+0x1f0];key=im[0x2771*16+0x2045:0x2771*16+0x2079];assert len(key)==52
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0xfba*16+0x1b2,code);writes=[]
u.hook_add(UC_HOOK_CODE,lambda m,a,n,z:m.emu_stop() if a==0x60000 else None)
u.hook_add(UC_HOOK_MEM_WRITE,lambda m,a,ad,n,v,z:writes.append((ad,n,v&((1<<(n*8))-1))))
digest=hashlib.sha256();cases=0
def run(data,offset=0x1000,ds=0x4000,ss=0x3000,df=False):
 global cases
 n=len(data);mem=bytearray(0x100000);mem[ss*16+0x2045:ss*16+0x2079]=key
 for i,x in enumerate(data):mem[ds*16+((offset+i)&65535)]=x
 u.mem_write(ss*16,bytes(mem[ss*16:ss*16+65536]))
 if ds!=ss:u.mem_write(ds*16,bytes(mem[ds*16:ds*16+65536]))
 checksum=0
 for i in range(n):
  addr=ds*16+((offset+i)&65535);checksum^=mem[addr];mem[addr]^=mem[ss*16+0x2045+i%52]
 expected=bytes(mem[ds*16+((offset+i)&65535)] for i in range(n))
 for reg,val in [(UC_X86_REG_CS,0xfba),(UC_X86_REG_DS,0x5555),(UC_X86_REG_SS,ss),(UC_X86_REG_ES,0x2222),(UC_X86_REG_AX,0xa55a),(UC_X86_REG_BP,0x1111),(UC_X86_REG_SI,0x3333),(UC_X86_REG_DI,0x4444),(UC_X86_REG_SP,0x8000),(UC_X86_REG_EFLAGS,0x202|(0x400 if df else 0))]:u.reg_write(reg,val)
 u.mem_write(ss*16+0x8000,struct.pack('<5H',0,0x6000,offset,ds,n));writes.clear();u.emu_start(0xfba*16+0x1b2,0xfffff,count=30+15*n)
 actual=bytes(u.mem_read(ds*16+((offset+i)&65535),1)[0] for i in range(n));assert actual==expected
 ax=u.reg_read(UC_X86_REG_AX);wantAH=((n-1)//52)>>8 if n else 0xa5;assert ax==(wantAH<<8)|checksum
 for reg,val in [(UC_X86_REG_DS,ss if n else 0x5555),(UC_X86_REG_SS,ss),(UC_X86_REG_ES,0x2222),(UC_X86_REG_BP,0x1111),(UC_X86_REG_SI,0x3333),(UC_X86_REG_DI,0x4444),(UC_X86_REG_SP,0x8004),(UC_X86_REG_CS,0x6000),(UC_X86_REG_IP,0)]:assert u.reg_read(reg)==val
 assert u.reg_read(UC_X86_REG_EFLAGS)&0x600==(0x200|(0x400 if df else 0))
 allowed={ds*16+((offset+i)&65535) for i in range(n)}|set(range(ss*16+0x7ff6,ss*16+0x8000))
 assert all(set(range(a,a+size))<=allowed for a,size,v in writes)
 assert len(writes)==(4+2*n+(1 if n else 0))
 digest.update(struct.pack('<HHHHHH',n,offset,ds,ss,ax,len(writes)&65535)+actual);cases+=1
 return actual,ax
for x in range(256):run(bytes([x]),df=bool(x&1))
for n in (0,2,51,52,53,54,103,104,105,255,256,65535):
 for off in (0x1000,0xfff0):run(bytes((i*73+n)&255 for i in range(n)),off,df=bool(n&1))
for off in (0x2044,0x2045,0x2078):run(bytes((i*17+3)&255 for i in range(104)),off,ds=0x3000)
D=R/'outputs/evidence/runtime/rng_episode3_p_20261107';cipher=(R/'work/runtime/game_rng_episode3_p_20261107/NITE3D.BSF').read_bytes()[:54];decoded,ax=run(cipher,0x3638,0x2771,0x2771);native=base64.b64decode(json.loads((D/'gate_endpoint_snapshot.json').read_text())['header_buffer']['result']['data_base64']);assert decoded==native and ax==0 and decoded[3]==1
for index in range(54):
 for bit in range(8):
  altered=bytearray(cipher);altered[index]^=1<<bit;out,result=run(altered,0x3638,0x2771,0x2771);want=bytearray(decoded);want[index]^=1<<bit;assert out==want and result==1<<bit
v={'status':'SYNTHETIC_ORIGINAL_CPU_PLUS_NATIVE_ENDPOINT_DATA_COMPARISON','cases':cases,'source_sha256':H(raw),'code_span_sha256':H(code),'key52_sha256':H(key),'transform':'In place byte[i] ^= SS:[2045+(i mod52)], SI wraps16 bits; AL is XOR of pre-transform bytes','nonzero_return':'DS=SS; AH=high byte of floor((count-1)/52); FAR consumes4 returnbytes, leaves6 argumentbytes','zero_return':'AL0,AH fixture preserved, incomingDS retained','preserved_fixture':'BP,SI,DI,SS,ES,IF/DF; allowed writes and exact write counts checked','domains':'all256 one-byte inputs; zero/boundary/65535 lengths; SI wrap; three key/buffer aliases with sequential-memory oracle','native_endpoint_header_byte_exact':True,'header_cipher_sha256':H(cipher),'header_decoded_sha256':H(decoded),'header_checksum_AL':ax,'header_offset3':decoded[3],'case_digest_sha256':digest.hexdigest(),'unicorn':unicorn.__version__,'scope':'No native transform entry/exit trace, no arbitrary stack/code aliases, IRQs or Win16/remake parity. Byte3 is the selector1 gate; broader feature/format meaning remainspartial.'}
O=R/'outputs/bsf_transform_20261107';O.mkdir(exist_ok=True);(O/'CPU_validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))

