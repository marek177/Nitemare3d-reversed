import pathlib,struct,json,hashlib,csv,collections,sys,difflib
from capstone import *
from capstone.x86 import *
ROOT=pathlib.Path(__file__).resolve().parents[1]; INPUT=ROOT.parent/'inputs';md=Cs(CS_ARCH_X86,CS_MODE_16);md.detail=True
for d in ['REFERENCES/DOS_2_0','REFERENCES/WIN_1_10','FUNCTIONS/DOS','FUNCTIONS/WIN16','ASM_DIFF','CFG','CALLGRAPH','PSEUDOCODE','ALGORITHMS','RUNTIME_EVIDENCE','REPORTS','MASTER_DATABASE','VERSIONS/WIN16']: (ROOT/d).mkdir(parents=True,exist_ok=True)
def js(p,v): (ROOT/p).write_text(json.dumps(v,indent=2))
def csvout(p,rows,fields):
 with (ROOT/p).open('w',newline='') as f:
  w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def sha(b):return hashlib.sha256(b).hexdigest()
inventory=[];models={};unpack=json.loads((ROOT/'VERSIONS/DOS/unpack_manifest.json').read_text())
for p in sorted(INPUT.rglob('*')):
 if p.suffix.lower()!='.exe':continue
 b=p.read_bytes();h=struct.unpack_from('<14H',b);n=struct.unpack_from('<I',b,60)[0] if len(b)>64 else 0;ne=b[n:n+2]==b'NE';r={'path':str(p.relative_to(INPUT)),'size':len(b),'sha256':sha(b),'format':'NE' if ne else 'MZ','version_status':'filename_claim_only','mz_header_bytes':h[4]*16,'mz_declared_size':(h[2]-1)*512+(h[1] or 512),'mz_relocation_count':h[3],'mz_entry_cs':h[11],'mz_entry_ip':h[10]}
 model={'inventory':r,'segments':{},'seeds':[],'fixups':{},'exports':[]};inventory.append(r);models[p.name]=model
 if not ne:
  u=next((x for x in unpack if pathlib.Path(x['file']).name==p.name),None)
  if u and u['status']=='handoff_captured':
   model['image']=pathlib.Path(u['image']).read_bytes();model['seeds']=[(u['entry_cs'],u['entry_ip'])];model['unpack']=u
  continue
 count=struct.unpack_from('<H',b,n+28)[0];st=n+struct.unpack_from('<H',b,n+34)[0];shift=struct.unpack_from('<H',b,n+50)[0];ip,cs=struct.unpack_from('<HH',b,n+20);model['seeds']=[(cs,ip)];r.update(ne_offset=n,segment_count=count,ne_entry_segment=cs,ne_entry_ip=ip,alignment_shift=shift)
 segments=[];fixups=[]
 for k in range(1,count+1):
  sec,ln,flags,minimum=struct.unpack_from('<4H',b,st+8*(k-1));sz=ln or 65536;pos=sec<<shift
  seg={'index':k,'file_offset':pos,'size':sz,'flags':flags,'minimum_allocation':minimum or 65536,'kind':'data' if flags&1 else 'code','file_backed':bool(sec)};segments.append(seg)
  data=b[pos:pos+sz] if sec else b'';model['segments'][k]=data
  if sec and flags&0x100:
   rc=struct.unpack_from('<H',b,pos+sz)[0]
   for j in range(rc):
    at=pos+sz+2+8*j;typ,fl,src,t1,t2=struct.unpack_from('<BBHHH',b,at);record={'segment':k,'type':typ,'flags':fl,'source':src,'target1':t1,'target2':t2,'kind':['internal','import_ordinal','import_name','os_fixup'][fl&3]};fixups.append(record)
    chain=[];s=src
    while s!=65535 and s not in chain and s+2<=len(data):
     chain.append(s);model['fixups'][(k,s)]=record
     if fl&4:break
     s=struct.unpack_from('<H',data,s)[0]
    record['source_chain']=chain
    if fl&3==0 and t1&255!=255 and t1&255<=count:
     if typ==3:model['seeds'].append((t1&255,t2))
     elif typ==2:
      for srcpos in chain:
       if srcpos>=3 and data[srcpos-3] in (0x9a,0xea):model['seeds'].append((t1&255,struct.unpack_from('<H',data,srcpos-2)[0]))
 # Entry table bundles: fixed entries 3 bytes, movable entries 6 bytes.
 et=n+struct.unpack_from('<H',b,n+4)[0];end=et+struct.unpack_from('<H',b,n+6)[0];ordinal=1
 while et+2<=end:
  cnt,seg=b[et:et+2];et+=2
  if cnt==0:break
  if seg==0:ordinal+=cnt;continue
  for j in range(cnt):
   if seg==255:
    flags=b[et];sn=b[et+3];off=struct.unpack_from('<H',b,et+4)[0];et+=6
   else:flags=b[et];sn=seg;off=struct.unpack_from('<H',b,et+1)[0];et+=3
   model['exports'].append({'ordinal':ordinal,'segment':sn,'offset':off,'flags':flags});model['seeds'].append((sn,off));ordinal+=1
 model['segment_metadata']=segments
 js('VERSIONS/WIN16/'+p.name+'.layout.json',{'sha256':sha(b),'segments':segments,'fixups':fixups,'exports':model['exports']})
