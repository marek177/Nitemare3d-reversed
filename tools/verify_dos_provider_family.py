"""Read-only exact resolver-family check for eight hash-pinned DOS executables.
Manifest: JSON list of {"binary_id": "nite3d20", "path": "local-unpacked.exe"}.
Requires all eight images; no original game files are distributed.
"""
import json,hashlib,struct,argparse
from pathlib import Path
SPECS = {'local_dos_12': {'sha256': '59894d010295ff943225a97dd38eebf2bef61470f44dfded328c5b46a2fdf919', 'segment': 1858, 'offset': 1932}, 'local_dos_cd': {'sha256': '5e33e621ecbc51f68bfbc798ed7a6c28a6b0b9a2b873a56447aaed6034f92eea', 'segment': 1895, 'offset': 1932}, 'nite3d10': {'sha256': '3bfaf8a788280dcb2d4420e389b00a36b3dfd57bc241641ef443ba8489cda5f3', 'segment': 1849, 'offset': 1520}, 'nite3d11': {'sha256': 'a32185b8f26abe1ffcff3504f7b7f1fff33765a712f5e410b84847e3270d68bb', 'segment': 1858, 'offset': 1920}, 'nite3d15': {'sha256': 'c5a41b2f8dc4649dc09fbda5b14da0d221c8fef7d0bf3566236b0d7d105e55d3', 'segment': 1863, 'offset': 1930}, 'nite3d17': {'sha256': 'b2cf8d62c0173fca00884ce111b8925e71c169638d7da1a0e156b8da132be56c', 'segment': 1873, 'offset': 1926}, 'nite3d19': {'sha256': 'd79c515d736da385cc27d78e37206b4902efb8e2648a83062b5d474474eca6fc', 'segment': 1895, 'offset': 1930}, 'nite3d20': {'sha256': '5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3', 'segment': 1896, 'offset': 1924}}
CANONICAL = bytes.fromhex("558becb80043cd2fa8807414b81043cd2f891e00008c060000b80100e9040090b80000c9cb")
def verify_one(binary_id,raw):
 if binary_id not in SPECS:raise ValueError("Unknown binary id")
 spec=SPECS[binary_id]
 if hashlib.sha256(raw).hexdigest()!=spec["sha256"]:raise ValueError("Source hash mismatch; no address assertions permitted")
 header=struct.unpack_from("<H",raw,8)[0]*16;address=header+spec["segment"]*16+spec["offset"];code=bytearray(raw[address:address+37])
 if len(code)!=37:raise ValueError("Short code span")
 lo=struct.unpack_from("<H",code,19)[0];hi=struct.unpack_from("<H",code,23)[0]
 if hi!=lo+2:raise ValueError("Slot pair mismatch")
 for i in (19,20,23,24):code[i]=0
 if bytes(code)!=CANONICAL:raise ValueError("Non-address instruction bytes differ")
 return {"binary_id":binary_id,"source_sha256":spec["sha256"],"segment":spec["segment"],"offset":spec["offset"],"slot_offset":lo,"slot_segment":hi,"status":"VERIFIED_STATIC"}
def main(manifest):
 items=json.loads(Path(manifest).read_text(encoding="utf-8"))
 if len(items)!=8 or {x["binary_id"] for x in items}!=set(SPECS):raise ValueError("Manifest must contain exactly all eight distinct known images")
 result=[verify_one(x["binary_id"],Path(x["path"]).read_bytes()) for x in items]
 return {"matched_versions":len(result),"canonical_code_sha256":hashlib.sha256(CANONICAL).hexdigest(),"allowed_changes":"only two adjacent absolute data-slot displacement words","scope":"37-byte resolver algorithm only; no runtime provider or gameplay equivalence","results":result}
if __name__=="__main__":
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("manifest");args=parser.parse_args()
 try:print(json.dumps(main(args.manifest),indent=2))
 except (ValueError,OSError,KeyError) as e:parser.exit(2,str(e)+"\n")

