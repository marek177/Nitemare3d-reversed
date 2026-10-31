"""Read-only identity and bounded actor-switch table verifier; no parity claim."""
from pathlib import Path
import hashlib,struct,json,argparse
SOURCE_SHA = '5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3'
TARGETS = (3532, 3594, 3620, 3684, 3754, 3846, 3854, 3914, 3994, 4100, 4784, 4784, 4204, 4204, 4226, 4274, 4408, 4510, 4604, 4678, 4696, 4746)
def verify(raw):
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Source identity mismatch')
    h=struct.unpack_from('<H',raw,8)[0]*16;a=h+0x4c7*16
    prefix=bytes.fromhex('2ae48a470b3d15000f87190503c0932effa7a00d')
    if raw[a+0xd8b:a+0xd9f]!=prefix:raise ValueError('Selector/bound/index prefix mismatch')
    if tuple(struct.unpack_from('<22H',raw,a+0xda0))!=TARGETS:raise ValueError('Table mismatch')
    return {'entries':22,'distinct_encoded_targets':len(set(TARGETS)),'selector':'u8 byte, unsigned <=21 before doubling','default':'04C7:12B0','scope':'Exact source and bounded encoded table under this entry path; no global self-modifying-code or whole-game closure','paired_parity_proven':False}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('unpacked_exe');a=p.parse_args()
    try:print(json.dumps(verify(Path(a.unpacked_exe).read_bytes()),indent=2))
    except (ValueError,OSError) as e:p.exit(2,str(e)+'\n')

