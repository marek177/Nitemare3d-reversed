import pathlib,zipfile,struct,subprocess,re,csv,json,shutil,collections,hashlib
src=pathlib.Path('/mnt/data/N3D_FUNCTION_RESEARCH_PASS03');out=pathlib.Path('/mnt/data/N3D_FUNCTION_RESEARCH_PASS04');shutil.copytree(src,out,dirs_exist_ok=True);db=out/'MASTER_DATABASE';(out/'CFG').mkdir(exist_ok=True)
z=zipfile.ZipFile('/mnt/data/files/dosbox-n3d(20261103-105917).zip');b=z.read('nite3/windows/nite3w - 110.exe');ne=struct.unpack_from('<I',b,0x3c)[0];shift=struct.unpack_from('<H',b,ne+0x32)[0];segtable=ne+struct.unpack_from('<H',b,ne+0x22)[0]
segments={};physical={}
for i in range(1,1+struct.unpack_from('<H',b,ne+0x1c)[0]):
 sector,n,flags,_=struct.unpack_from('<HHHH',b,segtable+(i-1)*8)
 if sector:
  segments[i]=b[sector<<shift:(sector<<shift)+(n or 65536)];physical[i]=sector<<shift
  (out/'REFERENCES'/'WIN_1_10'/f'NE_SEG_{i:02d}.bin').write_bytes(segments[i])
fixups=collections.defaultdict(list)
for r in csv.DictReader(open(db/'NE_FIXUP_EXPANDED_SITES.csv')):
 if r['version']=='WIN_1_10':fixups[(int(r['segment']),int(r['source_offset'],16))].append({'target':r['target'],'kind':r['target_kind'],'record':r['reloc_index']})
rx=re.compile(r'^\s*([0-9a-f]+):\s*((?:[0-9a-f]{2} )+)\s+([^\s]+)(?:\s+(.*))?$',re.I)
def decode_from(seg,offset):
 path=out/'REFERENCES'/'WIN_1_10'/f'NE_SEG_{seg:02d}.bin';length=len(segments[seg]); stop=min(length,offset+1200)
 cmd=['objdump','-D','-b','binary','-m','i8086','-M','intel',f'--start-address={offset}',f'--stop-address={stop}',str(path)]
 result=subprocess.run(cmd,capture_output=True,text=True,check=True)
 ins=[]
 for line in result.stdout.splitlines():
  m=rx.match(line)
  if m:
   a=int(m[1],16);by=bytes.fromhex(m[2]);ins.append({'address':a,'bytes':by.hex(' '),'size':len(by),'mnemonic':m[3].lower(),'operands':(m[4] or '').strip()})
 return ins
# Seed list restricted to real NE entry CS:IP and export ordinal; deliberately no bulk seed from syntactic call candidates
seeds=[{'id':'WIN110_NE_INITIAL_CSIP','seg':2,'start':0x3718,'kind':'NE_header_CSIP'},{'id':'WIN110_ORDINAL_1','seg':1,'start':0x53ca,'kind':'NE_export_ordinal_1'}]
all_results=[];edge_rows=[];instr_rows=[];unresolved=[]
for seed in seeds:
 seg=seed['seg'];start=seed['start'];q=collections.deque([start]);visited=set();ranges=[];edges=[];steps=0;decode_count=0
 while q and steps<650:
  entry=q.popleft()
  if entry in visited or entry<0 or entry>=len(segments[seg]):continue
  block=[];chunk=decode_from(seg,entry);decode_count+=1
  if not chunk:continue
  for ins in chunk:
   a=ins['address']
   if a in visited:break
   visited.add(a);steps+=1;block.append(ins)
   m=ins['mnemonic'];o=ins['operands'];nxt=a+ins['size']; direct=None
   if m.startswith('j') or m in ('loop','loope','loopne','loopnz','loopz','jcxz'):
    mtarget=re.match(r'^0x([0-9a-f]+)$',o,re.I)
    if mtarget:direct=int(mtarget[1],16)
    if direct is not None and 0<=direct<len(segments[seg]):
     edges.append({'source':f'{seg:04X}:{a:04X}','target':f'{seg:04X}:{direct:04X}','kind':m,'resolution':'within_segment'});q.append(direct)
    else:unresolved.append({'seed':seed['id'],'source':f'{seg:04X}:{a:04X}','opcode':m,'operand':o,'reason':'indirect_or_outside_segment'})
    if m not in ('jmp','jmpw','ljmp') and nxt<len(segments[seg]):
     edges.append({'source':f'{seg:04X}:{a:04X}','target':f'{seg:04X}:{nxt:04X}','kind':'fallthrough','resolution':'within_segment'});q.append(nxt)
    break
   if m in ('ret','retf','lret','iret','retw','retfw','hlt'):break
   if m.startswith('call') or m=='lcall':
    fixes=[]
    for p in range(a+1,min(a+ins['size'],a+6)):fixes+=fixups.get((seg,p),[])
    if fixes:
     edges.append({'source':f'{seg:04X}:{a:04X}','target':fixes[0]['target'],'kind':'fixup_call','resolution':'relocation_target_only'})
    else:
     near=re.fullmatch(r'0x([0-9a-f]+)',o,re.I)
     if near and int(near.group(1),16)<len(segments[seg]):
      edges.append({'source':f'{seg:04X}:{a:04X}','target':f'{seg:04X}:{int(near.group(1),16):04X}','kind':'near_call','resolution':'direct_operand_callee_not_traversed'})
     else:
      unresolved.append({'seed':seed['id'],'source':f'{seg:04X}:{a:04X}','opcode':m,'operand':o,'reason':'call_indirect_unresolved'})
    # follow caller fallthrough, do not conflate callee with this function
   if steps>=650:break
  if block:ranges.append({'entry':entry,'instructions':block,'terminated':block[-1]['mnemonic']})
  # if decoded chunk exhausted without a terminator, continue from final point
  if block and not q and steps<650 and block[-1]['mnemonic'] not in ('ret','retf','lret','iret','retw','retfw','hlt','jmp','ljmp'):
   end=block[-1]['address']+block[-1]['size']
   if end<len(segments[seg]):q.append(end)
 for block in ranges:
  for ins in block['instructions']:
   instr_rows.append({'candidate':seed['id'],'segment':seg,'offset':f"{ins['address']:04X}",'file_offset':f"{physical[seg]+ins['address']:06X}",'bytes':ins['bytes'],'mnemonic':ins['mnemonic'],'operands':ins['operands'],'size':ins['size'],'proof':'objdump_i8086_decode_not_semantic_verification'})
 edge_rows.extend([{'candidate':seed['id'],**e} for e in edges])
 all_results.append({'id':seed['id'],'seed_kind':seed['kind'],'segment':seg,'entry':f'{start:04X}','instructions_reached':steps,'basic_block_candidates':len(ranges),'edges':len(edges),'decode_invocations':decode_count,'limit_hit':steps>=650,'blocks':ranges,'edges_list':edges})
