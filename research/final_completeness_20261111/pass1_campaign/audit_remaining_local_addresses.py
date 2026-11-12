"""IMAGE MAP INVENTORY DECODER OUT. Conservative local constant-address witnesses.
No reachability, mutable-memory constant inference or status promotions.
"""
import csv,hashlib,json,sys
from pathlib import Path
image,mapping,inventory,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,InstructionInfoFactory,Register,RegisterExt,OpKind,OpAccess,Mnemonic,FlowControl,MemorySizeExt
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rs=json.loads(inventory.read_text(encoding='utf-8'));remaining=[r for r in csv.DictReader(mapping.open(encoding='utf-8-sig')) if r['status'] in ('UNKNOWN','CLASSIFIED ONLY')];out.mkdir(exist_ok=True)
fmt=Formatter(FormatterSyntax.INTEL);factory=InstructionInfoFactory();decoded={};targets=set();rows=[];resolved_rows=[];stats=dict(verified_inventory_starts=0,blocks=0,memory_operands=0,resolved_local_memory_operands=0,resolved_explicit_segments=0,unresolved_memory_operands=0)
for r in rs:
 p=r['image_offset'];raw=bytes.fromhex(r['bytes']);assert b[p:p+len(raw)]==raw
 i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);decoded[(r['cs'],r['ip'])]=(r,i)
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):targets.add((r['cs'],i.near_branch_target))

def key(reg):
 if RegisterExt.is_gpr(reg):return RegisterExt.full_register32(reg)
 return reg
def part(reg):
 width=RegisterExt.size(reg)*8;shift=8 if reg in (Register.AH,Register.BH,Register.CH,Register.DH) else 0
 return shift,((1<<width)-1)<<shift
def get(reg):
 if reg==Register.NONE:return (0,[])
 k=key(reg);shift,mask=part(reg);known,value,proof=values.get(k,(0,0,[]))
 return ((value&mask)>>shift,proof) if known&mask==mask else None
def put(reg,result,origin):
 k=key(reg);shift,mask=part(reg);known,value,proof=values.get(k,(0,0,[]))
 if result is None:values[k]=(known&~mask,value&~mask,proof);return
 val,prior=result;retained=proof if known&~mask else [];values[k]=(known|mask,(value&~mask)|((val<<shift)&mask),sorted(set(prior+retained+[origin]),key=str))
def immediate(i,n):
 if i.op_kind(n) in (OpKind.IMMEDIATE8,OpKind.IMMEDIATE8_2ND,OpKind.IMMEDIATE16,OpKind.IMMEDIATE32,OpKind.IMMEDIATE64,OpKind.IMMEDIATE8TO16,OpKind.IMMEDIATE8TO32,OpKind.IMMEDIATE8TO64,OpKind.IMMEDIATE32TO64):return (i.immediate(n),[])
 return None
def operand(i,n):return get(i.op_register(n)) if i.op_kind(n)==OpKind.REGISTER else immediate(i,n)
def effective(base,index,scale,disp,bits):
 a=get(base);c=get(index)
 if a is None or c is None:return None
 return ((a[0]+c[0]*scale+disp)&((1<<bits)-1),sorted(set(a[1]+c[1]),key=str))

