from pathlib import Path
import struct,json,csv,random,hashlib,re,subprocess,collections
from capstone import *
from capstone.x86 import *
from unicorn import *
from unicorn.x86_const import *
R=Path(__file__).resolve().parents[2];O=R/'PASS002';image=(R/'VERSIONS/DOS/N3D-UNFU.exe.loaded.bin').read_bytes();md=Cs(CS_ARCH_X86,CS_MODE_16);md.detail=True;randomizer=random.Random(2026110402)
def save(p,v): (O/p).write_text(json.dumps(v,indent=2))
def s16(x):x&=65535;return x-65536 if x&32768 else x
def s32(x):x&=0xffffffff;return x-0x100000000 if x&0x80000000 else x
def div0(a,b):
 if b==0:raise ZeroDivisionError()
 q=abs(a)//abs(b);q=-q if (a<0)!=(b<0) else q
 if not -0x80000000<=q<=0x7fffffff:raise OverflowError()
 return q
def word(b,o):return struct.unpack_from('<H',b,o)[0]
def put16(b,o,v):struct.pack_into('<H',b,o,v&65535)
def put32(b,o,v):struct.pack_into('<I',b,o,v&0xffffffff)
def corrected(i):return {b'\x98':'cbw',b'\x99':'cwd'}.get(bytes(i.bytes),i.mnemonic)
def traverse(seg,entry,extra_edges=None):
 q=[entry];seen={};edges=[];calls=[];unknown=[];exits=[]
 while q:
  ip=q.pop()
  if ip in seen:continue
  i=next(md.disasm(image[seg*16+ip:seg*16+ip+15],ip,count=1),None)
  if not i:unknown.append({'address':ip,'kind':'decode_failure'});continue
  seen[ip]=i;nx=ip+i.size
  if i.group(CS_GRP_RET):exits.append(ip);continue
  if i.group(CS_GRP_CALL):
   ops=i.operands;target=None
   if len(ops)==1 and ops[0].type==X86_OP_IMM:target=[seg,ops[0].imm&65535]
   elif len(ops)==2 and all(x.type==X86_OP_IMM for x in ops):target=[ops[0].imm-0x1000,ops[1].imm]
   calls.append({'address':ip,'target':target,'near_far':'FAR'if i.mnemonic=='lcall'else'NEAR','push_cs_prefix':image[seg*16+ip-1:seg*16+ip]==b'\x0e'})
   edges.append({'from':ip,'to':nx,'kind':'call_continuation_assumed'});q.append(nx);continue
  if i.group(CS_GRP_JUMP):
   if len(i.operands)==1 and i.operands[0].type==X86_OP_IMM:
    target=i.operands[0].imm&65535;edges.append({'from':ip,'to':target,'kind':'jump'if i.mnemonic=='jmp'else'taken'});q.append(target)
   elif extra_edges and ip in extra_edges:
    for target in sorted(set(extra_edges[ip])):edges.append({'from':ip,'to':target,'kind':'proven_table_target'});q.append(target)
   else:unknown.append({'address':ip,'kind':'indirect_jump'})
   if i.mnemonic not in ('jmp','ljmp'):edges.append({'from':ip,'to':nx,'kind':'fallthrough'});q.append(nx)
  else:edges.append({'from':ip,'to':nx,'kind':'fallthrough'});q.append(nx)
 addresses=set(seen);overlap=[(i.address,a)for i in seen.values()for a in range(i.address+1,i.address+i.size)if a in addresses]
 leaders={entry}
 for e in edges:
  src=seen[e['from']]
  if src.group(CS_GRP_JUMP) or src.group(CS_GRP_CALL):leaders.add(e['to'])
 indeg=collections.Counter(e['to']for e in edges)
 leaders.update(a for a,n in indeg.items()if n>1)
 blocks=[];assigned=set()
 for start in sorted(leaders):
  if start not in seen:continue
  a=start;body=[]
  while a in seen and a not in assigned:
   i=seen[a];body.append(a);assigned.add(a)
   if i.group(CS_GRP_JUMP)or i.group(CS_GRP_CALL)or i.group(CS_GRP_RET):break
   nxt=a+i.size
   if nxt in leaders:break
   a=nxt
  blocks.append({'start':start,'instructions':body})
 for a in sorted(addresses-assigned):blocks.append({'start':a,'instructions':[a],'status':'residual_requires_partition_review'})
 return {'segment':seg,'entry':entry,'instructions':seen,'edges':edges,'calls':calls,'unknown':unknown,'exits':exits,'overlap':overlap,'blocks':blocks}
