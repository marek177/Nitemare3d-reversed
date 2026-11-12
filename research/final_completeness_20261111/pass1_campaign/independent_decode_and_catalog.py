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
    for folder in ('episode_selector_replay','xms_request_replay','game_start_replay','sound_xms_cache_replay'):
        for f in readjson(root/folder/'summary.json')['functions']:sources.append((f['name'],root/folder/(f['name']+'.csv')))
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
    prompt_instructions=root/'pass1_prompt_fields/instructions.csv'
    if prompt_instructions.exists():sources.append(('prompt_helper_0720',prompt_instructions))
    runtime_lookup=root/'pass1_runtime_messages/lookup_instructions.csv'
    if runtime_lookup.exists():sources.append(('crt_runtime_message_lookup',runtime_lookup))
    for trig_name in ['sin','cos']:
        trig_path=root/'pass1_trig'/(trig_name+'_instructions.csv')
        if trig_path.exists():sources.append(('fixed_point_'+trig_name,trig_path))
    tangent_path=root/'pass1_tangent/tangent_magnitude_instructions.csv'
    if tangent_path.exists():sources.append(('signed_tangent_magnitude',tangent_path))
    angle_path=root/'angle_lookup/instructions.csv'
    if angle_path.exists():sources.append(('integer_ratio_angle_lookup',angle_path))
    debug_path=root/'pass1_debug_logger/instructions.csv'
    if debug_path.exists():sources.append(('debug_logger',debug_path))
    dsp_path=root/'pass1_dsp_status/instructions.csv'
    if dsp_path.exists():sources.append(('dsp_status_wrapper',dsp_path))
    music_path=root/'pass1_music_selector/instructions.csv'
    if music_path.exists():sources.append(('music_selection_dispatch',music_path))
    music_resource_path=root/'pass1_music_resource/instructions.csv'
    if music_resource_path.exists():sources.append(('music_resource_loader',music_resource_path))
    episode_path=root/'pass1_episode_files/instructions.csv'
    if episode_path.exists():sources.append(('episode_filenames_and_map_header',episode_path))
    map_level_path=root/'map_level_loader_replay/instructions.csv'
    if map_level_path.exists():sources.append(('map_level_record_loader',map_level_path))
    dos_wrappers=root/'dos_io_wrappers_replay/summary.json'
    if dos_wrappers.exists():
        for f in readjson(dos_wrappers)['functions']:sources.append((f['name'],root/'dos_io_wrappers_replay'/(f['name']+'.csv')))
    null_helpers=root/'pass1_crt_null_text/summary.json'
    if null_helpers.exists():
        for f in readjson(null_helpers)['functions']:sources.append((f['name'],root/'pass1_crt_null_text'/(f['name']+'.csv')))
    scanner_memset=root/'pass1_crt_scan_templates/memset_instructions.csv'
    if scanner_memset.exists():sources.append(('crt_memset_near_buffer',scanner_memset))
    title_path=root/'pass1_title_texts/instructions.csv'
    if title_path.exists():sources.append(('title_screen_wrapper',title_path))
    position_path=root/'pass1_sprite_positions/instructions.csv'
    if position_path.exists():sources.append(('sprite_position_animation_wrapper',position_path))
    action_gate_path=root/'pass1_action_gate/instructions.csv'
    if action_gate_path.exists():sources.append(('saturating_action_gate',action_gate_path))
    action_dispatch_path=root/'action_dispatch_replay/instructions.csv'
    if action_dispatch_path.exists():sources.append(('action_record_dispatcher',action_dispatch_path))
    rng_helpers=root/'pass1_rng/summary.json'
    if rng_helpers.exists():
        for f in readjson(rng_helpers)['functions']:sources.append((f['name'],root/'pass1_rng'/(f['name']+'.csv')))
    damage_effect_path=root/'damage_effect_replay/instructions.csv'
    if damage_effect_path.exists():sources.append(('typed_random_effect',damage_effect_path))
    allocator_path=root/'pass1_crt_allocator_state/allocator_instructions.csv'
    if allocator_path.exists():sources.append(('crt_heap_allocator',allocator_path))
    heap_root_summary=root/'pass1_heap_root/summary.json'
    if heap_root_summary.exists():
        for f in readjson(heap_root_summary)['functions']:sources.append((f['name'],root/'pass1_heap_root'/(f['name']+'.csv')))
    halloc_summary=root/'pass1_halloc/summary.json'
    if halloc_summary.exists():
        for f in readjson(halloc_summary)['functions']:sources.append((f['name'],root/'pass1_halloc'/(f['name']+'.csv')))
    xor_key_summary=root/'pass1_xor_key/summary.json'
    if xor_key_summary.exists():
        for f in readjson(xor_key_summary)['functions']:sources.append((f['name'],root/'pass1_xor_key'/(f['name']+'.csv')))
    mask_summary=root/'pass1_crt_segment_mask/summary.json'
    if mask_summary.exists():
        for f in readjson(mask_summary)['functions']:sources.append((f['name'],root/'pass1_crt_segment_mask'/(f['name']+'.csv')))
    image_cache_summary=root/'pass1_image_handle_cache/summary.json'
    if image_cache_summary.exists():
        for f in readjson(image_cache_summary)['functions']:sources.append((f['name'],root/'pass1_image_handle_cache'/(f['name']+'.csv')))
    lifecycle_summary=root/'pass1_input_lifecycle/summary.json'
    if lifecycle_summary.exists():
        for f in readjson(lifecycle_summary)['functions']:sources.append((f['name'],root/'pass1_input_lifecycle'/(f['name']+'.csv')))
    null_guard_summary=root/'pass1_null_guard/summary.json'
    if null_guard_summary.exists():
        for f in readjson(null_guard_summary)['functions']:sources.append((f['name'],root/'pass1_null_guard'/(f['name']+'.csv')))
    stats_summary=root/'pass1_statistics_formats/summary.json'
    if stats_summary.exists():
        for f in readjson(stats_summary)['functions']:sources.append((f['name'],root/'pass1_statistics_formats'/(f['name']+'.csv')))
    getenv_summary=root/'pass1_getenv/summary.json'
    if getenv_summary.exists():
        for f in readjson(getenv_summary)['functions']:sources.append((f['name'],root/'pass1_getenv'/(f['name']+'.csv')))
    progress_summary=root/'pass1_progress_ui/summary.json'
    if progress_summary.exists():
        for f in readjson(progress_summary)['functions']:sources.append((f['name'],root/'pass1_progress_ui'/(f['name']+'.csv')))
    error_output_summary=root/'pass1_crt_error_output/summary.json'
    if error_output_summary.exists():
        for f in readjson(error_output_summary)['functions']:sources.append((f['name'],root/'pass1_crt_error_output'/(f['name']+'.csv')))
    stack_summary=root/'pass1_stack_reserve/summary.json'
    if stack_summary.exists():
        for f in readjson(stack_summary)['functions']:sources.append((f['name'],root/'pass1_stack_reserve'/(f['name']+'.csv')))
    scheduler_summary=root/'pass1_scheduler/summary.json'
    if scheduler_summary.exists():
        for f in readjson(scheduler_summary)['functions']:sources.append((f['name'],root/'pass1_scheduler'/(f['name']+'.csv')))
    class44_summary=root/'pass1_class44_cache/summary.json'
    if class44_summary.exists():
        for f in readjson(class44_summary)['functions']:sources.append((f['name'],root/'pass1_class44_cache'/(f['name']+'.csv')))
    vga_pages_summary=root/'pass1_vga_pages/summary.json'
    if vga_pages_summary.exists():
        for f in readjson(vga_pages_summary)['functions']:sources.append((f['name'],root/'pass1_vga_pages'/(f['name']+'.csv')))
    audio_state_summary=root/'pass1_audio_state/summary.json'
    sound_priority_summary=root/'sound_priority_replay/summary.json'
    literal_consumer_summary=root/'pass1_literal_consumers/summary.json'
    direction_vector_summary=root/'pass1_direction_vectors/summary.json'
    secondary_class_summary=root/'secondary_class_search/summary.json'
    stream_cache_summary=root/'pass1_stream_cache/summary.json'
    backslash_summary=root/'pass1_backslash_strings/summary.json'
    near_heap_summary=root/'pass1_near_heap_state/summary.json'
    bsf_summary=root/'pass1_bsf_dispatch/summary.json'
    bsf_check_summary=root/'bsf_file_check/summary.json'
    near_heap_flags_summary=root/'pass1_near_heap_flags/summary.json'
    near_heap_grow_summary=root/'near_heap_grow/summary.json'
    near_heap_scan_summary=root/'near_heap_scan/summary.json'
    near_malloc_summary=root/'near_malloc_retry/summary.json'
    reciprocal_init_summary=root/'runtime_reciprocal_init/summary.json'
    slot_init_summary=root/'renderer_slot_initializer/summary.json'
    slot_flush_summary=root/'slot_pending_flush/summary.json'
    sprite_clip_summary=root/'sprite_clip_prefix/summary.json'
    input_wrapper_summary=root/'input_runtime_wrappers/summary.json'
    episode_probe_summary=root/'episode_available_probe/summary.json'
    palette_load_summary=root/'palette_load_replay/summary.json'
    sound_directory_summary=root/'sound_directory_producer/summary.json'
    font2_summary=root/'font2_runtime_fields/summary.json'
    intro_pcx_summary=root/'intro_pcx_replay/summary.json'
    block_blit_summary=root/'vga_column_block_blit/summary.json'
    keyboard_irq_summary=root/'keyboard_irq_replay/summary.json'
    private_stack_summary=root/'worx_private_stack_replay/summary.json'
    menu_gate_summary=root/'menu_save_gate_replay/summary.json'
    if menu_gate_summary.exists():
        for f in readjson(menu_gate_summary)['functions']:sources.append((f['name'],root/'menu_save_gate_replay'/(f['name']+'.csv')))
    if private_stack_summary.exists():
        for f in readjson(private_stack_summary)['functions']:sources.append((f['name'],root/'worx_private_stack_replay'/(f['name']+'.csv')))
    if keyboard_irq_summary.exists():
        for f in readjson(keyboard_irq_summary)['functions']:sources.append((f['name'],root/'keyboard_irq_replay'/(f['name']+'.csv')))
    if block_blit_summary.exists():
        for f in readjson(block_blit_summary)['functions']:sources.append((f['name'],root/'vga_column_block_blit'/(f['name']+'.csv')))
    if intro_pcx_summary.exists():
        for f in readjson(intro_pcx_summary)['functions']:sources.append((f['name'],root/'intro_pcx_replay'/(f['name']+'.csv')))
    if font2_summary.exists():
        for f in readjson(font2_summary)['functions']:sources.append((f['name'],root/'font2_runtime_fields'/(f['name']+'.csv')))
    if sound_directory_summary.exists():
        for f in readjson(sound_directory_summary)['functions']:sources.append((f['name'],root/'sound_directory_producer'/(f['name']+'.csv')))
    if palette_load_summary.exists():
        for f in readjson(palette_load_summary)['functions']:sources.append((f['name'],root/'palette_load_replay'/(f['name']+'.csv')))
    if episode_probe_summary.exists():
        for f in readjson(episode_probe_summary)['functions']:sources.append((f['name'],root/'episode_available_probe'/(f['name']+'.csv')))
    if input_wrapper_summary.exists():
        for f in readjson(input_wrapper_summary)['functions']:sources.append((f['name'],root/'input_runtime_wrappers'/(f['name']+'.csv')))
    if sprite_clip_summary.exists():
        for f in readjson(sprite_clip_summary)['functions']:sources.append((f['name'],root/'sprite_clip_prefix'/(f['name']+'.csv')))
    if slot_flush_summary.exists():
        for f in readjson(slot_flush_summary)['functions']:sources.append((f['name'],root/'slot_pending_flush'/(f['name']+'.csv')))
    if slot_init_summary.exists():
        for f in readjson(slot_init_summary)['functions']:sources.append((f['name'],root/'renderer_slot_initializer'/(f['name']+'.csv')))
    if reciprocal_init_summary.exists():
        for f in readjson(reciprocal_init_summary)['functions']:sources.append((f['name'],root/'runtime_reciprocal_init'/(f['name']+'.csv')))
    if near_malloc_summary.exists():
        for f in readjson(near_malloc_summary)['functions']:sources.append((f['name'],root/'near_malloc_retry'/(f['name']+'.csv')))
    if near_heap_scan_summary.exists():
        for f in readjson(near_heap_scan_summary)['functions']:sources.append((f['name'],root/'near_heap_scan'/(f['name']+'.csv')))
    if near_heap_grow_summary.exists():
        for f in readjson(near_heap_grow_summary)['functions']:sources.append((f['name'],root/'near_heap_grow'/(f['name']+'.csv')))
    if near_heap_flags_summary.exists():
        for f in readjson(near_heap_flags_summary)['functions']:sources.append((f['name'],root/'pass1_near_heap_flags'/(f['name']+'.csv')))
    if bsf_check_summary.exists():
        for f in readjson(bsf_check_summary)['functions']:sources.append((f['name'],root/'bsf_file_check'/(f['name']+'.csv')))
    if bsf_summary.exists():
        for f in readjson(bsf_summary)['functions']:sources.append((f['name'],root/'pass1_bsf_dispatch'/(f['name']+'.csv')))
    if near_heap_summary.exists():
        for f in readjson(near_heap_summary)['functions']:sources.append((f['name'],root/'pass1_near_heap_state'/(f['name']+'.csv')))
    if backslash_summary.exists():
        for f in readjson(backslash_summary)['functions']:sources.append((f['name'],root/'pass1_backslash_strings'/(f['name']+'.csv')))
    if stream_cache_summary.exists():
        for f in readjson(stream_cache_summary)['functions']:sources.append((f['name'],root/'pass1_stream_cache'/(f['name']+'.csv')))
    if secondary_class_summary.exists():
        for f in readjson(secondary_class_summary)['functions']:sources.append((f['name'],root/'secondary_class_search'/(f['name']+'.csv')))
    if direction_vector_summary.exists():
        for f in readjson(direction_vector_summary)['functions']:sources.append((f['name'],root/'pass1_direction_vectors'/(f['name']+'.csv')))
    if literal_consumer_summary.exists():
        for f in readjson(literal_consumer_summary)['functions']:sources.append((f['name'],root/'pass1_literal_consumers'/(f['name']+'.csv')))
    if sound_priority_summary.exists():
        for f in readjson(sound_priority_summary)['functions']:sources.append((f['name'],root/'sound_priority_replay'/(f['name']+'.csv')))
    if audio_state_summary.exists():
        for f in readjson(audio_state_summary)['functions']:sources.append((f['name'],root/'pass1_audio_state'/(f['name']+'.csv')))
    bucket_summary=root/'pass1_tick_buckets/summary.json'
    if bucket_summary.exists():
        for f in readjson(bucket_summary)['functions']:sources.append((f['name'],root/'pass1_tick_buckets'/(f['name']+'.csv')))
    clock_summary=root/'pass1_clock/summary.json'
    if clock_summary.exists():
        for f in readjson(clock_summary)['functions']:sources.append((f['name'],root/'pass1_clock'/(f['name']+'.csv')))
    timezone_summary=root/'pass1_timezone/summary.json'
    if timezone_summary.exists():
        for f in readjson(timezone_summary)['functions']:sources.append((f['name'],root/'pass1_timezone'/(f['name']+'.csv')))
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
    private_fields=root/'worx_private_stack_replay/data_fields.csv'
    if private_fields.exists():
        typed=[]
        for row in readcsv(private_fields):
            a,z=int(row['start']),int(row['end_exclusive'])
            if z-a!=int(row['length']) or sha(image[a:z])!=row['range_sha256']:raise ValueError('private stack field conflict')
            typed.append(dict(start=a,end_exclusive=z))
        data_sources.append(('worx_private_stack_direct_fields',typed))
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
        'pass1_ui_callbacks','pass1_dynamic_ui','pass1_grid_ui','pass1_flags_map_boundary','pass1_ui_strings','pass1_segment_globals','pass1_crt_hook_slots','pass1_message_fields','pass1_split_strings','pass1_crt_program_pointer','pass1_id_card_selector','pass1_scroll_selector','pass1_comparison_strings','pass1_prompt_fields','pass1_ctype','pass1_branched_texts','pass1_display_selector','pass1_calendar','pass1_io_strings','pass1_runtime_messages','pass1_error_formats','pass1_io_argument_strings','pass1_trig','pass1_tangent']
    current_pass1_sources.append('pass1_debug_logger')
    current_pass1_sources.append('pass1_dsp_status')
    current_pass1_sources.append('pass1_direction_fields')
    current_pass1_sources.append('pass1_music_selector')
    current_pass1_sources.append('pass1_music_resource')
    current_pass1_sources.append('pass1_audio_toggles')
    current_pass1_sources.append('pass1_episode_files')
    current_pass1_sources.append('pass1_crt_format_table')
    current_pass1_sources.append('pass1_crt_null_text')
    current_pass1_sources.append('pass1_crt_scan_templates')
    current_pass1_sources.append('pass1_title_texts')
    current_pass1_sources.append('pass1_sprite_positions')
    current_pass1_sources.append('pass1_action_gate')
    current_pass1_sources.append('pass1_rng')
    current_pass1_sources.append('pass1_crt_allocator_state')
    current_pass1_sources.append('pass1_heap_root')
    current_pass1_sources.append('pass1_timezone')
    current_pass1_sources.append('pass1_clock')
    current_pass1_sources.append('pass1_neighbor_offsets')
    current_pass1_sources.append('pass1_tick_buckets')
    current_pass1_sources.append('pass1_audio_state')
    current_pass1_sources.append('pass1_vga_pages')
    current_pass1_sources.append('pass1_class44_cache')
    current_pass1_sources.append('pass1_menu_latches')
    current_pass1_sources.append('pass1_game_input_history')
    current_pass1_sources.append('pass1_scheduler')
    current_pass1_sources.append('pass1_stack_reserve')
    current_pass1_sources.append('pass1_crt_error_output')
    current_pass1_sources.append('pass1_crt_spawn_data')
    current_pass1_sources.append('pass1_progress_ui')
    current_pass1_sources.append('pass1_getenv')
    current_pass1_sources.append('pass1_statistics_formats')
    current_pass1_sources.append('pass1_save_ui_texts')
    current_pass1_sources.append('pass1_status_data')
    current_pass1_sources.append('pass1_guard_diagnostics')
    current_pass1_sources.append('pass1_remaining_literals')
    current_pass1_sources.append('pass1_null_guard')
    current_pass1_sources.append('pass1_input_lifecycle')
    current_pass1_sources.append('pass1_image_handle_cache')
    current_pass1_sources.append('pass1_crt_segment_mask')
    current_pass1_sources.append('pass1_xor_key')
    current_pass1_sources.append('pass1_halloc')
    current_pass1_sources.append('pass1_crt_handoff')
    current_pass1_sources.append('pass1_crt_optional_hooks')
    current_pass1_sources.append('pass1_file_info')
    current_pass1_sources.append('pass1_small_state')
    current_pass1_sources.append('pass1_literal_consumers')
    current_pass1_sources.append('pass1_direction_vectors')
    current_pass1_sources.append('pass1_stream_cache')
    current_pass1_sources.append('pass1_backslash_strings')
    current_pass1_sources.append('pass1_near_heap_state')
    current_pass1_sources.append('pass1_bsf_dispatch')
    current_pass1_sources.append('pass1_startup_segments')
    current_pass1_sources.append('pass1_fcb_prefix')
    current_pass1_sources.append('pass1_near_heap_flags')
    current_pass1_sources.append('xms_request_replay')
    damage_summary=root/'damage_effect_replay/summary.json'
    if damage_summary.exists():
        d=readjson(damage_summary);a=d['dispatch_table_start'];e=d['dispatch_table_end_exclusive']
        if sha(image[a:e])!=d['dispatch_table_sha256']:raise ValueError('damage dispatch table hash conflict')
        data_sources.append(('damage_dispatch_table',[dict(start=a,end_exclusive=e)]))
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
    replay_folders=['crt_error_replay','bitmap_bit_reverse_replay','crt_string_compare_replay','runtime_message_lookup_replay','pass1_trig','pass1_tangent','angle_lookup','pass1_music_selector','pass1_audio_toggles','map_level_loader_replay','dos_io_wrappers_replay','pass1_crt_format_table','pass1_crt_null_text','pass1_crt_scan_templates','pass1_title_texts','pass1_sprite_positions','pass1_action_gate','action_dispatch_replay','pass1_rng','damage_effect_replay']
    replay_folders.append('pass1_crt_allocator_state')
    replay_folders.append('pass1_heap_root')
    replay_folders.append('pass1_timezone')
    replay_folders.append('pass1_clock')
    replay_folders.append('pass1_neighbor_offsets')
    replay_folders.append('pass1_tick_buckets')
    replay_folders.append('pass1_audio_state')
    replay_folders.append('pass1_vga_pages')
    replay_folders.append('pass1_class44_cache')
    replay_folders.append('pass1_menu_latches')
    replay_folders.append('pass1_game_input_history')
    replay_folders.append('pass1_scheduler')
    replay_folders.append('pass1_stack_reserve')
    replay_folders.append('pass1_crt_error_output')
    replay_folders.append('pass1_progress_ui')
    replay_folders.append('pass1_getenv')
    replay_folders.append('pass1_status_data')
    replay_folders.append('pass1_null_guard')
    replay_folders.append('pass1_input_lifecycle')
    replay_folders.append('pass1_image_handle_cache')
    replay_folders.append('pass1_crt_segment_mask')
    replay_folders.append('pass1_xor_key')
    replay_folders.append('pass1_halloc')
    replay_folders.append('pass1_crt_handoff')
    replay_folders.append('pass1_file_info')
    replay_folders.append('sound_priority_replay')
    replay_folders.append('pass1_literal_consumers')
    replay_folders.append('pass1_direction_vectors')
    replay_folders.append('secondary_class_search')
    replay_folders.append('pass1_stream_cache')
    replay_folders.append('pass1_backslash_strings')
    replay_folders.append('pass1_near_heap_state')
    replay_folders.append('bsf_assets_native_codec')
    replay_folders.append('bsf_file_check')
    replay_folders.append('pass1_startup_segments')
    replay_folders.append('pass1_fcb_prefix')
    replay_folders.append('pass1_near_heap_flags')
    replay_folders.append('near_heap_grow')
    replay_folders.append('near_heap_scan')
    replay_folders.append('near_malloc_retry')
    replay_folders.append('renderer_slot_initializer')
    replay_folders.append('slot_pending_flush')
    replay_folders.append('sprite_clip_prefix')
    replay_folders.append('sprite_pixel_replay')
    replay_folders.append('episode_available_probe')
    replay_folders.append('palette_load_replay')
    if (root/'intro_pcx_replay/summary.json').exists():replay_folders.append('intro_pcx_replay')
    if (root/'vga_column_block_blit/summary.json').exists():replay_folders.append('vga_column_block_blit')
    if (root/'keyboard_irq_replay/summary.json').exists():replay_folders.append('keyboard_irq_replay')
    if (root/'worx_private_stack_replay/summary.json').exists():replay_folders.append('worx_private_stack_replay')
    if (root/'menu_save_gate_replay/summary.json').exists():replay_folders.append('menu_save_gate_replay')
    replay_folders.extend(['episode_selector_replay','xms_request_replay','game_start_replay','sound_xms_cache_replay'])
    if len(replay_folders)!=len(set(replay_folders)):raise ValueError('duplicate replay batch')
    for replay_folder in replay_folders:
        replay_summary=readjson(root/replay_folder/'summary.json')
        if replay_summary['failures']!=0:raise ValueError('failed replay batch')
        result['controlled_instruction_replay_cases']+=replay_summary['cases']
    prefix_path=root/'direction_index_replay/summary.json'
    if prefix_path.exists():
        prefix=readjson(prefix_path)
        if prefix['failures']!=0:raise ValueError('failed direction prefix replay')
        result['direction_index_prefix_replay_cases']=prefix['cases']
        result['direction_index_prefix_replay_scope']=prefix['scope']
    latest_map=root/'pass1_xms_move_request/noncode_intervals.csv'
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
    runtime_evidence=[];runtime_sessions=set()
    for runtime_folder in ('dosbox_startup_runtime','dosbox_game_entry_runtime','dosbox_initialization_runtime','dosbox_post_vga_runtime','dosbox_input_init_runtime','dosbox_episode_init_runtime','dosbox_palette_init_runtime','dosbox_unknown_watch_runtime_v3','dosbox_dac_readback_runtime','dosbox_sound_directory_runtime','dosbox_sound_trace_runtime','dosbox_font2_runtime','dosbox_optional_intro_runtime','dosbox_intro_loaded_runtime_v3','dosbox_intro_flip_runtime','dosbox_intro_font0_runtime','dosbox_keyboard_font1_runtime','dosbox_keyboard_stack_runtime','dosbox_worx_stack_window_runtime','dosbox_main_menu_runtime_v2','dosbox_xms_request_runtime','dosbox_newgame_map_runtime_v3','dosbox_scheduler_runtime'):
        runtime_path=root/runtime_folder/'independent_verification.json'
        if not runtime_path.exists():continue
        runtime=readjson(runtime_path)
        if not runtime['verified'] or runtime['runtime_tests']!=1:raise ValueError('unverified original runtime')
        for item in runtime['files']:
            if sha(Path(item['path']).read_bytes())!=item['sha256']:raise ValueError('runtime capture hash mismatch')
        original_runtime=readjson(root/runtime_folder/'summary.json')
        if not original_runtime['success'] or not original_runtime['source_files_unchanged']:raise ValueError('runtime source/capture conflict')
        if runtime['summary_sha256'] in runtime_sessions:raise ValueError('duplicate runtime session')
        runtime_sessions.add(runtime['summary_sha256'])
        runtime_evidence.append(dict(path=str(runtime_path),sha256=sha(runtime_path.read_bytes()),runtime_image_sha256=runtime['runtime_image_sha256'],scope=runtime['scope']))
    if runtime_evidence:
        result['runtime_tests']=len(runtime_evidence)
        result['runtime_tests_scope']='retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer and map-init return after episode1/difficulty1 selection, exact8192B MAP1 level0, sound474B negative-XMS-offset directory reconstruction, 57295B NONCODE endpoint snapshot; endpoint0D29:0A31 is pre-music-selection CALL, not game-loop entry; first post-map scheduler return, due buckets/world counter1to2/synchronized VGA flip, reconstructed world+HUD planes with actual DAC; no host/physical/independent-pixel/full-gameplay/save-load/Win16 parity; prefixes overlap'
        result['runtime_evidence']=runtime_evidence
    bss_tables=[]
    for runtime_bss in (root/'runtime_reciprocal_init/external_bss_tables.csv',root/'sound_directory_producer/external_bss_tables.csv',root/'font2_runtime_fields/external_bss_tables.csv',root/'intro_flip_font0_fields/external_bss_tables.csv',root/'font1_keyboard_fields/external_bss_tables.csv'):
        if runtime_bss.exists():bss_tables.extend(readcsv(runtime_bss))
    if bss_tables:
        csvout(dest/'runtime_bss_tables.csv',bss_tables)
        result['runtime_bss_table_bytes_outside_file']=sum(int(row['length']) for row in bss_tables)
    runtime_buffers=[];runtime_buffer_bytes=set()
    for path in (root/'font2_runtime_fields/runtime_field_intervals.csv',root/'intro_flip_font0_fields/runtime_field_intervals.csv',root/'font1_keyboard_fields/runtime_field_intervals.csv',root/'main_menu_runtime_fields/runtime_field_intervals.csv'):
        if not path.exists():continue
        for row in readcsv(path):
            a,z=int(row['start']),int(row['end_exclusive'])
            if z-a!=int(row['length']) or any(p not in noncode for p in range(a,z)):raise ValueError('runtime buffer outside original NONCODE')
            runtime_buffers.append(dict(source=str(path),source_sha256=sha(path.read_bytes()),start=a,end_exclusive=z,length=z-a,type=row['type'],status='PARTIAL',scope='runtime layout refinement of inherited file-backed buffer, not new typed coverage',original_file_range_sha256=sha(image[a:z])))
            runtime_buffer_bytes.update(range(a,z))
    if runtime_buffers:
        csvout(dest/'runtime_buffer_refinements.csv',runtime_buffers)
        result['runtime_buffer_refinement_records']=len(runtime_buffers);result['runtime_buffer_refinement_bytes_already_in_pass1']=len(runtime_buffer_bytes)
    refinement_paths=[root/'action_dispatch_replay/record_field_roles.csv',root/'damage_effect_replay/consumer_field_roles.csv']
    refinement_paths.append(root/'pass1_guard_diagnostics/consumer_field_roles.csv')
    records=[]
    for refinements in refinement_paths:
        if not refinements.exists():continue
        for row in readcsv(refinements):
            row['evidence_source']=str(refinements);row['evidence_sha256']=sha(refinements.read_bytes());records.append(row)
    if records:
        csvout(dest/'record_field_refinements.csv',records)
        result['record_field_refinements']=len(records)
    win_palette_path=root/'win110_palette_consumer/summary.json'
    if win_palette_path.exists():
        win_palette=readjson(win_palette_path)
        if win_palette['failures']!=0 or win_palette['runtime_tests']!=0:raise ValueError('unexpected Win palette replay result')
        for item in win_palette['source_inputs']:
            if sha(Path(item['path']).read_bytes())!=item['sha256']:raise ValueError('Win palette source mismatch')
        if sha((root/'win110_palette_consumer/cases.csv').read_bytes())!=win_palette['cases_sha256']:raise ValueError('Win palette cases mismatch')
        win_functions=readcsv(root/'win110_palette_consumer/functions.csv')
        if len(win_functions)!=win_palette['functions']:raise ValueError('Win function count mismatch')
        csvout(dest/'win110_palette_functions.csv',win_functions)
        result['win110_palette_supplement']=dict(functions=win_palette['functions'],instructions=win_palette['instructions'],instruction_bytes=win_palette['instruction_bytes'],replay_cases_separate=win_palette['cases'],runtime_tests=0,scope=win_palette['scope'])
    (dest/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