previous=None;values={};block=[];df=None;constant_stack=[]
for (cs,ip),(r,i) in sorted(decoded.items()):
 if previous is None or previous[0]!=cs or previous[1]!=ip or (cs,ip) in targets:
  values={};put(Register.CS,(cs,[]),'CS_FROM_INVENTORY');put(Register.DS,(0x2771,[]),'ASSUMED_DEFAULT_DS_AT_BLOCK_ENTRY');block=[];df=None;constant_stack=[];stats['blocks']+=1
 stats['verified_inventory_starts']+=1;block.append(r['image_offset']);info=factory.info(i)
 for mem in info.used_memory():
  stats['memory_operands']+=1;seg=get(mem.segment);ea=effective(mem.base,mem.index,mem.scale,mem.displacement,32 if mem.address_size==2 else 16)
  if seg is None or ea is None:stats['unresolved_memory_operands']+=1;continue
  stats['resolved_local_memory_operands']+=1;proof=sorted(set(seg[1]+ea[1]),key=str);conditional='ASSUMED_DEFAULT_DS_AT_BLOCK_ENTRY' in proof
  if not conditional:stats['resolved_explicit_segments']+=1
  address=seg[0]*16+ea[0];width=max(1,MemorySizeExt.size(mem.memory_size));count=1
  if (i.has_rep_prefix or i.has_repne_prefix) and df is not None:
   cx=get(Register.CX)
   if cx is not None:
    count=cx[0];proof=sorted(set(proof+cx[1]),key=str)
  if count==0:continue
  # Do not infer a contiguous span across offset wrap or REPNE early exit.
  if i.has_repne_prefix:count=1
  if df==1 and ea[0]-(count-1)*width<0:count=1
  span=width*count
  if df==1:address-=(count-1)*width
  if span>65536 or ea[0]+span>65536:span=width
  resolved_rows.append(dict(instruction_image=r['image_offset'],instruction=fmt.format(i),segment=seg[0],offset=ea[0],linear_start=address,span_bytes=span,conditional_default_DS=conditional,proof=json.dumps(proof),block_start=block[0]))
  hits=[]
  for target in remaining:
   a,z=int(target['start']),int(target['end_exclusive'])
   if address<z and address+span>a:hits.append((a,z,target['status']))
  for a,z,status in hits:
   row=dict(interval_start=a,interval_end_exclusive=z,interval_status=status,instruction_image=r['image_offset'],cs=cs,ip=ip,bytes=r['bytes'],instruction=fmt.format(i),resolved_segment=seg[0],resolved_offset=ea[0],linear_start=address,span_bytes=span,operand_access=mem.access,conditional_default_DS=conditional,proof=json.dumps(proof),block_start=block[0],scope='local constant-address candidate only; incoming segment assumption explicit, runtime reachability/domain unproved')
   rows.append(row)
 # Calculate a supported register result from pre-instruction state, then invalidate all writes.
 result=None;dest=None
 if i.op_count and i.op_kind(0)==OpKind.REGISTER:
  dest=i.op_register(0);mn=i.mnemonic
  if mn==Mnemonic.MOV and i.op_count==2:result=operand(i,1)
  elif mn==Mnemonic.POP:result=constant_stack.pop() if constant_stack else None
  elif mn==Mnemonic.LEA:result=effective(i.memory_base,i.memory_index,i.memory_index_scale,i.memory_displacement,32 if RegisterExt.size(dest)==4 else 16)
  elif mn in (Mnemonic.XOR,Mnemonic.SUB) and i.op_count==2 and i.op_kind(1)==OpKind.REGISTER and dest==i.op_register(1):result=(0,[])
  elif mn in (Mnemonic.ADD,Mnemonic.SUB,Mnemonic.AND,Mnemonic.OR,Mnemonic.XOR,Mnemonic.SHL,Mnemonic.SHR):
   x=get(dest);y=operand(i,1)
   if x is not None and y is not None:
    av,bv=x[0],y[0];value={Mnemonic.ADD:lambda:av+bv,Mnemonic.SUB:lambda:av-bv,Mnemonic.AND:lambda:av&bv,Mnemonic.OR:lambda:av|bv,Mnemonic.XOR:lambda:av^bv,Mnemonic.SHL:lambda:av<<(bv&31),Mnemonic.SHR:lambda:av>>(bv&31)}[mn]()
    result=(value,sorted(set(x[1]+y[1]),key=str))
  elif mn in (Mnemonic.INC,Mnemonic.DEC):
   x=get(dest)
   if x is not None:result=(x[0]+(1 if mn==Mnemonic.INC else -1),x[1])
 if i.mnemonic==Mnemonic.PUSH:constant_stack.append(operand(i,0))
 elif i.mnemonic not in (Mnemonic.POP,Mnemonic.PUSH) and any(u.register in (Register.SP,Register.ESP) and u.access in (OpAccess.WRITE,OpAccess.COND_WRITE,OpAccess.READ_WRITE,OpAccess.READ_COND_WRITE) for u in info.used_registers()):constant_stack=[]
 for used in info.used_registers():
  if used.access in (OpAccess.WRITE,OpAccess.COND_WRITE,OpAccess.READ_WRITE,OpAccess.READ_COND_WRITE):
   if RegisterExt.is_gpr(used.register) or RegisterExt.is_segment_register(used.register):put(used.register,None,r['image_offset'])
 if dest is not None and result is not None:put(dest,result,r['image_offset'])
 if i.mnemonic==Mnemonic.CLD:df=0
 if i.mnemonic==Mnemonic.STD:df=1
 previous=(cs,i.next_ip) if i.flow_control==FlowControl.NEXT else None

fields=list(rows[0]) if rows else ['instruction_image','scope']
with (out/'candidates.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
with (out/'resolved_addresses.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(resolved_rows[0]));w.writeheader();w.writerows(resolved_rows)
summary=dict(**stats,remaining_intervals=len(remaining),remaining_bytes=sum(int(r['length']) for r in remaining),candidate_rows=len(rows),candidate_intervals=len(set((r['interval_start'],r['interval_end_exclusive']) for r in rows)),status_changes=0,new_deep_verified_bytes=0,runtime_tests=0,scope='Supported local register constant operations; branch entries/calls reset. Mutable memory loads are never inferred constant. DS2771 at block entry is an explicit candidate-only assumption. REPNE counted only first element; not absence proof, exhaustive symbolic execution or promotions.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,mapping,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