def export_function(fid,f):
 rows=[];lines=[]
 for ip,i in sorted(f['instructions'].items()):
  rd,wr=i.regs_access();mem=[]
  for op in i.operands:
   if op.type==X86_OP_MEM:mem.append({'segment_override':i.reg_name(op.mem.segment),'base':i.reg_name(op.mem.base),'index':i.reg_name(op.mem.index),'displacement':op.mem.disp,'size':op.size,'access':op.access})
  rows.append({'function_id':fid,'address':f'{f["segment"]:04X}:{ip:04X}','bytes':i.bytes.hex(),'raw_capstone_mnemonic':i.mnemonic,'corrected_mnemonic':corrected(i),'operands':i.op_str,'size':i.size,'registers_read_decoder':','.join(i.reg_name(x)for x in rd),'registers_written_decoder':','.join(i.reg_name(x)for x in wr),'flags_decoder_mask':i.eflags,'memory_operands':json.dumps(mem),'semantics_status':'decoder_metadata; CBW/CWD register corrections in mnemonic_audit.json'})
  lines.append(f'{f["segment"]:04X}:{ip:04X} {i.bytes.hex():24} {corrected(i)} {i.op_str}')
 (O/'FUNCTIONS'/(fid+'.asm')).write_text('\n'.join(lines)+'\n')
 with (O/'FUNCTIONS'/(fid+'.instructions.csv')).open('w',newline='')as out:
  w=csv.DictWriter(out,list(rows[0]));w.writeheader();w.writerows(rows)
 save('CFG/'+fid+'.json',{k:v for k,v in f.items()if k!='instructions'})
 return len(rows)
# Exhaustive dispatch proof.
seg=0x476;table=[word(image,seg*16+0x39e+2*k)for k in range(24)];dispatch=[]
for char in range(256):
 for upper in [0,0x7fff,0x8000,0xffff]:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,image[seg*16:seg*16+0x516]);u.reg_write(UC_X86_REG_CS,0x1000);u.reg_write(UC_X86_REG_DS,0x4000);u.reg_write(UC_X86_REG_BX,0x1000);u.reg_write(UC_X86_REG_EAX,(upper<<16)|0xa500);u.mem_write(0x41001,bytes([char]));record={};targets=set(table)|{0x3ce}
  def stop(u,a,s,d):
   ip=a-0x10000
   if ip in targets:record.update(target=ip,bx=u.reg_read(UC_X86_REG_BX),eax=u.reg_read(UC_X86_REG_EAX));u.emu_stop()
  u.hook_add(UC_HOOK_CODE,stop);u.emu_start(0x10389,0x11000,count=30)
  expected=table[char-ord('a')]if ord('a')<=char<=ord('x')else 0x3ce
  assert record.get('target')==expected,(char,record,expected)
  if ord('a')<=char<=ord('x'):assert record['bx']==2*(char-ord('a'))
  dispatch.append({'character':char,'initial_EAX_high16':upper,'expected_target':expected,'actual':record,'status':'PASS'})