js('MASTER_DATABASE/BINARY_INVENTORY.json',inventory)
csvout('MASTER_DATABASE/BINARY_INVENTORY.csv',inventory,['path','size','sha256','format','version_status','mz_header_bytes','mz_declared_size','mz_relocation_count','mz_entry_cs','mz_entry_ip','ne_offset','segment_count','ne_entry_segment','ne_entry_ip','alignment_shift'])
# Recursive traversal: each call target gets its own identity. No linear scan, no next-entry boundary assumption.
def decode(model,seg,ip):
 if 'image'in model: data=model['image'];pos=seg*16+ip;chunk=data[pos:pos+15]
 else:
  data=model['segments'].get(seg,b'');chunk=data[ip:ip+15]
 return next(md.disasm(chunk,ip,count=1),None)
def analyze(model,label):
 seeds=set(model['seeds']);todo=list(seeds);funcs={};allun=[]
 while todo and len(funcs)<3000:
  seg,entry=todo.pop(0)
  if (seg,entry) in funcs:continue
  if 'segments'in model and 'image' not in model:
   sm=next((s for s in model.get('segment_metadata',[]) if s['index']==seg),None)
   if not sm or sm['kind']!='code':continue
  q=[entry];seen={};edges=[];calls=[];unknown=[];exits=[]
  while q and len(seen)<12000:
   ip=q.pop()
   if ip in seen:continue
   if ip!=entry and (seg,ip) in seeds:
    edges.append({'from':ip,'to':ip,'kind':'known_entry_boundary_requires_review'});continue
   i=decode(model,seg,ip)
   if not i:unknown.append({'address':ip,'kind':'decode_failure'});continue
   seen[ip]=i;nx=(ip+i.size)&65535;op=i.operands;isjump=i.group(CS_GRP_JUMP);iscall=i.group(CS_GRP_CALL);isret=i.group(CS_GRP_RET) or i.mnemonic.startswith('iret')
   if isret:exits.append(ip);continue
   if iscall or isjump:
    target=None;fix=None
    for disp in range(i.size):
     if (seg,ip+disp) in model['fixups']:fix=model['fixups'][(seg,ip+disp)];break
    if fix:
     if fix['kind']=='internal' and fix['target1']&255!=255:
      target=(fix['target1']&255,op[1].imm if fix['type']==2 and len(op)==2 else fix['target2'])
     else:unknown.append({'address':ip,'kind':'NE_'+fix['kind'],'fixup':fix})
    elif len(op)==1 and op[0].type==X86_OP_IMM:target=(seg,op[0].imm&65535)
    elif len(op)==2 and all(x.type==X86_OP_IMM for x in op):
     target=(op[0].imm-(model.get('unpack',{}).get('load_segment',0)),op[1].imm)
    else:unknown.append({'address':ip,'kind':'indirect_control_flow','asm':i.mnemonic+' '+i.op_str})
    if iscall:
     calls.append({'address':ip,'target':target,'fixup':fix})
     if target and target not in seeds:seeds.add(target);todo.append(target)
     edges.append({'from':ip,'to':nx,'kind':'call_return_assumed'});q.append(nx);continue
    unconditional=i.mnemonic in ('jmp','ljmp')
    if target:
     if target[0]==seg:edges.append({'from':ip,'to':target[1],'kind':'jump' if unconditional else 'taken'});q.append(target[1])
     else:unknown.append({'address':ip,'kind':'cross_segment_jump','target':target})
    if not unconditional:edges.append({'from':ip,'to':nx,'kind':'fallthrough'});q.append(nx)
    continue
   if i.mnemonic in ('hlt','int','int3','into'):unknown.append({'address':ip,'kind':'system_effect','asm':i.mnemonic+' '+i.op_str})
   edges.append({'from':ip,'to':nx,'kind':'fallthrough'});q.append(nx)
  if q:unknown.append({'kind':'instruction_budget'})
  funcs[(seg,entry)]={'segment':seg,'entry':entry,'instructions':seen,'edges':edges,'calls':calls,'unknown':unknown,'exits':exits}
 return funcs
