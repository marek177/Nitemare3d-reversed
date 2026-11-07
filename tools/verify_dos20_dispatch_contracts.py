"""Read-only identity/span verifier for bounded DOS2 dispatcher contracts; not parity."""
from pathlib import Path
import hashlib,struct,json,argparse
SOURCE_SHA = '5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3'
SPANS = {'0BDE:03C8': {'segment': 3038, 'start': 968, 'end_exclusive': 1238, 'span_sha256': '032af1da065a6cc57667d1215cdd61ad0d3715ebcc58f0a3e97686c35f665afe', 'instructions': 92}, '0BDE:0370': {'segment': 3038, 'start': 880, 'end_exclusive': 967, 'span_sha256': '08283f8615a1d497a6c896155ef24664cdb7d580d3cae3bb70eee6f1f3cc5bf9', 'instructions': 26}, '083D:1CFC': {'segment': 2109, 'start': 7420, 'end_exclusive': 7625, 'span_sha256': 'b266de863e421bf6b3d11dd24350287086b59d9e8c0b25099fe83261fff6c882', 'instructions': 63}}
def verify(raw):
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Source SHA256 mismatch; address claims rejected')
    header=struct.unpack_from('<H',raw,8)[0]*16
    for name,spec in SPANS.items():
        begin=header+spec['segment']*16+spec['start'];end=header+spec['segment']*16+spec['end_exclusive']
        if hashlib.sha256(raw[begin:end]).hexdigest()!=spec['span_sha256']:raise ValueError('Span mismatch: '+name)
    return {'source_sha256':SOURCE_SHA,'verified_local_spans':len(SPANS),'scope':'Exact identity and bounded span hashes only; semantic claims require accompanying analysis/runtime evidence','whole_function_boundaries_proven':False,'paired_parity_proven':False}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('unpacked_exe');a=p.parse_args()
    try:print(json.dumps(verify(Path(a.unpacked_exe).read_bytes()),indent=2))
    except (ValueError,OSError) as e:p.exit(2,str(e)+'\n')