save('RUNTIME_EVIDENCE/dispatch_1024_cases.json',dispatch)
f_switch=traverse(seg,0x326,{0x398:table});switch_count=export_function('DOS_2_0_0476_0326',f_switch)
save('DATAFLOW/CLI_dispatch_table.json',{'selector_source':'DS:[BX+1] at 0476:0389, BX restored argv pointer at 0384–0387','sign_extension':'CBW at 038C','index_formula':'uint16(sign_extend_8(character)-0x61)','guard':'unsigned index <= 0x17 at 0390–0393','effective_index':'BX=2*index at 0395–0397','table_segment':'CS','table_offset':0x39e,'table_bytes':image[seg*16+0x39e:seg*16+0x3ce].hex(),'entries':[{'character':chr(97+k),'index':k,'byte_index':2*k,'target':f'0476:{t:04X}'}for k,t in enumerate(table)],'invalid_target':'0476:03CE','distinct_targets':len(set(table)),'tests':len(dispatch),'unknowns':['Callee termination behavior for invalid arguments','CLI meanings of called helper operations','DS preservation through prior callees']})
# Fixed-point endpoint helper, no external callees.
f_math=traverse(0x201,0x1a);math_count=export_function('DOS_2_0_0201_001A',f_math);mathcode=image[0x201*16+0x1a:0x201*16+0x12d]
assert not f_math['calls'] and not f_math['unknown'] and f_math['exits']==[0x12c]
cases=[];special=[(0,0,0,0),(0,0,0,100),(0,5,100,5),(0,0,-1,-32768),(32767,-32768,-32768,32767),(-32768,32767,32767,-32768)]
for idx in range(1006):
 x1,y1,x2,y2=special[idx]if idx<len(special)else tuple(randomizer.randrange(-32768,32768)for _ in range(4));xa,xb,origin=(randomizer.randrange(-32768,32768)for _ in range(3));dx=s16(x2-x1);dy=s16(y2-y1);mem=bytearray([idx%251]*65536);ptr=0x1000;put16(mem,ptr+2,xa);put16(mem,ptr+6,xb);put16(mem,0x4554,origin);expected=bytearray(mem);fault=False
 try:
  slope=div0(s32((dy&65535)<<16),dx)if dx else 0;put32(expected,ptr+10,slope)
  if dy==0:ya=yb=y1;fixed=((y1-origin)&65535)<<16
  elif dx==0:ya,yb=y1,y2;fixed=((y1-origin)&65535)<<16
  else:
   ya=(div0(s16(xa-x1)*dy,dx)+y1)&65535;yb=(div0(s16(xb-x1)*dy,dx)+y1)&65535;fixed=(slope*s16(xa-x1)+(((y1-origin)&65535)<<16))&0xffffffff
  put16(expected,ptr+4,ya);put16(expected,ptr+8,yb);put32(expected,ptr+14,fixed)
 except OverflowError:fault=True
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,mathcode);u.mem_write(0x40000,bytes(mem));u.reg_write(UC_X86_REG_CS,0x1000);u.reg_write(UC_X86_REG_DS,0x4000);u.reg_write(UC_X86_REG_SS,0x7000);u.reg_write(UC_X86_REG_SP,0x8000)
 for reg,val in [(UC_X86_REG_BP,0x4567),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x6789)]:u.reg_write(reg,val)
 u.mem_write(0x78000,struct.pack('<9H',0x100,0x2000,ptr,x1&65535,y1&65535,x2&65535,y2&65535,0,0));interrupt=[]
 def intr(u,n,d):interrupt.append(n);u.emu_stop()
 u.hook_add(UC_HOOK_INTR,intr);u.emu_start(0x10000,0x20100,count=500)
 if fault:assert interrupt==[0],(idx,interrupt)
 else:
  assert not interrupt,(idx,interrupt)
  assert bytes(u.mem_read(0x40000,65536))==bytes(expected),(idx,x1,y1,x2,y2,xa,xb,origin)
  assert u.reg_read(UC_X86_REG_AX)==((fixed>>16)&65535)
  assert u.reg_read(UC_X86_REG_SP)==0x8004
  assert u.reg_read(UC_X86_REG_BP)==0x4567 and u.reg_read(UC_X86_REG_SI)==0x5678 and u.reg_read(UC_X86_REG_DI)==0x6789
 cases.append({'case':idx,'x1':x1,'y1':y1,'x2':x2,'y2':y2,'record_xa':xa,'record_xb':xb,'origin':origin,'wrapped_dx':dx,'wrapped_dy':dy,'expected_divide_fault':fault,'observed_interrupts':interrupt,'status':'PASS'})
