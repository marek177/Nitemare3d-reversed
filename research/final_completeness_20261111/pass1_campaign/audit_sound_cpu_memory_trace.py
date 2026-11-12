"""python audit_sound_cpu_memory_trace.py RUNTIME_OUT IMAGE RELOCS MAP DECODER OUT
Reconstruct logged x86 memory operands; explicitly exclude DOSBox host callbacks.
"""
import collections,csv,hashlib,json,re,struct,sys
from pathlib import Path
runtime,image,relocs,mapping,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,InstructionInfoFactory,MemorySizeExt,Register,Mnemonic,OpAccess
sha=lambda b:hashlib.sha256(b).hexdigest();proof=json.loads((runtime/'independent_verification.json').read_text());assert proof['cpu_trace_manifest_verified']
for item in proof['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
manifest=json.loads((runtime/'trace_manifest.json').read_text());trace=Path(manifest['path']);rawlog=trace.read_bytes();assert sha(rawlog)==manifest['sha256'];capture=json.loads((runtime/'summary.json').read_text());load=capture['load_segment'];canonical=bytearray(image.read_bytes());assert sha(canonical)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',canonical,int(r['image_offset']),(int(r['original_word'])+load)&65535)
unknown=set()
for r in csv.DictReader(mapping.open(encoding='utf-8-sig')):
 if r['status']=='UNKNOWN':unknown.update(range(load*16+int(r['start']),load*16+int(r['end_exclusive'])))
assert len(unknown)==44;hook=set(range(load*16+0x29a66,load*16+0x29a6a));fmt=Formatter(FormatterSyntax.INTEL);factory=InstructionInfoFactory();records=[]
for number,line in enumerate(rawlog.decode('ascii').splitlines(),1):
 head=re.match(r'^([0-9.]+) ([0-9A-F]{4}):([0-9A-F]{8})\s+',line);assert head,(number,line)
 prefix=line.split(' EAX:',1)[0];m=re.search(r'((?:[0-9A-F]{2} ){1,15})\s*$',prefix);assert m,(number,line);raw=bytes.fromhex(m[1]);regs={k:int(v,16) for k,v in re.findall(r'\b(EAX|EBX|ECX|EDX|ESI|EDI|EBP|ESP|DS|ES|FS|GS|SS|FLG|CR0):([0-9A-F]+)',line)};assert len(regs)==15 and regs['CR0']&1==0
 records.append(dict(number=number,cs=int(head[2],16),ip=int(head[3],16),raw=raw,regs=regs,host_callback='callback ' in prefix,asm_text=prefix[head.end():m.start()].strip()))
assert (records[0]['cs'],records[0]['ip'])==(load+0x476,0x17c) and (records[-1]['cs'],records[-1]['ip'])==(load+0x476,0x190)
out.mkdir(parents=True,exist_ok=True);accesses=[];instructions=[];callbacks=[];interrupts=[];canonical_matches=0;unknown_fetches=0
def reg_value(reg,values):
 if reg==Register.NONE:return 0
 name=fmt.format_register(reg).upper()
 if name in values:return values[name]
 if name in ('AX','BX','CX','DX','SI','DI','BP','SP'):return values['E'+name]&65535
 if name in ('AL','BL','CL','DL'):return values['E'+name[0]+'X']&255
 if name in ('AH','BH','CH','DH'):return (values['E'+name[0]+'X']>>8)&255
 raise AssertionError(('unsupported address register',name))
def add_access(r,kind,seg,offset,width,access):
 linear=(seg<<4)+offset;assert 0<=linear and linear+width<=0x100000
 u=sorted(set(range(linear,linear+width))&unknown);h=sorted(set(range(linear,linear+width))&hook)
 accesses.append(dict(trace_record=r['number'],cs=r['cs'],ip=r['ip'],kind=kind,segment=seg,offset=offset,linear_start=linear,width=width,access=access,unknown_byte_hits=len(u),hook_byte_hits=len(h),scope='logged x86 operand address only; not callback internal memory'))
for r in records[:-1]:
 physical=r['cs']*16+r['ip'];unknown_fetches+=len(set(range(physical,physical+len(r['raw'])))&unknown)
 if r['host_callback']:
  assert r['raw'].startswith(bytes.fromhex('fe38'));callbacks.append(dict(record=r['number'],cs=r['cs'],ip=r['ip'],bytes=r['raw'].hex(),description=r['asm_text'],scope='DOSBox extension; internal C++ reads/writes not traced'));continue
 i=Decoder(16,r['raw'],ip=r['ip']).decode();assert not i.is_invalid and i.len==len(r['raw']),(r['number'],r['raw'].hex())
 assert not(i.has_rep_prefix or i.has_repne_prefix),'REP needs separately verified iteration semantics'
 imageoffset=physical-load*16;inside=0<=imageoffset and imageoffset+len(r['raw'])<=len(canonical)
 if inside:assert canonical[imageoffset:imageoffset+len(r['raw'])]==r['raw'];canonical_matches+=1
 instructions.append(dict(record=r['number'],cs=r['cs'],ip=r['ip'],bytes=r['raw'].hex(),instruction=fmt.format(i),canonical_image_match=inside))
 for m in factory.info(i).used_memory():
  if m.access==OpAccess.NO_MEM_ACCESS:continue
  width=MemorySizeExt.size(m.memory_size);assert width>0,(r['number'],fmt.format(i))
  assert m.address_size in (1,2);mask=65535 if m.address_size==1 else 0xffffffff
  offset=(reg_value(m.base,r['regs'])+reg_value(m.index,r['regs'])*m.scale+m.displacement)&mask
  add_access(r,'instruction_info',reg_value(m.segment,r['regs']),offset,width,m.access)
 if i.mnemonic==Mnemonic.INT:
  vector=i.immediate8;ss=r['regs']['SS'];sp=r['regs']['ESP']&65535
  for n in (2,4,6):add_access(r,'realmode_INT_stack',ss,(sp-n)&65535,2,OpAccess.WRITE)
  add_access(r,'realmode_INT_vector',0,vector*4,4,OpAccess.READ)
  interrupts.append(dict(record=r['number'],vector=vector,AX=r['regs']['EAX']&65535,BX=r['regs']['EBX']&65535,CX=r['regs']['ECX']&65535,DX=r['regs']['EDX']&65535,DS=r['regs']['DS'],scope='observed input registers; host implementation excluded'))
def save(name,rows):
 if not rows:return
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for name,rows in [('instructions',instructions),('memory_operands',accesses),('host_callbacks',callbacks),('interrupt_inputs',interrupts)]:save(name,rows)
summary=dict(trace_sha256=sha(rawlog),trace_bytes=len(rawlog),trace_records=len(records),terminal_record_excluded=1,executed_record_candidates=len(records)-1,x86_instruction_records=len(instructions),canonical_instruction_records=canonical_matches,host_callback_records=len(callbacks),explicit_and_INT_memory_ranges=len(accesses),unknown_operand_byte_hits=sum(a['unknown_byte_hits'] for a in accesses),unknown_fetch_byte_hits=unknown_fetches,hook_operand_byte_hits=sum(a['hook_byte_hits'] for a in accesses),REP_records=0,interrupt_records=len(interrupts),INT21_inputs=[r for r in interrupts if r['vector']==0x21],runtime_tests=0,new_deep_verified_bytes=0,scope='bounded pre-instruction LOGL reconstruction, excluding terminal and host callback memory; no general read/write proof outside this trace, no whole-game or UNUSED classification')
summary['map_sha256']=sha(mapping.read_bytes());summary['relocations_sha256']=sha(relocs.read_bytes());summary['runtime_proof_sha256']=sha((runtime/'independent_verification.json').read_bytes());summary['access_kind_counts']=dict(collections.Counter(str(a['access']) for a in accesses))
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
