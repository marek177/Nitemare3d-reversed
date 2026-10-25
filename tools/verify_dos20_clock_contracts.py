"""Read-only SHA-gated verification of seven bounded DOS20 clock bodies.
Checks byte streams and explicit arithmetic examples, not reachability or parity.
"""
import hashlib,struct,json,argparse
from pathlib import Path
SOURCE_SHA = "5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3"
SPECS = [{'function_id': 'nite3d20:0BCC:0002', 'segment': 3020, 'ranges': [[2, 39]], 'instruction_stream_sha256': '4c4418854c5d6ef749d9c379c6f868d41c466cb53dc96271564c36b9a2229750'}, {'function_id': 'nite3d20:0BCC:0074', 'segment': 3020, 'ranges': [[116, 131], [132, 291]], 'instruction_stream_sha256': '46d3abfafca64e01ffa6d623715071504f5f0fce874b1d166284851879e65760'}, {'function_id': 'nite3d20:0BDE:0018', 'segment': 3038, 'ranges': [[24, 107], [108, 148]], 'instruction_stream_sha256': 'b220befa6c79dd445c4cc163d217b7900febd7bb9803bc5e67eefc40451dd268'}, {'function_id': 'nite3d20:0BDE:0094', 'segment': 3038, 'ranges': [[148, 174]], 'instruction_stream_sha256': 'ff97d7c9e9e36e3832628a50590edbc64260e4c09f8a1d8df2a6e6e727e3a994'}, {'function_id': 'nite3d20:0BDE:00AE', 'segment': 3038, 'ranges': [[174, 212]], 'instruction_stream_sha256': '4cb3ef4aa8493b61cbe8f300353ea2233c786c79965d976a526e84918c3b1791'}, {'function_id': 'nite3d20:0BDE:00D4', 'segment': 3038, 'ranges': [[212, 275]], 'instruction_stream_sha256': 'c8a93bed732866f6942cba54a9d81757f77756207aca51878663bf6071252e69'}, {'function_id': 'nite3d20:0BDE:0114', 'segment': 3038, 'ranges': [[276, 341]], 'instruction_stream_sha256': '2799fb27b109a7f02b52917e609d8a70ee5c72d3b52d3a112f13f8bde59bb17a'}]
def bucket8(time,previous,sequence):
 q=((time<<3)&0xffffffff)//1000
 return (q,(sequence+1)&0xffffffff) if q!=previous else (previous,sequence)
def rate_bucket(time,rate,previous,sequence):
 rate=rate&65535;factor=(rate if rate<32768 else rate-65536)&0xffffffff
 q=((factor*time)&0xffffffff)//1000
 return (q,(sequence+1)&0xffffffff) if q!=previous else (previous,sequence)
def verify(raw):
 if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError("Unknown source hash; address claims rejected")
 header=struct.unpack_from("<H",raw,8)[0]*16;image=raw[header:]
 for spec in SPECS:
  s=spec["segment"];stream=b"".join(image[s*16+a:s*16+b] for a,b in spec["ranges"])
  if hashlib.sha256(stream).hexdigest()!=spec["instruction_stream_sha256"]:raise ValueError("Instruction stream mismatch")
 checks=[bucket8(1000,0,7)==(8,8),bucket8(0x20000000,99,7)==(0,8),bucket8(1000,8,7)==(8,7),rate_bucket(4000,25,0,7)==(100,8),bucket8(1000,0,0xffffffff)==(8,0)]
 if not all(checks):raise ValueError("Synthetic contract examples failed")
 return {"bounded_clock_bodies_verified":len(SPECS),"synthetic_contract_examples":len(checks),"runtime_edge_cases_tested":False,"IRQ_rate_proven":False,"full_parity_proven":False,"scope":"known local instruction streams plus arithmetic examples; external dependencies remain open"}
if __name__=="__main__":
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("unpacked_exe");args=parser.parse_args()
 try:print(json.dumps(verify(Path(args.unpacked_exe).read_bytes()),indent=2))
 except (ValueError,OSError) as e:parser.exit(2,str(e)+"\n")