refs={'DOS_2_0':'N3D-UNFU.exe','WIN_1_10':'nite3w - 110.exe'};results={}
for label,name in refs.items():
 print('analyzing',label,flush=True);results[label]=analyze(models[name],label);print(label,len(results[label]),flush=True)
# Analyze every available uniquely hashed game image. Editor binaries excluded.
version_results={};hashcache={}
for name,model in models.items():
 if name.lower() in ('map.exe','maps.exe') or not model['seeds']:continue
 key=model['inventory']['sha256']
 if key not in hashcache:
  ref=next((v for k,v in results.items() if refs[k]==name),None)
  hashcache[key]=ref if ref is not None else analyze(model,name)
 version_results[name]=hashcache[key]
 print('version',name,len(hashcache[key]),flush=True)
masters=[];instructions=[];cfg={};cg={};df={};unresolved=[];bounds=[]
for label,funcs in results.items():
 model=models[refs[label]];platform='DOS' if label.startswith('DOS') else 'WIN16'
 for (seg,en),f in sorted(funcs.items()):
  fid=f'{label}_{seg:04X}_{en:04X}';ins=sorted(f['instructions'].values(),key=lambda x:x.address);addresses={i.address for i in ins};overlaps=[(i.address,j) for i in ins for j in range(i.address+1,i.address+i.size) if j in addresses]
  row={'function_id':fid,'binary_sha256':model['inventory']['sha256'],'segment':f'{seg:04X}','entry':f'{en:04X}','instruction_count':len(ins),'unique_decoded_bytes':len({a for i in ins for a in range(i.address,i.address+i.size)}),'return_count':len(f['exits']),'unresolved_count':len(f['unknown']),'overlap_count':len(overlaps),'status':'CANDIDATE_STATIC_PARTIAL','boundaries_verified':False,'cfg_complete':False,'algorithm_verified':False,'runtime_verified':False}
  masters.append(row);bounds.append(dict(row,exits=';'.join(f'{x:04X}'for x in f['exits']),ranges=';'.join(f'{i.address:04X}+{i.size}'for i in ins)))
  cfg[fid]={'entry':en,'edges':f['edges'],'exits':f['exits'],'overlaps':overlaps,'status':'instruction_graph_not_verified_basic_blocks'};cg[fid]=f['calls'];df[fid]={'status':'local_register_access_only_interinstruction_dataflow_unresolved'}
  for u in f['unknown']:unresolved.append(dict(function_id=fid,**u))
  lines=[]
  for i in ins:
   try:rd,wr=i.regs_access()
   except:rd,wr=[],[]
   mem=[]
   for o in i.operands:
    if o.type==X86_OP_MEM:mem.append({'segment_override':i.reg_name(o.mem.segment)or'default_DS_or_SS_requires_context','base':i.reg_name(o.mem.base),'index':i.reg_name(o.mem.index),'scale':o.mem.scale,'displacement':o.mem.disp,'size':o.size,'access':o.access})
   ir={'function_id':fid,'address':f'{seg:04X}:{i.address:04X}','bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operands':i.op_str,'size':i.size,'registers_read':','.join(i.reg_name(x)for x in rd),'registers_written':','.join(i.reg_name(x)for x in wr),'eflags_metadata':i.eflags,'memory_operands':json.dumps(mem),'semantic_status':'decoder_metadata_not_full_semantics'};instructions.append(ir);lines.append(f'{seg:04X}:{i.address:04X}  {i.bytes.hex():24} {i.mnemonic} {i.op_str}')
  (ROOT/'FUNCTIONS'/platform/(fid+'.asm')).write_text('\n'.join(lines)+'\n')
  # Individual dossier retains every requested topic without fabricating unknown data.
  topics=['Identity and evidence','Boundaries and entries','Original ASM','Basic blocks and CFG','Callers and callees','Arguments and calling convention','Registers and FLAGS','Stack frame','Memory operations','Globals','Data structures','Constants and tables','Branches and loops','Algorithm','RAW Ghidra/IDA pseudocode','Corrected pseudocode','Behavioral reconstruction','Cross-version diff','Added/removed instructions','CFG and algorithm changes','Dependencies','Runtime evidence','Unknowns','Verification','History']
  content=f'# {fid}\n\nStatus: CANDIDATE_STATIC_PARTIAL. Binary SHA-256: `{row["binary_sha256"]}`.\n\n'
  for num,t in enumerate(topics,1):
   val='Unknown; not established by this pass.'
   if num==1:val=json.dumps(row,indent=2)
   elif num==2:val=f'Entry candidate {seg:04X}:{en:04X}; returns {f["exits"]}. Exact reachable instruction ranges in FUNCTION_BOUNDARIES.csv. No next-entry end assumption. Shared blocks/tail calls remain unproved.'
   elif num==3:val=f'See {fid}.asm and instruction database (exact decoded bytes).'
   elif num==4:val='See FUNCTION_CFG.json. Instruction-level edges; call continuation assumes return. Basic-block partition and reachability unverified.'
   elif num==5:val=json.dumps(f['calls'])
   elif num==7:val='See per-instruction decoder register accesses and EFLAGS bitmask. CPU-generation legality and exact flag semantics remain to verify.'
   elif num==15:val='UNAVAILABLE: no Ghidra/IDA raw decompiler output was supplied or generated. Decoder output is not decompilation.'
   elif num==22:val='No gameplay runtime evidence. DOS image extraction executed only the loader/unpacker in Unicorn.'
   elif num==23:val=json.dumps(f['unknown'])+'; indirect targets, calling context, full dataflow, aliases and algorithm remain open.'
   elif num==24:val='No complete-function claim. Static decode only; all full-completion gates false.'
   elif num==25:val='2026-11-04: initial evidence-preserving automated traversal.'
   content+=f'## {num}. {t}\n\n{val}\n\n'
  (ROOT/'FUNCTIONS'/platform/(fid+'.md')).write_text(content)
