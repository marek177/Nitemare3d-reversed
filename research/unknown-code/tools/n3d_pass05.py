import pathlib,zipfile,struct,subprocess,re,csv,json,shutil,collections,hashlib
base=pathlib.Path('/mnt/data/N3D_FUNCTION_RESEARCH_PASS04');out=pathlib.Path('/mnt/data/N3D_FUNCTION_RESEARCH_PASS05');shutil.copytree(base,out,dirs_exist_ok=True)
db=out/'MASTER_DATABASE';(out/'FUNCTIONS'/'WIN16').mkdir(parents=True,exist_ok=True)
z=zipfile.ZipFile('/mnt/data/files/dosbox-n3d(20261103-105917).zip')
versions={'WIN_1_10':'nite3/windows/nite3w - 110.exe','WIN_1_8':'nite3/windows/NITE3W - 18.EXE'}
images={}; segments={}; physical={}; hashes={}
for ver,path in versions.items():
 b=z.read(path); hashes[ver]=hashlib.sha256(b).hexdigest(); ne=struct.unpack_from('<I',b,0x3c)[0]; shift=struct.unpack_from('<H',b,ne+0x32)[0]; table=ne+struct.unpack_from('<H',b,ne+0x22)[0]; images[ver]=b
 for i in range(1,1+struct.unpack_from('<H',b,ne+0x1c)[0]):
  sector,n,flags,_=struct.unpack_from('<HHHH',b,table+(i-1)*8)
  if sector: segments[ver,i]=b[sector<<shift:(sector<<shift)+(n or 65536)];physical[ver,i]=sector<<shift
rx=re.compile(r'^\s*([0-9a-f]+):\s*((?:[0-9a-f]{2} )+)\s+([^\s]+)(?:\s+(.*))?$',re.I)
cache={}
def decoded(ver,seg,start):
 key=(ver,seg,start)
 if key in cache:return cache[key]
 raw=segments[ver,seg]; end=min(len(raw),start+480)
 # temp file with full section for absolute addresses
 p=out/'REFERENCES'/ver/f'NE_SEG_{seg:02d}.bin';p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():p.write_bytes(raw)
 cmd=['objdump','-D','-b','binary','-m','i8086','-M','intel',f'--start-address={start}',f'--stop-address={end}',str(p)]
 ret=subprocess.run(cmd,capture_output=True,text=True,check=True)
 ins=[]
 for line in ret.stdout.splitlines():
  m=rx.match(line)
  if m:ins.append(dict(offset=int(m[1],16),raw=bytes.fromhex(m[2]),opcode=m[3].lower(),operands=(m[4] or '').strip()))
 cache[key]=ins;return ins

