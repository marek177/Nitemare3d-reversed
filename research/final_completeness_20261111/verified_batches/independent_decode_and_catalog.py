"""Decode campaign instructions using iced-x86 1.21.0, create bounded catalog.
Usage: python independent_decode_and_catalog.py DECODER_DIR OUTPUTS_DIR
Current campaign map is NOT the original PASS320 ledger.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def readjson(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def csvout(p,rows):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    decoder_dir,root=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder_dir))
    from iced_x86 import Decoder, Formatter, FormatterSyntax, FlowControl
    image=(root/'unpack/reproduced_image.bin').read_bytes()
    if sha(image)!='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297':raise ValueError('wrong image')
    helper=readjson(root/'worx_helper/helper_evidence.json')
    leaf=readjson(root/'worx_leafs/leaf_evidence.json')
    dataflow=readjson(root/'worx_dataflow/dataflow_evidence.json')
    sources=[('helper_31ca',root/'worx_helper/instructions.csv')]
    sources += [(f['name'],root/'worx_leafs'/(f['name']+'.csv')) for f in leaf['functions']]
    sources += [(f['name'],root/'worx_dataflow'/(f['name']+'.csv')) for f in dataflow['functions']]
    int63 = readjson(root/'int63/int63_evidence.json') if (root/'int63/int63_evidence.json').exists() else None
    if int63:sources.append(('int63_dispatcher',root/'int63/dispatcher_instructions.csv'))
    wave = readjson(root/'wave_header/wave_header_evidence.json') if (root/'wave_header/wave_header_evidence.json').exists() else None
    if wave:sources += [(f['name'],root/'wave_header'/(f['name']+'.csv')) for f in wave['functions']]
    read_replay = readjson(root/'read_replay/read_replay_evidence.json') if (root/'read_replay/read_replay_evidence.json').exists() else None
    if read_replay:sources.append((read_replay['function']['name'],root/'read_replay/instructions.csv'))
    audio=readjson(root/'dos_audio_lifecycle/summary.json') if (root/'dos_audio_lifecycle/summary.json').exists() else None
    if audio:sources += [(f['name'],root/'dos_audio_lifecycle'/(f['name']+'.csv')) for f in audio['functions']]
    sample_irq=readjson(root/'dos_sample_irq/summary.json') if (root/'dos_sample_irq/summary.json').exists() else None
    if sample_irq:sources.append(('sample_irq',root/'dos_sample_irq/sample_irq.csv'))
    fmt=Formatter(FormatterSyntax.INTEL); decoded=[]; code_owners={}; functions=[]
    for name,path in sources:
        rows=readcsv(path); byte_count=0
        for row in rows:
            a=int(row['image_offset']);ip=int(row['ip']);cs=int(row['cs']);code=bytes.fromhex(row['bytes'])
            if image[a:a+len(code)]!=code or a!=16*cs+ip:raise ValueError('source mismatch')
            ins=Decoder(16,code,ip=ip).decode()
            if ins.is_invalid or ins.len!=len(code):raise ValueError('independent length/validity conflict at '+hex(a))
            for pos in range(a,a+len(code)):
                if pos in code_owners:raise ValueError('duplicate code ownership')
                code_owners[pos]=name
            target=''
            if ins.flow_control in (FlowControl.CALL,FlowControl.UNCONDITIONAL_BRANCH,FlowControl.CONDITIONAL_BRANCH):target=cs*16+ins.near_branch_target
            old_text=(row['mnemonic']+' '+row['operands']) if 'mnemonic' in row else 'new independent decode; no historical text imported'
            decoded.append(dict(function=name,image_offset=a,cs=cs,ip=ip,bytes=code.hex(),iced_text=fmt.format(ins),historical_text=old_text,flow_control=ins.flow_control,direct_target_image=target,status='PARTIAL'))
            byte_count+=len(code)
        functions.append(dict(name=name,start=min(int(r['image_offset']) for r in rows),last_instruction_end=max(int(r['image_offset'])+len(bytes.fromhex(r['bytes'])) for r in rows),instruction_bytes=byte_count,instructions=len(rows),independent_boundary_check='PASS',semantic_status='PARTIAL',pass320_membership='UNKNOWN'))
    data_sources=[('worx_helper',helper['data_intervals']),('worx_dataflow',dataflow['data_intervals'])]
    if int63:
        data_sources.append(('int63_local',[
            dict(start=int63['candidate_table_start'],end_exclusive=int63['candidate_table_end_exclusive']),
            dict(start=0x17cb4,end_exclusive=0x17cb6),
            dict(start=0x18cd2,end_exclusive=0x18cd6),
            dict(start=0x19ac4,end_exclusive=0x19ac6)]))
    if wave:data_sources.append(('wave_header',[dict(start=wave['header_start'],end_exclusive=wave['header_end_exclusive'])]))
    xms_fields = root/'dos_xms_layout/data_fields.csv'
    if xms_fields.exists():
        typed=[]
        for row in readcsv(xms_fields):
            a=int(row['image_start']);b=int(row['image_end_exclusive'])
            if b-a!=int(row['size']) or sha(image[a:b])!=row['range_sha256']:
                raise ValueError('XMS field bounds/hash conflict')
            typed.append(dict(start=a,end_exclusive=b))
        data_sources.append(('dos_xms_layout',typed))
    vector_fields=root/'dos_vector63/data_intervals.csv'
    if vector_fields.exists():
        typed=[]
        for row in readcsv(vector_fields):
            a=int(row['start']);b=int(row['end_exclusive'])
            if sha(image[a:b])!=row['range_sha256']:raise ValueError('vector field hash conflict')
            typed.append(dict(start=a,end_exclusive=b))
        data_sources.append(('dos_vector63',typed))
    data_owners={}
    if sample_irq:data_sources.append(('dos_sample_irq',sample_irq['standalone_data_intervals']))
    lookup_fields=root/'dos_sample_lookup/data_intervals.csv'
    if lookup_fields.exists():
        typed=[]
        for row in readcsv(lookup_fields):
            a=int(row['start']);b=int(row['end_exclusive'])
            if sha(image[a:b])!=row['range_sha256']:raise ValueError('sample lookup hash conflict')
            typed.append(dict(start=a,end_exclusive=b))
        data_sources.append(('dos_sample_lookup',typed))
    if audio:
        typed=[]
        for row in readcsv(root/'dos_audio_lifecycle/data_intervals.csv'):
            a=int(row['start']);b=int(row['end_exclusive'])
            if sha(image[a:b])!=row['range_sha256']:raise ValueError('audio field hash conflict')
            typed.append(dict(start=a,end_exclusive=b))
        data_sources.append(('dos_audio_lifecycle',typed))
    for evidence,rows in data_sources:
        for row in rows:
            a=row['start'];b=row['end_exclusive']
            for pos in range(a,b):
                if pos in code_owners:raise ValueError('code/data conflict')
                data_owners.setdefault(pos,set()).add(evidence)
    # Partition every image byte, preserving local evidence scope and all unknowns.
    def key(pos):
        if pos in code_owners:return ('EXECUTABLE_CODE','PARTIAL',code_owners[pos])
        if pos in data_owners:return ('DATA','PARTIAL',';'.join(sorted(data_owners[pos])))
        return ('UNKNOWN_CONTENT','UNKNOWN','not_assessed_in_this_campaign')
    ranges=[];start=0;prior=key(0)
    for pos in range(1,len(image)+1):
        current=key(pos) if pos<len(image) else None
        if current!=prior:
            ranges.append(dict(start=start,end_exclusive=pos,length=pos-start,primary_type=prior[0],status=prior[1],evidence=prior[2],sha256=sha(image[start:pos]),pass320_membership='UNKNOWN'))
            start=pos;prior=current
    totals={}
    for row in ranges:totals[row['primary_type']]=totals.get(row['primary_type'],0)+row['length']
    if sum(r['length'] for r in ranges)!=len(image):raise ValueError('partition error')
    dest=root/'campaign_catalog';dest.mkdir(exist_ok=True)
    csvout(dest/'independent_instructions.csv',decoded)
    csvout(dest/'functions.csv',functions)
    csvout(dest/'byte_intervals.csv',ranges)
    (dest/'byte_intervals.json').write_text(json.dumps(ranges,indent=2)+'\n',encoding='utf-8')
    result=dict(image_sha256=sha(image),image_bytes=len(image),decoder='iced-x86 1.21.0, 16-bit',decoder_native_files=[dict(path=p.name,sha256=sha(p.read_bytes())) for p in decoder_dir.rglob('*.pyd')],functions=len(functions),independent_instruction_count=len(decoded),independent_instruction_bytes=len(code_owners),data_bytes_with_local_evidence=len(data_owners),primary_type_bytes=totals,interval_count=len(ranges),original_pass320_ledger_imported=False,new_deep_verified_bytes=0,runtime_tests=0,scope='Current campaign partition only; PARTIAL does not mean closed semantics; UNKNOWN is not historical reclassification')
    result['controlled_instruction_replay_cases'] = read_replay['controlled_replay_cases'] if read_replay else 0
    pit_replay_path=root/'dos_pit_replay/evidence.json'
    if pit_replay_path.exists():result['controlled_instruction_replay_cases'] += readjson(pit_replay_path)['controlled_replay_cases']
    pit_caller_replay_path=root/'dos_pit_caller_replay/evidence.json'
    if pit_caller_replay_path.exists():result['controlled_instruction_replay_cases'] += readjson(pit_caller_replay_path)['controlled_replay_cases']
    result['runtime_tests_scope'] = 'DOSBox-X/original-runtime tests only; controlled instruction replay counted separately'
    (dest/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
