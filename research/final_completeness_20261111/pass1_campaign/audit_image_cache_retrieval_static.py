"""Reproduce bounded static evidence; not an execution/semantic-equivalence test."""
import argparse, csv, hashlib, json
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument('image'); p.add_argument('inventory'); p.add_argument('out')
    a = p.parse_args(); image = Path(a.image).read_bytes()
    inv = Path(a.inventory); rows = json.loads(inv.read_text(encoding='utf-8'))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    chosen = []; gaps = []
    for lo, hi, name in [(0x350, 0x3ce, 'xms_read_to_conventional'),
                          (0x402, 0x4d7, 'image_cache_slot_fill')]:
        rr = sorted((r for r in rows if r['cs'] == 0x768 and lo <= r['ip'] < hi), key=lambda r:r['ip'])
        cursor = lo
        for r in rr:
            raw = bytes.fromhex(r['bytes']); off = 0x7680+r['ip']
            assert r['ip'] >= cursor, (name, cursor, r['ip'])
            if r['ip'] != cursor:
                gaps.append(dict(start=0x7680+cursor,end_exclusive=off,bytes=image[0x7680+cursor:off].hex(),status='Uncovered by retained inventory; not proven padding'))
            assert r['image_offset'] == off and image[off:off+len(raw)] == raw
            cursor = r['ip'] + len(raw)
            chosen.append(dict(function=name, cs='0768', ip='%04X'%r['ip'], image_offset=off,
                               bytes=r['bytes'], mnemonic=r['mnemonic'], operands=r['operands']))
        assert cursor == hi, (name, cursor, hi)
    anchors = {0x476:'66837c0200', 0x47b:'7e19', 0x47d:'680020',
               0x496:'680020', 0x49f:'f7d8', 0x4a1:'83d200', 0x4a4:'f7da',
               0x43b:'72de'}
    for ip, hx in anchors.items():
        if hx: assert image[0x7680+ip:0x7680+ip+len(bytes.fromhex(hx))] == bytes.fromhex(hx)
    with (out/'instructions.csv').open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(chosen[0])); w.writeheader(); w.writerows(chosen)
    (out/'reachable.asm').write_text('\n'.join('%s:%s %-16s %-7s %s'%(r['cs'],r['ip'],r['bytes'],r['mnemonic'],r['operands']) for r in chosen)+'\n', encoding='utf-8')
    result = dict(status='PARTIAL', method='Inventory bytes checked against canonical image; no independent decoding or runtime replay in this batch',
                  image_sha256=hashlib.sha256(image).hexdigest(), inventory_sha256=hashlib.sha256(inv.read_bytes()).hexdigest(),
                  instructions=len(chosen), instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in chosen), gaps=gaps,
                  native_scenarios_added=0, deep_verified_bytes_added=0,
                  intervals=[dict(start=0x79d0,end_exclusive=0x7a4e),dict(start=0x7a82,end_exclusive=0x7b57)],
                  unresolved=['Independent decoder and original-instruction replay', 'XMS destination readback', 'Slot allocation sizes and renderer consumers', 'Native zero/negative marker retrieval'])
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))

if __name__ == '__main__': main()