save('RUNTIME_EVIDENCE/fixed_point_1006_cases.json',cases)
# New Win getters; preserve NE address model in metadata. Tests use isolated copied code in real mode.
layout=json.loads((R/'VERSIONS/WIN16/nite3w - 110.exe.layout.json').read_text());b=(R.parent/'inputs/nite3/windows/nite3w - 110.exe').read_bytes();nebase=layout['segments'][2]['file_offset'];getter=[]
for off,dsaddr in [(0xd9e,0x4be1),(0xda4,0x4be2)]:
 code=b[nebase+off:nebase+off+6];assert code==b'\xa0'+struct.pack('<H',dsaddr)+bytes.fromhex('2ae4cb')
 fid=f'WIN_1_10_0003_{off:04X}';(O/'FUNCTIONS'/(fid+'.asm')).write_text('\n'.join(f'0003:{i.address:04X} {i.bytes.hex():16} {corrected(i)} {i.op_str}'for i in md.disasm(code,off))+'\n')
 for value in range(256):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,code);u.reg_write(UC_X86_REG_CS,0x1000);u.reg_write(UC_X86_REG_DS,0x4000);u.reg_write(UC_X86_REG_SS,0x7000);u.reg_write(UC_X86_REG_SP,0x8000);u.reg_write(UC_X86_REG_EAX,0x1234abcd);flags=0xcd7;u.reg_write(UC_X86_REG_EFLAGS,flags);u.mem_write(0x40000+dsaddr,bytes([value]));u.mem_write(0x78000,struct.pack('<HH',0x100,0x2000));writes=[]
  def write(u,access,address,size,value,user):writes.append([address,size,value])
  u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(0x10000,0x20100,count=10)
  assert u.reg_read(UC_X86_REG_EAX)==0x12340000+value
  assert u.reg_read(UC_X86_REG_EFLAGS)&0x8d5==0x44 and (u.reg_read(UC_X86_REG_EFLAGS)^flags)&~0x8d5&65535==0
  assert u.reg_read(UC_X86_REG_SP)==0x8004 and not writes
  getter.append({'function_id':fid,'input_byte':value,'eax':u.reg_read(UC_X86_REG_EAX),'status':'PASS'})
save('RUNTIME_EVIDENCE/win_getters_512_cases.json',getter)
# Startup DS establishment, stopping before any runtime-library call or program entry.
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,image);u.mem_write(0xff02,struct.pack('<H',0x9000));u.reg_write(UC_X86_REG_CS,0x21ee);u.reg_write(UC_X86_REG_DS,0xff0);u.reg_write(UC_X86_REG_ES,0xff0);u.reg_write(UC_X86_REG_SS,0x4574);u.reg_write(UC_X86_REG_SP,0x800);ints=[];states=[]
def dosint(u,n,d):
 assert n==0x21
 ah=u.reg_read(UC_X86_REG_AH);ints.append({'int':n,'ah':ah,'source':'synthetic minimal DOS service'})
 if ah==0x30:u.reg_write(UC_X86_REG_AX,5)
 elif ah==0x4a:u.reg_write(UC_X86_REG_EFLAGS,u.reg_read(UC_X86_REG_EFLAGS)&~1)
 else:raise AssertionError(ah)
def startup_hook(u,a,s,d):
 ip=u.reg_read(UC_X86_REG_IP)
 if ip in [0x37,0xb1,0xb3]:states.append({'cs':u.reg_read(UC_X86_REG_CS),'ip':ip,'ds':u.reg_read(UC_X86_REG_DS),'ss':u.reg_read(UC_X86_REG_SS),'sp':u.reg_read(UC_X86_REG_SP)})
 if ip==0xb3:u.emu_stop()