def walk(ver,seg,start,limit=700):
 q=collections.deque([start]);insmap={};edges=[];unresolved=[];terminators=[];sources=collections.defaultdict(set)
 while q and len(insmap)<limit:
  point=q.popleft()
  if not 0<=point<len(segments[ver,seg]):continue
  if point in insmap:continue
  chunk=decoded(ver,seg,point)
  for ins in chunk:
   a=ins['offset'];n=a+len(ins['raw']); op=ins['opcode'];operand=ins['operands']
   if a in insmap:break
   existing=[(k,k+len(x['raw'])) for k,x in insmap.items() if k<a<k+len(x['raw'])]
   if existing:
    unresolved.append(dict(address=f'{seg:04X}:{a:04X}',kind='overlapping_instruction',detail=str(existing)));break
   insmap[a]=ins
   if op.startswith(('ret','iret')) or op in ('lret','hlt'):
    terminators.append(dict(address=f'{seg:04X}:{a:04X}',opcode=op));break
   branch=op.startswith('j') or op in ('loop','loope','loopne','loopz','loopnz','jcxz')
   if branch:
    match=re.fullmatch(r'0x([0-9a-f]+)',operand,re.I)
    target=int(match[1],16) if match else None
    if target is not None and target<len(segments[ver,seg]):
     edges.append(dict(source=a,target=target,kind=op));q.append(target);sources[target].add(a)
    else:unresolved.append(dict(address=f'{seg:04X}:{a:04X}',kind='indirect_branch',detail=op+' '+operand))
    if op not in ('jmp','ljmp'):
     edges.append(dict(source=a,target=n,kind='fallthrough'));q.append(n);sources[n].add(a)
    break
   if op in ('call','lcall','callw'):
    match=re.fullmatch(r'0x([0-9a-f]+)',operand,re.I)
    target=int(match[1],16) if match else None
    if target is not None:
     edges.append(dict(source=a,target=target,kind='near_call_not_traversed'))
    else:unresolved.append(dict(address=f'{seg:04X}:{a:04X}',kind='far_or_indirect_call',detail=op+' '+operand))
   if len(insmap)>=limit:break
  if len(insmap)>=limit:unresolved.append(dict(address=f'{seg:04X}:{start:04X}',kind='instruction_limit',detail=str(limit)))
 # Addresses from decoded branch may land within instruction and be flagged on next traversal
 return dict(instructions=[dict(offset=k,bytes=v['raw'].hex(' '),opcode=v['opcode'],operands=v['operands'],size=len(v['raw']),file_offset=physical[ver,seg]+k) for k,v in sorted(insmap.items())],edges=edges,unresolved=unresolved,terminators=terminators,limit_hit=len(insmap)>=limit)

seeds=[0x73c0,0x39a8,0x3cb7,0x3c80]
rows=[];edges=[];unresolved=[];reports=[];comparison=[];results={}
for ver in versions:
 for s in seeds:
  r=walk(ver,2,s);results[ver,s]=r
  function_id=f'{ver}_SEG2_{s:04X}'
  for i in r['instructions']:rows.append(dict(function_id=function_id,version=ver,segment=2,**i))
  for e in r['edges']:edges.append(dict(function_id=function_id,source=f"0002:{e['source']:04X}",target=f"0002:{e['target']:04X}",kind=e['kind']))
  for e in r['unresolved']:unresolved.append(dict(function_id=function_id,**e))
  asm='\n'.join(f"{i['offset']:04X}  {i['bytes']:<23} {i['opcode'].upper():<8} {i['operands']}" for i in r['instructions'])
  md=f"# {function_id} — candidate, NOT fully verified\n\nBinary SHA-256: `{hashes[ver]}`\n\nSeed `0002:{s:04X}`, {len(r['instructions'])} decoded instructions, {len(r['edges'])} edges, {len(r['terminators'])} terminating instructions, {len(r['unresolved'])} unresolved items.\n\nDecoded output is on-disk bytes before relocation; exact calling convention and boundary unproven.\n\n## ASM\n```asm\n{asm}\n```\n\n## Remaining unknown\n- All indirect calls and segment fixups must be resolved; branch exploration does not follow calls.\n- Return paths and shared code/data require independent proof.\n- No runtime corroboration performed.\n"
  (out/'FUNCTIONS'/'WIN16'/f'{function_id}.md').write_text(md)
  reports.append(dict(id=function_id,version=ver,entry=f'0002:{s:04X}',instructions=len(r['instructions']),edges=len(r['edges']),ret_sites=len(r['terminators']),unresolved=len(r['unresolved']),limit_hit=r['limit_hit'],status='CANDIDATE_NOT_VERIFIED'))
