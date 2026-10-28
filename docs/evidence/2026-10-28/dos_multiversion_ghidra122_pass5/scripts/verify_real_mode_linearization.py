"""Independent x86 ES:BX loads for proposed real-mode address expression."""
from pathlib import Path
import json,random,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_AX
root=Path(__file__).resolve().parent.parent;rng=random.Random(20261028)
pairs=[(s,o) for s in (0,1,0x1000,0x31fd,0x3771,0xffff) for o in (0,1,2,0x1234,0xffff)]+[(rng.randrange(65536),rng.randrange(65536)) for _ in range(64)];results=[]
for seg,off in pairs:
 physical=(seg<<4)+off;assert not 0x10800<=physical<0x1080b
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);code=b'\xb8'+struct.pack('<H',seg)+b'\x8e\xc0\xbb'+struct.pack('<H',off)+b'\x26\x8a\x07';u.mem_write(0x10800,code);u.mem_write(physical,b'\xa5');u.reg_write(UC_X86_REG_CS,0x1000);u.emu_start(0x10800,0x10800+len(code),count=20);assert u.reg_read(UC_X86_REG_AX)&255==0xa5,(seg,off,physical);results.append({'segment':hex(seg),'offset':hex(off),'physical':hex(physical),'pass':True})
out={'scope':'SYNTHETIC_X86_REAL_MODE_ADDRESS_MODEL_CHECK','original_game_code':False,'cases':len(results),'passed':len(results),'hooks':False,'stubs':False,'results':results};(root/'pass5/evidence/linearization_synthetic.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2))
