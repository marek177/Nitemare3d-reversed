from pathlib import Path
import csv,json,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];branch_cases=0
for q in json.loads((root/'pass5/evidence/scopes.json').read_text()):
 v=q['build'];d=root/'pass5/audit'/('DOS'+v);rows=list(csv.DictReader((d/'explicit_model_results.tsv').open(),delimiter='\t'));stock={r['entry']:r for r in rows if r['model']=='stock'};view={r['entry']:r for r in rows if r['model']=='explicit_real_mode_pcode_view'};old={r['entry']:r for r in csv.DictReader((root/'pass4/audit'/('DOS'+v)/'functions.tsv').open(),delimiter='\t')};assert stock.keys()==view.keys()==old.keys()
 good=lambda x:x['completed']=='true' and x.get('C_available','true')=='true'
 assert all(good(stock[k])==good(old[k]) for k in old)
 regression=[k for k in stock if good(stock[k]) and not good(view[k])];assert not regression
 before=list(csv.DictReader((root/'pass4/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));after=list(csv.DictReader((d/'instructions.tsv').open(),delimiter='\t'));assert [(r['address'],r['bytes']) for r in before]==[(r['address'],r['bytes']) for r in after]
 imap={r['address']:r for r in before};events=list(csv.DictReader((d/'explicit_pcode_changes.tsv').open(),delimiter='\t'));audit={r['address']:r for r in csv.DictReader((root/'pass5/evidence'/('DOS'+v)/'scope_audit/rewrite_scope.tsv').open(),delimiter='\t')}
 def phys(a):s,o=map(lambda x:int(x,16),a.split(':'));return s*16+o
 far=[];near=[]
 for e in events:
  p=phys(e['source'])
  if e['kind']=='SEGMENT_LINEARIZE':
   assert q['far1_start']<=p<=q['far1_end'] or q['far2_start']<=p<=q['far2_end'];a=next(r for a,r in audit.items() if phys(a)==p);assert int(a['segment_ops'])>0 and int(a['internal_branches'])==0 and int(a['max_original_unique'],16)<0x70000000;far.append(e['source'])
  else:
   assert q['near_start']<=p<=q['near_end'];bb=bytes.fromhex(next(r for a,r in imap.items() if phys(a)==p)['bytes']);assert len(bb)==4 and bb[:2] in [b'\x0f\x84',b'\x0f\x85'];off=p-q['near_start'];target=q['near_start']+((off+4+int.from_bytes(bb[2:],'little',signed=True))&65535);assert int(e['input_or_new_target'],16)==target;near.append(e['source'])
   for flags in range(16):
    zf=(flags>>1)&1;u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(p,bb);u.reg_write(UC_X86_REG_CS,q['renderer_CS']);u.reg_write(UC_X86_REG_EFLAGS,2|(flags&1)|(zf<<6)|(((flags>>2)&1)<<7)|(((flags>>3)&1)<<11));u.emu_start(p,0,count=1);taken=bool(zf) if bb[1]==0x84 else not bool(zf);assert u.reg_read(UC_X86_REG_IP)==((target-q['near_start']) if taken else off+4);branch_cases+=1
 owner=json.loads((root/'pass5/evidence'/('owner_'+v+'.json')).read_text());assert owner['passed']==1371
 results.append(dict(build=v,functions=len(stock),stock_completed=sum(good(r) for r in stock.values()),explicit_view_completed=sum(good(r) for r in view.values()),recovered_only_in_explicit_view=[k for k in stock if not good(stock[k]) and good(view[k])],remaining_in_explicit_view=[k for k in view if not good(view[k])],regressions=regression,unchanged_defined_instructions=len(after),far_rewrite_sites=len(set(far)),near_rewrite_sites=len(set(near)),owner_cases=owner['passed'],AX_boolean_disagreements=sum(bool(x['raw_AX'])!=bool(x['AL']) for x in owner['results'])))
(root/'pass5/evidence/validation.json').write_text(json.dumps(dict(builds=results,synthetic_branch_cases=branch_cases),indent=2));print([(r['build'],r['stock_completed'],r['explicit_view_completed']) for r in results]);print('extra C only in explicit view',sum(len(r['recovered_only_in_explicit_view']) for r in results),'remaining',sum(len(r['remaining_in_explicit_view']) for r in results),'branch tests',branch_cases)
