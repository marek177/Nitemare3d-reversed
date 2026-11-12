"""python audit_pass1_crt_spawn_data.py IMAGE INVENTORY DECODER OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
fields=[]
def field(name,off,raw,typ,refs):
    a=0x27710+off;e=a+len(raw);assert b[a:e]==raw
    for ip in refs:assert (0x11ee,ip) in lookup
    fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type=typ,status='PARTIAL',range_sha256=sha(raw),evidence_ips=';'.join('11EE:%04X'%i for i in refs)))
for name,off,raw,refs in [('crt_shell_prefix_space',0x24bc,b'/c \0',[0x33cd]),('crt_COMSPEC_spawn_key',0x24f0,b'COMSPEC\0',[0x35bf,0x35c3]),('crt_extension_bat',0x24f8,b'.bat\0',[0x36bb,0x3744]),('crt_extension_exe',0x24fd,b'.exe\0',[0x3744]),('crt_extension_com',0x2502,b'.com\0',[0x3744]),('crt_PATH_key',0x250e,b'PATH\0',[0x37f7,0x37fb]),('crt_path_separator',0x2513,b'\\\0',[0x384e,0x3853]),('crt_COMSPEC_system_key',0x2516,b'COMSPEC\0',[0x38ec,0x38f0]),('crt_shell_switch',0x251e,b'/c\0',[0x3918]),('crt_default_shell',0x2521,b'command.com\0',[0x3966,0x3970])]:field(name,off,raw,'NUL_ASCII_CRT_spawn_literal',refs)
field('crt_spawn_option_word',0x24c0,b'\0\0','mutable_WORD_zero_test',[0x3261])
field('crt_exec_parameter_word',0x24c2,b'\0\0','mutable_WORD_exec_parameter_record_head',[0x34c9,0x3536,0x3559])
field('crt_exec_command_tail_pointer',0x24c4,b'\0'*4,'mutable_FAR16_pointer_offset_written_AX_segment_DS',[0x34cf,0x34d2,0x34e0])
field('crt_exec_fcb1_pointer',0x24c8,struct.pack('<HH',0x24d0,0),'mutable_FAR16_pointer_initial_near_target_24D0_segment_initialized_DS',[0x34d6,0x34e5])
field('crt_exec_fcb2_pointer',0x24cc,struct.pack('<HH',0x24e0,0),'mutable_FAR16_pointer_initial_near_target_24E0_segment_initialized_DS',[0x34da,0x34f0])
field('crt_extension_pointer_table',0x2508,struct.pack('<HHH',0x24f8,0x24fd,0x2502),'NEAR16_pointer_array_3_indexed_2_down_to_0',[0x372e,0x3739,0x3742,0x3744])
field('crt_allocation_retry_callback',0x252e,b'\0'*4,'mutable_FAR16_pointer_null_OR_test_callback_with_WORD_request',[0x3cee,0x3cf1,0x3cfa])
save('data_fields',fields)
contexts=[(0x3250,0x3275),(0x33c1,0x33f2),(0x34c0,0x3503),(0x3536,0x355b),(0x35b5,0x35dc),(0x36bb,0x36c7),(0x372e,0x3753),(0x37e9,0x3809),(0x3841,0x385b),(0x38e6,0x3934),(0x395e,0x3975),(0x3cee,0x3d06)];rows=[]
for r in old:
    if r['cs']!=0x11ee or not any(a<=r['ip']<e for a,e in contexts):continue
    raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw)
    rows.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i),scope='selected original context only; not a closed full function or whole CFG'))
save('instruction_contexts',rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=sum(f['length'] for f in fields),fields=len(fields),verified_context_instructions=len(rows),scope='static literal consumers, pointer initialization and local extension-index bounds; no process launch, no OS parser or allocator execution',exec_parameter_OS_ABI_closed=False,fcb_output_extent_closed=False,spawn_algorithm_closed=False,callback_body_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
