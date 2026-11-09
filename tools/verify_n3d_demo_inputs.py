"""Read-only exact-source DEMO format inventory; not playback or parity acceptance."""
from pathlib import Path
import json,struct,hashlib,argparse
SPECS={'DEMO.1': {'size': 2206, 'sha256': '25ae7e97f61d19bc3fa61d630ec13b9614a4f3193da84f7c1a3c3d519f795840', 'records': 275}, 'DEMO.2': {'size': 4198, 'sha256': 'deb7fe959b6b1c9f0f7f4a793a40e0ef75873b436c715bd9f74d4ef965ac304d', 'records': 524}, 'DEMO.3': {'size': 3382, 'sha256': '8cc9899520b0c60aabba7fd73cb38025bfb0978bd31eb20551bcf5555e4939e1', 'records': 422}}
def verify(name,raw):
    spec=SPECS[name]
    if len(raw)!=spec['size'] or hashlib.sha256(raw).hexdigest()!=spec['sha256']:raise ValueError('DEMO identity mismatch: '+name)
    if (len(raw)-6)%8:raise ValueError('Record framing mismatch')
    records=list(struct.iter_unpack('<HHI',raw[6:]));assert len(records)==spec['records']
    return {'file':name,'records':len(records),'timing_words':struct.unpack('<3H',raw[:6]),'fire_flag_records':sum(bool(r[1]&0x80) for r in records),'scope':'Exact data identity/framing only; playback completion and RNG order unproven'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('game_directory');a=p.parse_args()
    try:print(json.dumps([verify(n,(Path(a.game_directory)/n).read_bytes()) for n in SPECS],indent=2))
    except (ValueError,OSError) as e:p.exit(2,str(e)+'\n')

