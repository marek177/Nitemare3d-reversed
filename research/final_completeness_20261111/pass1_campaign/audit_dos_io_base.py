"""Close local I/O-base producer/consumer contracts without hardware execution.
Usage: python audit_dos_io_base.py IMAGE DECODER_DIR REFERENCE_ATLAS_CSV OUT_DIR
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,dep,atlas,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
spec=[('mixer_index0c_write',0x17dcc,0x17ddc),('mixer_index2e_write',0x17ddc,0x17df8),('mixer_index0a_write',0x17df8,0x17e08),('bios_tick_wait',0x18a31,0x18a46),('io_base_setter',0x1a44a,0x1a456),('io_base_getter',0x1a456,0x1a45c),('dsp_base_probe',0x1b768,0x1b7bb)]
def save(p,rows,fields=None):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,start,end in spec:
    rows=[];pos=start
    for ins in Decoder(16,b[start:end],ip=start-base):
        assert not ins.is_invalid
        rows.append(dict(image_offset=pos,cs=0x15bf,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==end and rows[-1]['bytes']=='c3'
    save(out/(name+'.csv'),rows)
    slots=[n for n in range(82) if struct.unpack_from('<H',b,base+0x2020+2*n)[0]==start-base]
    functions.append(dict(name=name,start=start,end_exclusive=end,instruction_bytes=end-start,instructions=len(rows),candidate_service_slots=slots,status='PARTIAL'))
refs=[r for r in csv.DictReader(atlas.open(encoding='utf-8-sig')) if int(r['cs'])==0x15bf and int(r['cs_offset'])==0x2df0]
assert len(refs)==21
save(out/'io_base_xrefs.csv',refs)
fields=[]
for name,start,size,typ in [('sound_io_base',base+0x2df0,2,'WORD_IO_port_base'),('device_mode_code',base+0x2010,2,'WORD_zero_extended_AL_on_setter_path')]:
    fields.append(dict(name=name,start=start,end_exclusive=start+size,type=typ,initial_bytes=b[start:start+size].hex(),range_sha256=hashlib.sha256(b[start:start+size]).hexdigest(),status='PARTIAL',pass320_membership='UNKNOWN'))
save(out/'data_intervals.csv',fields)
critical={0x1b768:'2ec706f02d0002',0x1b795:'2e8306f02d10',0x1b79b:'2e813ef02d0003',0x1b7af:'3caa',0x1a44a:'2e891ef02d32e42ea31020c3'}
for a,v in critical.items():assert b[a:a+len(bytes.fromhex(v))]==bytes.fromhex(v)
r=dict(image_sha256=h,functions=functions,total_instruction_bytes=sum(x['instruction_bytes'] for x in functions),fixed_base_reference_count=len(refs),probe_candidate_bases=list(range(0x200,0x300,0x10)),probe_failure_base=0x300,probe_failure_cf=1,probe_success_cf=0,probe_poll_count_per_candidate=200,getter_always_clears_cf=True,hardware_probe_executed=False,bios_tick_wrap_contract_closed=False,new_deep_verified_bytes=0,runtime_tests=0)
(out/'summary.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
