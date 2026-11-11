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
    noncode=set();baseline_path=root/'pass320_recovered/noncode_baseline.csv'
    if baseline_path.exists():
        ledger=root/'pass320_recovered/source_ledgers/N3D_PASS320_INT63_COUNTER_WRAP_AUDIT.csv'
        if sha(ledger.read_bytes())!='8bf6afc62977ff68f6b7030288db48adb12cbba2d0157a14195f1708307830d2':raise ValueError('PASS320 ledger identity conflict')
        for row in readcsv(baseline_path):
            a=int(row['start']);b=int(row['end_exclusive'])
            if sha(image[a:b])!=row['range_sha256']:raise ValueError('PASS320 NON-CODE bounds/hash conflict')
            noncode.update(range(a,b))
        if len(noncode)!=57295:raise ValueError('PASS320 NON-CODE total conflict')
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
    io_base=readjson(root/'dos_io_base/summary.json') if (root/'dos_io_base/summary.json').exists() else None
    if io_base:sources += [(f['name'],root/'dos_io_base'/(f['name']+'.csv')) for f in io_base['functions']]
    irq_detection=readjson(root/'dos_irq_detection/summary.json') if (root/'dos_irq_detection/summary.json').exists() else None
    if irq_detection:sources += [(f['name'],root/'dos_irq_detection'/(f['name']+'.csv')) for f in irq_detection['functions']]
    key_labels=readjson(root/'pass1_key_labels/summary.json') if (root/'pass1_key_labels/summary.json').exists() else None
    if key_labels:sources.append(('key_label_selector',root/'pass1_key_labels/selector_instructions.csv'))
    bit_reverse=root/'bitmap_bit_reverse_replay/instructions.csv'
    if bit_reverse.exists():sources.append(('bitmap_bit_reverse',bit_reverse))
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
    record_table_fields=root/'pass1_record_tables/data_fields.csv'
    if record_table_fields.exists():
        typed=[]
        for row in readcsv(record_table_fields):
            a=int(row['start']);b=int(row['end_exclusive'])
            if sha(image[a:b])!=row['range_sha256']:raise ValueError('record table field hash conflict')
            typed.append(dict(start=a,end_exclusive=b))
        data_sources.append(('pass1_record_tables',typed))
    if key_labels:
        typed=[]
        for row in readcsv(root/'pass1_key_labels/data_fields.csv'):
            a=int(row['start']);b=int(row['end_exclusive'])
            if sha(image[a:b])!=row['range_sha256']:raise ValueError('key label field hash conflict')
            typed.append(dict(start=a,end_exclusive=b))
        data_sources.append(('pass1_key_labels',typed))
    if irq_detection:
        typed=[]
        for row in readcsv(root/'dos_irq_detection/data_intervals.csv'):
            a=int(row['start']);b=int(row['end_exclusive'])
            if sha(image[a:b])!=row['range_sha256']:raise ValueError('IRQ profile field hash conflict')
            typed.append(dict(start=a,end_exclusive=b))
        data_sources.append(('dos_irq_detection',typed))
    if io_base:
        typed=[]
        for row in readcsv(root/'dos_io_base/data_intervals.csv'):
            a=int(row['start']);b=int(row['end_exclusive'])
            if sha(image[a:b])!=row['range_sha256']:raise ValueError('I/O base field hash conflict')
            typed.append(dict(start=a,end_exclusive=b))
        data_sources.append(('dos_io_base',typed))
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
    # Explicit current sources. The old pass1_map_grid extent is superseded:
    # flags_map_boundary supplies the corrected whole map, including both bytes.
    current_pass1_sources=['pass1_key_labels','pass1_record_tables','pass1_records28','pass1_error_path','pass1_crt_cleanup',
        'pass1_crt_streams','pass1_crt_parallel','pass1_crt_commit','pass1_crt_errors',
        'pass1_resource_buffer','pass1_resource_directory','pass1_graphics_blocks',
        'pass1_byte_grid','pass1_guard_slots','pass1_allocated_pointer_table',
        'pass1_menu_records','pass1_menu_records_more','pass1_menu_tail',
        'pass1_ui_callbacks','pass1_dynamic_ui','pass1_grid_ui','pass1_flags_map_boundary','pass1_ui_strings','pass1_segment_globals','pass1_crt_hook_slots','pass1_message_fields','pass1_split_strings','pass1_crt_program_pointer','pass1_id_card_selector']
    typed_catalog=[]
    for evidence in current_pass1_sources:
        path=root/evidence/'data_fields.csv'
        if not path.exists():raise ValueError('missing current evidence '+str(path))
        typed=[]
        for row in readcsv(path):
            a,b=int(row['start']),int(row['end_exclusive'])
            if b-a!=int(row['length']) or sha(image[a:b])!=row['range_sha256']:
                raise ValueError('current data field conflict '+evidence)
            if any(p not in noncode for p in range(a,b)):
                raise ValueError('PASS1 data outside baseline '+evidence)
            typed.append(dict(start=a,end_exclusive=b))
            typed_catalog.append(dict(source=evidence,source_sha256=sha(path.read_bytes()),
                name=row.get('name',''),start=a,end_exclusive=b,length=b-a,
                type=row.get('type',''),status='PARTIAL',range_sha256=sha(image[a:b])))
        data_sources.append((evidence,typed))
    csvout(root/'campaign_catalog/current_pass1_data_types.csv',typed_catalog)
    for evidence,rows in data_sources:
        for row in rows:
            a=row['start'];b=row['end_exclusive']
            for pos in range(a,b):
                if pos in code_owners:raise ValueError('code/data conflict')
                data_owners.setdefault(pos,set()).add(evidence)
    # Partition every image byte, preserving local evidence scope and all unknowns.
    def key(pos):
        membership=('NON_CODE_BASELINE' if pos in noncode else 'OUTSIDE_NON_CODE_BASELINE') if baseline_path.exists() else 'UNKNOWN'
        if pos in code_owners:return ('EXECUTABLE_CODE','PARTIAL',code_owners[pos],membership)
        if pos in data_owners:return ('DATA','PARTIAL',';'.join(sorted(data_owners[pos])),membership)
        return ('UNKNOWN_CONTENT','UNKNOWN','not_assessed_in_this_campaign',membership)
    ranges=[];start=0;prior=key(0)
    for pos in range(1,len(image)+1):
        current=key(pos) if pos<len(image) else None
        if current!=prior:
            ranges.append(dict(start=start,end_exclusive=pos,length=pos-start,primary_type=prior[0],status=prior[1],evidence=prior[2],sha256=sha(image[start:pos]),pass320_membership=prior[3]))
            start=pos;prior=current
    totals={}
    for row in ranges:totals[row['primary_type']]=totals.get(row['primary_type'],0)+row['length']
    if sum(r['length'] for r in ranges)!=len(image):raise ValueError('partition error')
    dest=root/'campaign_catalog';dest.mkdir(exist_ok=True)
    if baseline_path.exists():
        for f in functions:
            addresses={p for r in decoded if r['function']==f['name'] for p in range(r['image_offset'],r['image_offset']+len(bytes.fromhex(r['bytes'])))}
            f['pass320_membership']='NO_INSTRUCTION_BYTES_IN_NONCODE' if not addresses&noncode else 'INSTRUCTION_BYTE_OVERLAP'
    csvout(dest/'independent_instructions.csv',decoded)
    csvout(dest/'functions.csv',functions)
    csvout(dest/'byte_intervals.csv',ranges)
    (dest/'byte_intervals.json').write_text(json.dumps(ranges,indent=2)+'\n',encoding='utf-8')
    result=dict(image_sha256=sha(image),image_bytes=len(image),decoder='iced-x86 1.21.0, 16-bit',decoder_native_files=[dict(path=p.name,sha256=sha(p.read_bytes())) for p in decoder_dir.rglob('*.pyd')],functions=len(functions),independent_instruction_count=len(decoded),independent_instruction_bytes=len(code_owners),data_bytes_with_local_evidence=len(data_owners),primary_type_bytes=totals,interval_count=len(ranges),original_pass320_ledger_imported=False,new_deep_verified_bytes=0,runtime_tests=0,scope='Current campaign partition only; PARTIAL does not mean closed semantics; UNKNOWN is not historical reclassification')
    result['controlled_instruction_replay_cases'] = read_replay['controlled_replay_cases'] if read_replay else 0
    result['original_pass320_ledger_imported']=baseline_path.exists()
    if baseline_path.exists():
        result['original_noncode_bytes']=len(noncode)
        result['original_noncode_intersection_code_bytes']=len(noncode&set(code_owners))
        result['original_noncode_intersection_data_bytes']=len(noncode&set(data_owners))
    pit_replay_path=root/'dos_pit_replay/evidence.json'
    if pit_replay_path.exists():result['controlled_instruction_replay_cases'] += readjson(pit_replay_path)['controlled_replay_cases']
    pit_caller_replay_path=root/'dos_pit_caller_replay/evidence.json'
    if pit_caller_replay_path.exists():result['controlled_instruction_replay_cases'] += readjson(pit_caller_replay_path)['controlled_replay_cases']
    dsp_probe_replay_path=root/'dos_dsp_probe_replay/evidence.json'
    if dsp_probe_replay_path.exists():result['controlled_instruction_replay_cases'] += readjson(dsp_probe_replay_path)['controlled_replay_cases']
    key_replay_path=root/'pass1_key_selector_replay/evidence.json'
    if key_replay_path.exists():result['controlled_instruction_replay_cases'] += readjson(key_replay_path)['controlled_replay_cases']
    key_caller_replay_path=root/'pass1_key_caller_replay/evidence.json'
    if key_caller_replay_path.exists():result['controlled_instruction_replay_cases'] += readjson(key_caller_replay_path)['controlled_replay_cases']
    for replay_folder in ['crt_error_replay','bitmap_bit_reverse_replay']:
        replay_summary=readjson(root/replay_folder/'summary.json')
        if replay_summary['failures']!=0:raise ValueError('failed replay batch')
        result['controlled_instruction_replay_cases']+=replay_summary['cases']
    latest_map=root/'pass1_id_card_selector/noncode_intervals.csv'
    latest_partial=set()
    for row in readcsv(latest_map):
        if row['status']=='PARTIAL':latest_partial.update(range(int(row['start']),int(row['end_exclusive'])))
    if not (noncode&set(data_owners))<=latest_partial:
        raise ValueError('central typed data contradict latest PASS1 status')
    result['latest_pass1_map_sha256']=sha(latest_map.read_bytes())
    result['pass1_partial_bytes_without_typed_data']=len(latest_partial-set(data_owners))
    relocation_bytes=set()
    for row in readcsv(root/'unpack/relocations.csv'):
        p=int(row['image_offset']);relocation_bytes.update([p,p+1])
    untyped=latest_partial-set(data_owners)
    if not untyped<=relocation_bytes:raise ValueError('unexplained PARTIAL data gap')
    (dest/'untyped_partial_relocation_check.json').write_text(json.dumps(dict(
        bytes=len(untyped),all_at_verified_relocation_sites=True,image_offsets=sorted(untyped)),indent=2)+'\n')
    result['runtime_tests_scope'] = 'DOSBox-X/original-runtime tests only; controlled instruction replay counted separately'
    (dest/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