fields=list(masters[0]);csvout('MASTER_DATABASE/FUNCTION_MASTER.csv',masters,fields);csvout('MASTER_DATABASE/FUNCTION_BOUNDARIES.csv',bounds,fields+['exits','ranges']);csvout('MASTER_DATABASE/FUNCTION_INSTRUCTION_DATABASE.csv',instructions,list(instructions[0]));csvout('MASTER_DATABASE/UNKNOWN_FUNCTIONS.csv',masters,fields);js('CFG/FUNCTION_CFG.json',cfg);js('CALLGRAPH/FUNCTION_CALLGRAPH.json',cg);js('MASTER_DATABASE/FUNCTION_DATAFLOW.json',df);js('MASTER_DATABASE/UNRESOLVED_BRANCHES.json',unresolved);csvout('MASTER_DATABASE/UNRESOLVED_BRANCHES.csv',[{'function_id':u['function_id'],'address':u.get('address',''),'kind':u['kind'],'details':json.dumps(u)}for u in unresolved],['function_id','address','kind','details'])
# Exact reachable-byte signatures; matching does not prove boundaries/semantics or identity across duplicate helpers.
def signature(f):return b''.join(i.bytes for _,i in sorted(f['instructions'].items()))
matrix=[]
for label,funcs in results.items():
 for name,vf in version_results.items():
  if ('dos/' in models[name]['inventory']['path'])!=label.startswith('DOS'):continue
  index=collections.defaultdict(list)
  for addr,f in vf.items():index[signature(f)].append(addr)
  for addr,f in funcs.items():
   hits=index.get(signature(f),[]);matrix.append({'function_id':f'{label}_{addr[0]:04X}_{addr[1]:04X}','target_file':name,'target_sha256':models[name]['inventory']['sha256'],'classification':'IDENTICAL_BYTES' if len(hits)==1 else 'UNKNOWN_MATCH','match_scope':'concatenated_reachable_decoded_bytes_only','candidate_targets':json.dumps(hits),'match_unique':len(hits)==1,'behavioral_equivalence_verified':False})