u.hook_add(UC_HOOK_INTR,dosint);u.hook_add(UC_HOOK_CODE,startup_hook);u.emu_start(0x21ef8,0x30000,count=100000);assert u.reg_read(UC_X86_REG_IP)==0xb3 and u.reg_read(UC_X86_REG_DS)==0x3771
save('DATAFLOW/startup_DS_establishment.json',{'load_segment':0x1000,'DS_after_11EE_00B2':0x3771,'module_relative_DS':0x2771,'interrupt_shims':ints,'states':states,'proof_scope':'startup prefix with synthetic DOS success responses; does not prove DS remains this value at initializer call','initializer_call_path':['11EE:00DA -> 0476:0326','0476:04F2 -> 0476:00CE (PUSH CS + near CALL)','0476:0128 -> 0201:000A'],'remaining_barrier':'Prior callees and optional callback 11EE:00B9 may alter DS; interprocedural proof not complete'})
# Cross-check real operand-size behavior versus decoder names.
probe=bytes.fromhex('989966986699');q=O/'mnemonic_probe.bin';q.write_bytes(probe);asm=subprocess.run(['objdump','-D','-b','binary','-m','i8086',str(q)],capture_output=True,text=True,check=True).stdout;(O/'REPORTS/objdump_mnemonic_probe.txt').write_text(asm)
corrections=[]
for i in md.disasm(probe,0):corrections.append({'bytes':i.bytes.hex(),'raw_capstone':i.mnemonic,'corrected_16bit':corrected(i),'semantic_registers_read':'AL'if i.bytes==b'\x98'else'AX'if i.bytes==b'\x99'else'AX'if i.bytes==b'\x66\x98'else'EAX','semantic_registers_written':'AX'if i.bytes==b'\x98'else'DX'if i.bytes==b'\x99'else'EAX'if i.bytes==b'\x66\x98'else'EDX','flags':'unchanged'})
save('DATAFLOW/mnemonic_audit.json',corrections)
# Direct control-reference byte searches are locators, not validated instruction boundaries.
refs=[]
for entry in [0x1a,0x12e]:
 pattern=b'\x9a'+struct.pack('<HH',entry,0x1201);pos=image.find(pattern)
 while pos>=0:refs.append({'target':f'0201:{entry:04X}','image_offset':hex(pos),'bytes':pattern.hex(),'status':'raw_far_control_signature_candidate; source_boundary_unverified'});pos=image.find(pattern,pos+1)
save('DATAFLOW/math_helper_reference_candidates.json',refs)
# Cross-version local opcode templates, explicitly classify address immediates.
win_matches=[]
for lp in sorted((R/'VERSIONS/WIN16').glob('*.layout.json')):
 name=lp.name.removesuffix('.layout.json')
 if name=='MAPS.EXE':continue
 raw=(R.parent/'inputs/nite3/windows'/name).read_bytes();j=json.loads(lp.read_text());hits=[]
 for sg in j['segments']:
  if sg['kind']!='code' or not sg['file_backed']:continue
  data=raw[sg['file_offset']:sg['file_offset']+sg['size']]
  for m in re.finditer(re.escape(b'\xa0')+b'..'+re.escape(bytes.fromhex('2ae4cba0'))+b'..'+re.escape(bytes.fromhex('2ae4cb')),data,re.S):
   a,z=word(m[0],1),word(m[0],7)
   if z==a+1:hits.append({'segment':sg['index'],'entry_a':hex(m.start()),'entry_b':hex(m.start()+6),'DS_byte_a':hex(a),'DS_byte_b':hex(z),'bytes':m[0].hex()})
 win_matches.append({'file':name,'candidate_pairs':hits,'classification':'UNKNOWN_MATCH'if len(hits)!=1 else'IDENTICAL_BYTES'if hits[0]['bytes']=='a0e14b2ae4cba0e24b2ae4cb'else'MODIFIED_INSTRUCTIONS','equivalence_scope':'zero_extend_u8_from_corresponding_DS_offset; field meanings unknown'})
save('ASM_DIFF/win_getter_pair_cross_version.json',win_matches)
summary={'pass':'PASS002','new_function_body_audits':3,'refined_function_body_audits':1,'local_emulation_cases':len(cases)+len(getter),'exhaustive_dispatch_cases':len(dispatch),'startup_prefix_cases':1,'total_new_experiments':len(cases)+len(getter)+len(dispatch)+1,'fixed_point_divide_fault_cases':sum(x['expected_divide_fault']for x in cases),'switch_before_instruction_rows':len((R/'FUNCTIONS/DOS/DOS_2_0_0476_0326.asm').read_text().splitlines()),'switch_after_instruction_rows':switch_count,'math_instruction_rows':math_count,'switch_table_entries':24,'switch_table_distinct_targets':len(set(table)),'switch_unresolved_local_jumps':len(f_switch['unknown']),'math_unresolved_local_jumps':len(f_math['unknown']),'full_exhaustive_function_completions':0,'original_gameplay_runtime_verifications':0}
save('REPORTS/PASS002_metrics.json',summary);print(json.dumps(summary,indent=2));print('Win cross-version pairs',[(x['file'],len(x['candidate_pairs']))for x in win_matches]);print('reference signature candidates',refs)