for s in seeds:
 a=results['WIN_1_10',s]['instructions'];b=results['WIN_1_8',s]['instructions'];ma={x['offset']:x for x in a};mb={x['offset']:x for x in b}
 for offset in sorted(set(ma)|set(mb)):
  x=ma.get(offset);y=mb.get(offset)
  if not x or not y:kind='OFFSET_ONLY_ONE_VERSION'
  elif x['bytes']==y['bytes']:kind='SAME_BYTES_AT_OFFSET'
  elif (x['opcode'],x['operands'])==(y['opcode'],y['operands']):kind='SAME_DISASM_DIFFERENT_BYTES'
  else:kind='DIFFERENT_AT_OFFSET_UNALIGNED'
  comparison.append(dict(seed=f'0002:{s:04X}',offset=f'{offset:04X}',comparison=kind,win110_bytes=x['bytes'] if x else '',win110_asm=(x['opcode']+' '+x['operands']) if x else '',win18_bytes=y['bytes'] if y else '',win18_asm=(y['opcode']+' '+y['operands']) if y else '',proof='raw_offset_comparison_not_semantic_function_match'))

def write_csv(path,items,fields):
 with open(path,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(items)
write_csv(db/'PASS05_FUNCTION_INSTRUCTIONS.csv',rows,['function_id','version','segment','offset','bytes','opcode','operands','size','file_offset'])
write_csv(db/'PASS05_FUNCTION_EDGES.csv',edges,['function_id','source','target','kind'])
write_csv(db/'PASS05_UNRESOLVED.csv',unresolved,['function_id','address','kind','detail'])
write_csv(db/'PASS05_FUNCTION_CANDIDATES.csv',reports,['id','version','entry','instructions','edges','ret_sites','unresolved','limit_hit','status'])
write_csv(db/'PASS05_WIN18_WIN110_SAME_OFFSET_DIFF.csv',comparison,['seed','offset','comparison','win110_bytes','win110_asm','win18_bytes','win18_asm','proof'])
(out/'CFG'/'PASS05_FUNCTION_CFG.json').write_text(json.dumps({f'{v}:{s:04X}':r for (v,s),r in results.items()},indent=2))
summary=['# PASS 05 — four NEAR callee seeds and provisional Windows 1.8 comparison','','All offsets 16-bit segment 2. Code decoder: GNU objdump i8086.','Four call targets observed in PASS04 startup, treated as seeds, not certified entry points.','','| Seed | WIN 1.10 instructions | WIN 1.8 instructions | WIN 1.10 returns | WIN 1.10 unresolved |','|---|---:|---:|---:|---:|']
for s in seeds:
 a=results['WIN_1_10',s];b=results['WIN_1_8',s]
 summary.append(f"| `{s:04X}` | {len(a['instructions'])} | {len(b['instructions'])} | {len(a['terminators'])} | {len(a['unresolved'])} |")
summary+=['','**IMPORTANT:** Cross-version comparison is at *identical segment offsets*, not function matching. Changed bytes may reflect moved code, different linker output, or different functions.','',f'WIN 1.10 sha256 `{hashes["WIN_1_10"]}`',f'WIN 1.8 sha256 `{hashes["WIN_1_8"]}`','','This pass has not certified any function, calling convention, or semantic equivalence. No DOS2 unpacking and no runtime verification performed.','',f'Unresolved edges/items in this pass: {len(unresolved)}.','','The previous PASS04 traversal used chunk-limited disassembly and should not be interpreted as full function coverage.']
(out/'REPORTS'/'PASS05_FUNCTION_CANDIDATES.md').write_text('\n'.join(summary)+'\n')
with open(out/'REPORTS'/'ALL_VERSIONS_PROGRESS.md','a') as f:f.write('\nPASS05: 4 segment-2 Windows near-call target seeds each evaluated at Win1.10 and Win1.8 physical same offsets, provisional CFG and raw offset-level differences. Fully verified functions: 0.\n')
shutil.make_archive('/mnt/data/N3D_FUNCTION_RESEARCH_PASS05_20261103','zip',out.parent,out.name)
print(json.dumps({'candidates':reports,'diff_counts':dict(collections.Counter(x['comparison'] for x in comparison)),'output':'/mnt/data/N3D_FUNCTION_RESEARCH_PASS05_20261103.zip'},indent=2))