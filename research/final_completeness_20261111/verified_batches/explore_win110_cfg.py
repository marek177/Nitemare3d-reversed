"""Bounded static direct-flow exploration from actual NE entries.
Usage: python explore_win110_cfg.py EXE DECODER_DIR FIXUP_DIR OUT_DIR
Call continuations are may-return assumptions. No indirect targets are invented.
"""
import collections,csv,hashlib,json,struct,sys
from pathlib import Path

def csvrows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def csvout(p,rows,fields=None):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    exe,dep,fixdir,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep))
    from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind
    b=exe.read_bytes();h=hashlib.sha256(b).hexdigest()
    if h!='12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481':raise ValueError('EXE mismatch')
    ne=struct.unpack_from('<I',b,60)[0];word=lambda p:struct.unpack_from('<H',b,p)[0]
    table=ne+word(ne+0x22);shift=word(ne+0x32);segments={}
    for i in range(1,word(ne+0x1c)+1):
        sector,length,flags,_=struct.unpack_from('<4H',b,table+8*(i-1));off=sector<<shift;size=(length or 65536) if sector else 0
        segments[i]=dict(raw=b[off:off+size] if sector else b'',flags=flags,file_offset=off)
    imports={(int(r['segment']),int(r['instruction_offset'])):r for r in csvrows(fixdir/'far_candidates.csv')}
    if len(imports)!=len(csvrows(fixdir/'far_candidates.csv')):raise ValueError('duplicate FAR candidates')
    fmt=Formatter(FormatterSyntax.INTEL);queue=collections.deque();roots={};cache={};owners=collections.defaultdict(set);edge_map={};blocked=[];stats={}
    def valid(seg,ip):return seg in segments and not segments[seg]['flags']&1 and 0<=ip<len(segments[seg]['raw'])
    def addroot(seg,ip,reason):
        if not valid(seg,ip):blocked.append(dict(segment=seg,offset=ip,reason='root_outside_code_payload:'+reason));return
        if (seg,ip) not in roots:roots[(seg,ip)]={reason};queue.append((seg,ip))
        else:roots[(seg,ip)].add(reason)
    addroot(word(ne+0x16),word(ne+0x14),'NE program entry')
    p=ne+word(ne+4);end=p+word(ne+6);ordinal=1;exports=[]
    while p<end:
        count=b[p];p+=1
        if not count:break
        kind=b[p];p+=1
        if kind==0:ordinal+=count;continue
        for _ in range(count):
            if kind==255:
                if p+6>end:raise ValueError('movable entry bounds')
                flags=b[p];seg=b[p+3];ip=word(p+4);marker=word(p+1);p+=6
                if marker!=0x3fcd:raise ValueError('movable entry marker')
            else:
                if p+3>end:raise ValueError('fixed entry bounds')
                flags=b[p];seg=kind;ip=word(p+1);p+=3
            exports.append(dict(ordinal=ordinal,segment=seg,offset=ip,flags=flags));addroot(seg,ip,'NE entry-table ordinal %d'%ordinal);ordinal+=1
    def decode(seg,ip):
        key=(seg,ip)
        if key not in cache:
            ins=Decoder(16,segments[seg]['raw'][ip:ip+15],ip=ip).decode()
            if ins.is_invalid or ip+ins.len>len(segments[seg]['raw']):return None
            cache[key]=ins
        return cache[key]
    def edge(seg,ip,kind,tseg='',tip='',symbol='',scope=''):
        key=(seg,ip,kind,tseg,tip,symbol,scope)
        if key not in edge_map:edge_map[key]=dict(source_segment=seg,source_offset=ip,kind=kind,target_segment=tseg,target_offset=tip,target_symbol=symbol,scope=scope)
    limit=False
    while queue:
        if len(roots)>10000:limit=True;break
        root=queue.popleft();pending=[root];visited=set();counts=collections.Counter()
        while pending:
            seg,ip=pending.pop()
            if (seg,ip) in visited:continue
            if len(visited)>200000:limit=True;break
            visited.add((seg,ip))
            if not valid(seg,ip):blocked.append(dict(segment=seg,offset=ip,reason='flow_outside_code_payload'));continue
            ins=decode(seg,ip)
            if ins is None:blocked.append(dict(segment=seg,offset=ip,reason='invalid_instruction'));continue
            owners[(seg,ip)].add(root);counts['instructions']+=1;flow=ins.flow_control;nextip=ip+ins.len
            if flow==FlowControl.RETURN:edge(seg,ip,'return');counts['returns']+=1;continue
            if flow in (FlowControl.CALL,FlowControl.UNCONDITIONAL_BRANCH,FlowControl.CONDITIONAL_BRANCH):
                if ins.op_kind(0)==OpKind.FAR_BRANCH16:
                    binding=imports.get((seg,ip))
                    if binding and binding['effective_internal_segment']:
                        ts,ti=int(binding['effective_internal_segment']),int(binding['effective_internal_offset'])
                        edge(seg,ip,'internal_far_call' if flow==FlowControl.CALL else 'internal_far_jump',ts,ti,scope='selector-only NE fixup + preserved encoded offset')
                        if flow==FlowControl.CALL:addroot(ts,ti,'direct FAR call from %d:%04X'%(seg,ip))
                        elif valid(ts,ti):pending.append((ts,ti))
                    elif binding:
                        edge(seg,ip,'external_far_call' if flow==FlowControl.CALL else 'external_far_jump',symbol=binding['target'],scope='NE symbolic import; ordinal name may be unresolved');counts['external_calls']+=1
                    else:
                        edge(seg,ip,'unresolved_far_target',scope='no supported fixup binding');counts['unresolved']+=1
                else:
                    target=ins.near_branch_target
                    edge(seg,ip,'near_call' if flow==FlowControl.CALL else 'conditional_taken' if flow==FlowControl.CONDITIONAL_BRANCH else 'near_jump',seg,target)
                    if flow==FlowControl.CALL:addroot(seg,target,'direct NEAR call from %d:%04X'%(seg,ip))
                    else:pending.append((seg,target))
                if flow==FlowControl.UNCONDITIONAL_BRANCH:continue
            elif flow==FlowControl.INDIRECT_BRANCH:edge(seg,ip,'unresolved_indirect_jump');counts['unresolved']+=1;continue
            elif flow==FlowControl.INDIRECT_CALL:edge(seg,ip,'unresolved_indirect_call');counts['unresolved']+=1
            elif flow==FlowControl.INTERRUPT:edge(seg,ip,'interrupt_semantics_open');counts['unresolved']+=1
            elif flow not in (FlowControl.NEXT,):edge(seg,ip,'other_control_semantics_open');counts['unresolved']+=1;continue
            edge(seg,ip,'may_return_continuation' if flow in (FlowControl.CALL,FlowControl.INDIRECT_CALL,FlowControl.INTERRUPT) else 'fallthrough',seg,nextip,scope='continuation after call/interrupt is an assumption' if flow in (FlowControl.CALL,FlowControl.INDIRECT_CALL,FlowControl.INTERRUPT) else '')
            pending.append((seg,nextip))
        stats[root]=counts
    instructions=[];byte_starts=collections.defaultdict(set);conflict_bytes=set();unique_bytes=set()
    for (seg,ip),rs in sorted(owners.items()):
        ins=cache[(seg,ip)];raw=segments[seg]['raw'][ip:ip+ins.len]
        for pos in range(ip,ip+ins.len):
            if byte_starts[(seg,pos)] and ip not in byte_starts[(seg,pos)]:conflict_bytes.add((seg,pos))
            byte_starts[(seg,pos)].add(ip);unique_bytes.add((seg,pos))
        instructions.append(dict(segment=seg,offset=ip,file_offset=segments[seg]['file_offset']+ip,bytes=raw.hex(),instruction=fmt.format(ins),flow_control=ins.flow_control,owner_roots=';'.join('%d:%04X'%r for r in sorted(rs)),status='PARTIAL',scope='statically explored from NE entries; may-return continuations assumed'))
    conflicts=[]
    for seg,pos in sorted(conflict_bytes):
        for start in sorted(byte_starts[(seg,pos)]):
            ins=cache[(seg,start)]
            conflicts.append(dict(segment=seg,byte_offset=pos,instruction_start=start,bytes=segments[seg]['raw'][start:start+ins.len].hex(),instruction=fmt.format(ins),owner_roots=';'.join('%d:%04X'%r for r in sorted(owners[(seg,start)])),status='UNKNOWN_DECODE_CONFLICT'))
    functions=[dict(segment=s,offset=i,root_provenance=';'.join(sorted(reasons)),local_explored_instructions=stats.get((s,i),{}).get('instructions',0),returns=stats.get((s,i),{}).get('returns',0),unresolved_control_sites=stats.get((s,i),{}).get('unresolved',0),external_calls=stats.get((s,i),{}).get('external_calls',0),status='PARTIAL',scope='candidate function root, not closed semantic contract') for (s,i),reasons in sorted(roots.items())]
    out.mkdir(parents=True,exist_ok=True);csvout(out/'entry_table.csv',exports);csvout(out/'instructions.csv',instructions);csvout(out/'edges.csv',list(edge_map.values()));csvout(out/'function_candidates.csv',functions);csvout(out/'blocked_flow.csv',blocked,['segment','offset','reason'])
    csvout(out/'decode_conflicts.csv',conflicts,['segment','byte_offset','instruction_start','bytes','instruction','owner_roots','status'])
    summary=dict(exe_sha256=h,entry_table_entries=len(exports),program_entry='%d:%04X'%(word(ne+0x16),word(ne+0x14)),function_candidate_roots=len(roots),unique_explored_instruction_starts=len(instructions),unique_explored_instruction_bytes=len(unique_bytes),overlapping_decode_bytes=len(conflict_bytes),edge_counts=dict(collections.Counter(e['kind'] for e in edge_map.values())),blocked_flow_events=len(blocked),exploration_limit_hit=limit,unresolved_indirect_targets=True,may_return_assumptions=True,closed_function_contracts=0,new_deep_verified_bytes=0,runtime_tests=0,scope='bounded direct-flow exploration, not global code coverage or runtime reachability')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