csvout('ASM_DIFF/FUNCTION_CROSS_VERSION_MATRIX.csv',matrix,list(matrix[0]));csvout('ASM_DIFF/INSTRUCTION_LEVEL_DIFF.csv',[],['function_id','version_a','version_b','address_a','address_b','old_bytes','new_bytes','status'])
progress=[]
for name,vf in version_results.items():progress.append({'file':name,'sha256':models[name]['inventory']['sha256'],'candidate_functions':len(vf),'confirmed_functions':0,'verified_boundaries':0,'complete_cfg':0,'full_instruction_analysis':0,'reconstructed_algorithms':0,'corrected_pseudocode':0,'runtime_verified_functions':0,'unique_reachable_byte_matches_to_reference':sum(x['target_file']==name and x['match_unique']for x in matrix),'unknown_matches':sum(x['target_file']==name and not x['match_unique']for x in matrix)})
js('MASTER_DATABASE/METRICS.json',progress)
(ROOT/'REPORTS/ALL_VERSIONS_PROGRESS.md').write_text('# Evidence baseline — 2026-11-04\n\nAutomated candidate counts are traversal results, not true function totals. Version labels are filename claims pending internal verification. DOS 1.5 absent from this archive. No percentage uses an unknown total.\n\n```json\n'+json.dumps(progress,indent=2)+'\n```\n\nAll candidates retain incomplete status. Raw Ghidra/IDA decompilation unavailable. Exact-byte matching compares concatenated decoded reachable bytes only; layout, aliases, relocation changes and duplicate helpers require further analysis. No ADDED/REMOVED/MODIFIED_ALGORITHM classifications inferred from unmatched candidates.\n')
(ROOT/'ASM_DIFF/FUNCTION_SEMANTIC_DIFF.md').write_text('# Semantic diff\n\nUnknown: candidate byte matches do not establish semantic equivalence. No semantic change claims made.\n')
(ROOT/'PSEUDOCODE/FUNCTION_PSEUDOCODE.md').write_text('# Pseudocode availability\n\nRAW Ghidra/IDA: unavailable. Corrected and behavioral pseudocode require per-function review. See audited function supplements when present.\n')
print('TOTAL',len(masters),'instructions',len(instructions),'matrix',len(matrix),flush=True)