fields=['candidate','segment','offset','file_offset','bytes','mnemonic','operands','size','proof']
with open(db/'PASS04_REACHABLE_INSTRUCTIONS.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(instr_rows)
with open(db/'PASS04_CFG_EDGES.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['candidate','source','target','kind','resolution']);w.writeheader();w.writerows(edge_rows)
with open(db/'PASS04_UNRESOLVED_EDGES.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['seed','source','opcode','operand','reason']);w.writeheader();w.writerows(unresolved)
(out/'CFG'/'PASS04_SEED_CFG.json').write_text(json.dumps(all_results,indent=2)+'\n')
# inspect unmodified DOS loader first instructions in all DOS version via prior verified report, never claim decompression solved
readme=['# PASS 04 — Conservative seed-based recursive 16-bit CFG analysis','', 'Source: original Windows 1.10 NE binary from supplied DOSBox bundle. Decoder: GNU objdump -m i8086 -M intel.','', 'IMPORTANT: branch exploration limited to direct within-segment targets; a `call` records relocation evidence but does not automatically absorb the callee into the seed candidate. Blocks are *candidates*, not fully verified function boundaries.','', '| Candidate | Reached instructions | Preliminary blocks | Edges | Truncated |','|---|---:|---:|---:|---|']
for v in all_results:readme.append(f"| {v['id']} ({v['segment']:04X}:{v['entry']}) | {v['instructions_reached']} | {v['basic_block_candidates']} | {v['edges']} | {v['limit_hit']} |")
readme+=['','## Open issues','- Decode from the NE CS:IP startup and exported ordinal entry only; these are two seeds, not proof of the whole call graph.','- Decoder output uses on-disk operands. For FAR calls the relocation records must override original placeholder bytes.','- Some decoder paths may enter padding/data via spurious edges. Further semantic disambiguation and fixup correction required.','- Existing PASS03 call candidates based on preceding byte 0x9A require instruction-boundary confirmation.','- No runtime emulation was executed in this pass; no complete functions certified.','- DOS 2.0 unpacked main image not yet recovered.','','## Output','- MASTER_DATABASE/PASS04_REACHABLE_INSTRUCTIONS.csv','- MASTER_DATABASE/PASS04_CFG_EDGES.csv','- MASTER_DATABASE/PASS04_UNRESOLVED_EDGES.csv','- CFG/PASS04_SEED_CFG.json','- REFERENCES/WIN_1_10/NE_SEG_*.bin']
(out/'REPORTS'/'PASS04_RECURSIVE_CFG.md').write_text('\n'.join(readme)+'\n')
(out/'REPORTS'/'ALL_VERSIONS_PROGRESS.md').open('a').write('\nPASS04: 2 trusted Windows 1.10 entry seeds explored with conservative direct-branch recursive traversal; see PASS04_RECURSIVE_CFG.md. 0 fully verified functions.\n')
shutil.make_archive('/mnt/data/N3D_FUNCTION_RESEARCH_PASS04_20261103','zip',out.parent,out.name)
print(json.dumps({'summary':[{k:v for k,v in x.items() if k not in ('blocks','edges_list')} for x in all_results],'unresolved':len(unresolved),'archive':'/mnt/data/N3D_FUNCTION_RESEARCH_PASS04_20261103.zip'},indent=2))