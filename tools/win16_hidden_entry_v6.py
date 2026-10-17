#!/usr/bin/env python3
"""Binary-first High-only Win16 hidden-entry closure.

The v5 corpus is input evidence, never executable Python. No medium candidate is
promoted. Addresses named selectors are static analysis selectors, not runtime
Windows selectors; no flat runtime VA can be recovered from an on-disk NE file.
"""
import argparse, csv, hashlib, json, re, struct, subprocess, tempfile
from collections import Counter, defaultdict
from pathlib import Path

VERSIONS = {'1.0':'NITE3W -10.EXE','1.3':'NITE3W - 13.EXE',
            '1.6':'NITE3W - 16.EXE','1.8':'NITE3W - 18.EXE','1.10':'nite3w - 110.exe'}
HASHES = {'1.0':'6476e259a3a763e2985f22ea6655929e5b313f63ca4bcb976f98b6d50b72140c',
 '1.3':'926c0001944b9822cdae10b35c92c2d6cd3772bc774c4c88fb17df7465d1f156',
 '1.6':'5851849bacd8b03e93444d8a8f34d51c23fecddc73d6b8df7f016885c3b9d418',
 '1.8':'144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22',
 '1.10':'12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481'}
SELECTORS = {1:'1000',2:'1008',3:'1010',4:'1018'}
ASM = re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-zA-Z][a-zA-Z0-9.]*)\s*(.*)$')
COND = {'je','jne','jz','jnz','jl','jle','jg','jge','jb','jbe','ja','jae','jc','jnc','jo','jno','js','jns','jp','jnp','jcxz','loop','loope','loopne','loopz','loopnz'}
csv.field_size_limit(10000000)

def readcsv(path):
    with open(path, newline='', encoding='utf-8') as f: return list(csv.DictReader(f))

def writecsv(path, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n"); w.writeheader(); w.writerows(rows)

def number(x): return int(x,16) if str(x).lower().startswith('0x') else int(float(x))
def target(op):
    m=re.search(r'(?:^|\s)0x([0-9a-f]+)$',op.strip()); return int(m[1],16) if m else None

def parseasm(text):
    out={}
    for line in text.splitlines():
        m=ASM.match(line)
        if m: out[int(m[1],16)]={'offset':int(m[1],16),'bytes':bytes.fromhex(m[2]),'mn':m[3].lower(),'op':m[4].strip()}
    return out

def reachable(by,start):
    todo=[start]; seen=set()
    while todo:
        a=todo.pop()
        if a in seen or a not in by: continue
        seen.add(a); x=by[a]; mn=x['mn']; nxt=a+len(x['bytes'])
        if mn.startswith(('ret','lret')) or mn in {'iret','hlt'}: continue
        if mn in {'jmp','ljmp'}:
            t=target(x['op']) if mn=='jmp' else None
            if t is not None: todo.append(t)
        else:
            todo.append(nxt)
            if mn in COND:
                t=target(x['op'])
                if t is not None: todo.append(t)
    return seen

class Binary:
    def __init__(self,path,version):
        self.path=path; self.version=version; self.data=path.read_bytes()
        self.sha=hashlib.sha256(self.data).hexdigest()
        if self.sha!=HASHES[version]: raise ValueError(f'Unexpected binary hash: {version}')
        d=self.data; u=lambda o:struct.unpack_from('<H',d,o)[0]
        ne=struct.unpack_from('<I',d,0x3c)[0]
        if d[:2]!=b'MZ' or d[ne:ne+2]!=b'NE': raise ValueError('Not MZ/NE')
        self.segments={}; self.fixups={}; self.cache={}
        tab=ne+u(ne+0x22); shift=u(ne+0x32); imp=ne+u(ne+0x2a)
        def string(o): return d[o+1:o+1+d[o]].decode('latin1')
        modules=[string(imp+u(ne+u(ne+0x28)+i*2)) for i in range(u(ne+0x1e))]
        entries={}; pos=ne+u(ne+4); end=pos+u(ne+6); ordinal=1
        while pos<end:
            count=d[pos]; pos+=1
            if not count:break
            typ=d[pos];pos+=1
            for _ in range(count):
                if typ==0: entries[ordinal]=None
                elif typ==0xff:
                    entries[ordinal]=(d[pos+3],u(pos+4));pos+=6
                elif typ==0xfe:entries[ordinal]=None;pos+=3
                else:entries[ordinal]=(typ,u(pos+1));pos+=3
                ordinal+=1
        self.entry_table=entries
        self.record_count=0;self.site_count=0
        for i in range(u(ne+0x1c)):
            sec,length,flags,_=struct.unpack_from('<HHHH',d,tab+8*i)
            fo=sec<<shift; length=length or 65536
            self.segments[i+1]={'file_offset':fo,'bytes':d[fo:fo+length] if sec else b'','flags':flags}
        for seg,sg in self.segments.items():
            if not sg['file_offset'] or not sg['flags']&0x100:continue
            raw=sg['bytes'];ro=sg['file_offset']+len(raw);count=u(ro);self.record_count+=count
            for j in range(count):
                record_file=ro+2+j*8;st,flags,src,a,b=struct.unpack_from('<BBHHH',d,record_file)
                kind=flags&3; additive=bool(flags&4); seen=set();site=src;chain=0
                while True:
                    if site in seen or site+2>len(raw):raise ValueError('Broken NE source chain')
                    seen.add(site);nxt=struct.unpack_from('<H',raw,site)[0];self.site_count+=1
                    opcode=None
                    if st==3 and site>=1 and raw[site-1] in (0x9a,0xea):opcode=site-1
                    if st==2 and site>=3 and raw[site-3] in (0x9a,0xea):opcode=site-3
                    tseg=toff=None;symbol=''
                    if kind==0:
                        if a&255==255:
                            ent=entries.get(b)
                            if ent:tseg,toff=ent
                        else:
                            tseg=a&255;toff=struct.unpack_from('<H',raw,site-2)[0] if st==2 and opcode is not None else b
                    elif kind in (1,2):
                        module=modules[a-1];symbol=f'{module}!#{b}' if kind==1 else f'{module}!{string(imp+b)}'
                    row={'source_segment':seg,'source_fixup_offset':hex(site),'opcode_site_offset':hex(opcode) if opcode is not None else '',
                         'record_index':j,'record_file_offset':hex(record_file),'record_bytes':d[record_file:record_file+8].hex(),
                         'source_type':hex(st),'flags':hex(flags),'chain_index':chain,'next_chain_offset':hex(nxt),
                         'target_segment':tseg,'target_offset':hex(toff) if toff is not None else '', 'import_symbol':symbol,
                         'target_kind':kind,'additive':additive}
                    if opcode is not None:
                        key=(seg,opcode)
                        if key in self.fixups:raise ValueError('Multiple fixups at opcode')
                        self.fixups[key]=row
                    if additive or nxt==0xffff:break
                    site=nxt;chain+=1
    def dis(self,seg,start):
        k=(seg,start)
        if k not in self.cache:
            raw=self.segments[seg]['bytes']
            if not 0<=start<len(raw):return {}
            with tempfile.NamedTemporaryFile() as f:
                f.write(raw[start:]);f.flush()
                text=subprocess.check_output(['objdump','-D','-b','binary','-m','i8086','--insn-width=16',f'--adjust-vma={start}',f.name],text=True)
            self.cache[k]=parseasm(text)
        return self.cache[k]
    def trace(self,seg,start):
        by=self.dis(seg,start).copy();todo=[start];seen={};errors=[]
        while todo:
            a=todo.pop()
            if a in seen:continue
            if a not in by:by.update(self.dis(seg,a))
            x=by.get(a)
            if not x or x['mn'] in {'.byte','data16','addr32'} or '(bad)' in x['op']:
                errors.append(f'undecodable:{a:04x}');continue
            # Reject overlapping instruction streams, including branches into operands.
            if any(p<a<p+len(q['bytes']) or a<p<a+len(x['bytes']) for p,q in seen.items()):
                errors.append(f'overlapping-instructions:{a:04x}');continue
            seen[a]=x;mn=x['mn'];nxt=a+len(x['bytes'])
            if mn.startswith(('ret','lret')):continue
            if mn in {'iret','hlt'}:errors.append(f'non-return-terminal:{a:04x}');continue
            if mn in {'jmp','ljmp'}:
                t=target(x['op']) if mn=='jmp' else None
                if t is None:errors.append(f'unclosed-jump:{a:04x}')
                else:todo.append(t)
            else:
                todo.append(nxt)
                if mn in COND:
                    t=target(x['op'])
                    if t is None:errors.append(f'unclosed-branch:{a:04x}')
                    else:todo.append(t)
            if len(seen)>10000:raise ValueError('Unbounded CFG')
        return seen,errors

def intervals(corpus,version):
    filename='win16_10_machine_functions_cfg_v5.csv' if version=='1.0' else f'win16_{version.replace(".","")}_machine_functions_v4.csv'
    rows=[]
    for r in readcsv(corpus/filename):
        start=number(r.get('start_offset',r.get('start')));end=number(r.get('end_offset',r.get('end')))
        by=parseasm(r['assembly']);reach=reachable(by,start)
        rows.append({'function':r['function'],'source10':r.get('source10_function',r['function']),
                     'seg':int(r['segment_ordinal']),'start':start,'end':end,'ins':by,'reach':reach})
    return rows

def address(seg,off):return f'{SELECTORS[seg]}:{off:04X}'
def fn(seg,off):return f'HIDDEN_{SELECTORS[seg]}_{off:04x}'

def mask_pattern(binary,seg,start,ins):
    end=max(p+len(x['bytes']) for p,x in ins.items());data=binary.segments[seg]['bytes'][start:end]; mask=bytearray(b'\xff'*len(data))
    for p,x in ins.items():
        q=p-start;bs=x['bytes'];mn=x['mn'];op=x['op']
        if mn=='lcall': mask[q+1:q+len(bs)]=b'\0'*(len(bs)-1)
        elif mn=='call' and not op.startswith('*'):mask[q+1:q+len(bs)]=b'\0'*(len(bs)-1)
        # Absolute DS data locations drift. Preserve BP/register displacement and
        # branch displacement; only no-base absolute memory operands are masked.
        for m in re.finditer(r'(?<![$\w])0x([0-9a-f]+)(?![\w])',op):
            if mn in COND or mn in {'jmp','ljmp','call','lcall'}:continue
            value=int(m[1],16)
            suffix=op[m.end():]
            if suffix.startswith('(') and re.match(r'\([^)]*%(?:bp|sp)',suffix):continue
            if value<=65535:
                needle=value.to_bytes(2,'little');at=bs.find(needle)
                if at>=0:mask[q+at:q+at+2]=b'\0\0'
        # Large pushed addresses are structural operands, not semantic equivalence.
        if mn=='push' and op.startswith('$0x') and int(op[3:],16)>255:
            mask[q+1:q+len(bs)]=b'\0'*(len(bs)-1)
    regex=b''.join(re.escape(bytes([b])) if mask[i] else b'.' for i,b in enumerate(data))
    return data,bytes(mask),regex

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binaries',type=Path,required=True);ap.add_argument('--v5-output',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    bins={v:Binary(args.binaries/name,v) for v,name in VERSIONS.items()}
    olds={v:intervals(args.v5_output,v) for v in VERSIONS}
    candidates=readcsv(args.v5_output/'win16_hidden_entry_candidates_aggregated_v5.csv')
    fix_v5=readcsv(args.v5_output/'win16_ne_fixup_sites_cfg_refined_v5.csv')
    dossiers=[];audit=[];bykey={}
    for c in candidates:
        if c['confidence']!='High':continue
        v=c['version'];s=int(c['segment_ordinal']);a=number(c['candidate_offset']);b=bins[v]
        ins,errors=b.trace(s,a)
        # Independently re-expand the NE source chain; require an exact reachable
        # instruction boundary at the originating v5 indexed caller.
        incoming=[]
        for f in fix_v5:
            if f['version']!=v or not f['target_kind'].startswith('internal') or f['cfg_reachable_from_owner'].lower()!='true':continue
            if not f['target_segment'] or not f['target_offset']:continue
            if number(f['target_segment'])!=s or number(f['target_offset'])!=a:continue
            ss=int(f['source_segment_ordinal']);site=number(f['opcode_site_offset']);raw=b.fixups.get((ss,site))
            owner=next((r for r in olds[v] if r['function']==f['cfg_owner_function']),None)
            decoded=owner['ins'].get(site) if owner else None
            if not raw or raw['target_segment']!=s or number(raw['target_offset'])!=a or not decoded or decoded['mn']!='lcall' or decoded['bytes']!=b.segments[ss]['bytes'][site:site+len(decoded['bytes'])]:
                errors.append('incoming-fixup-or-instruction-mismatch');continue
            incoming.append({**raw,'caller':owner['function'],'caller_source10':owner['source10'],'caller_address':address(ss,owner['start']), 'call_site_address':address(ss,site)})
        if not incoming:errors.append('no-verified-incoming-call')
        previous=[r for r in olds[v] if r['seg']==s and a in r['reach']]
        boundary_notes=[]
        for r in previous:
            # The known D7CC entry is inside a separately proved CALL operand.
            containers=[q for q in dossiers if q['version']==v and q['segment_ordinal']==s and any(p<r['start']<p+len(x['bytes']) for p,x in q['_ins'].items())]
            # Probe all High starts to avoid dependence on candidate CSV ordering.
            if not containers:
                for cc in candidates:
                    if cc['confidence']=='High' and cc['version']==v and int(cc['segment_ordinal'])==s and number(cc['candidate_offset'])<a:
                        ii,ee=b.trace(s,number(cc['candidate_offset']))
                        if not ee and any(p<r['start']<p+len(x['bytes']) for p,x in ii.items()):containers=[cc];break
            old_entry_referenced=any(f['target_segment']==s and f['target_offset'] and number(f['target_offset'])==r['start'] for f in b.fixups.values()) or (s,r['start']) in b.entry_table.values() or any(q['seg']==s and x['mn']=='call' and target(x['op'])==r['start'] for q in olds[v] for p,x in q['ins'].items() if p in q['reach'])
            if containers and not old_entry_referenced:boundary_notes.append(f"{r['function']} starts inside another verified High routine instruction operand; mapped interval is not an independent entry proof")
            else:errors.append('reachable-from-existing-entry:'+r['function'])
        ret=[p for p,x in ins.items() if x['mn'].startswith(('ret','lret'))]
        if not ret:errors.append('no-return')
        status='deferred' if errors else 'promoted'
        audit.append({'version':v,'address':address(s,a),'status':status,'confidence':'High','errors':' | '.join(errors),'boundary_notes':' | '.join(boundary_notes)})
        if errors:continue
        end=max(p+len(x['bytes']) for p,x in ins.items());raw=b.segments[s]['bytes'][a:end]
        ranges=[]
        for p,x in sorted(ins.items()):
            e=p+len(x['bytes'])
            if ranges and ranges[-1][1]==p:ranges[-1][1]=e
            else:ranges.append([p,e])
        parents=[r for r in olds[v] if r['seg']==s and r['start']<=a<r['end']]
        d={'platform':'Win16','version':v,'function':fn(s,a),'segment_ordinal':s,'selector':SELECTORS[s],
           'entry':address(s,a),'start_offset':hex(a),'end_offset_exclusive':hex(end),'size_envelope_bytes':end-a,
           'reachable_bytes':sum(len(x['bytes']) for x in ins.values()),'reachable_ranges':[[hex(p),hex(e)] for p,e in ranges],
           'address_space':'Ghidra analysis selector:offset; NE ordinal mapping 1=1000,2=1008,3=1010,4=1018',
           'runtime_va':None,'runtime_va_reason':'Windows loader selects actual selectors; no stable flat runtime VA in NE binary',
           'file_offset':hex(b.segments[s]['file_offset']+a),'file_end_exclusive':hex(b.segments[s]['file_offset']+end),
           'binary_filename':b.path.name,'binary_sha256':b.sha,'body_sha256':hashlib.sha256(raw).hexdigest(),
           'entry_confidence':'High','boundary_confidence':'High','semantic_status':'Unknown','semantic_confidence':'Unknown',
           'classification':'unclassified-application-or-runtime','classification_status':'Unknown',
           'incoming_evidence':incoming,'previous_intervals':[r['function'] for r in parents],
           'previous_source10_intervals':[r['source10'] for r in parents],'boundary_notes':boundary_notes,
           'instruction_count':len(ins),'return_sites':[hex(p) for p in sorted(ret)],
           'branch_sites':[hex(p) for p,x in sorted(ins.items()) if x['mn'] in COND or x['mn'] in {'jmp','ljmp'}],
           'assembly':[{'offset':hex(p),'bytes':x['bytes'].hex(),'mnemonic':x['mn'],'operand':x['op']} for p,x in sorted(ins.items())], '_ins':ins}
        dossiers.append(d);bykey[(v,s,a)]=d
    # Cross-build search is a relation ledger. Matches without their own High
    # candidate evidence are reference bodies only, never additional dossiers.
    relations=[]
    for d in dossiers:
        v=d['version'];s=d['segment_ordinal'];a=number(d['start_offset']);data,mask,pattern=mask_pattern(bins[v],s,a,d['_ins'])
        imports=[bins[v].fixups[(s,p)]['import_symbol'] for p,x in sorted(d['_ins'].items()) if x['mn']=='lcall' and (s,p) in bins[v].fixups]
        for vv,b in bins.items():
            matches=[]
            for ss in SELECTORS:
                raw=b.segments[ss]['bytes']
                for m in re.finditer(b'(?=('+pattern+b'))',raw,re.DOTALL):
                    aa=m.start();ii,ee=b.trace(ss,aa)
                    if ee or len(ii)!=len(d['_ins']):continue
                    # Preserve complete reachable instruction layout and import identity.
                    if [(p-aa,x['mn'],len(x['bytes'])) for p,x in sorted(ii.items())]!=[(p-a,x['mn'],len(x['bytes'])) for p,x in sorted(d['_ins'].items())]:continue
                    imp=[b.fixups[(ss,p)]['import_symbol'] for p,x in sorted(ii.items()) if x['mn']=='lcall' and (ss,p) in b.fixups]
                    if imports!=imp:continue
                    parents=[r for r in olds[vv] if r['seg']==ss and r['start']<=aa<r['end']]
                    source_anchor=bool(set(d['previous_source10_intervals'])&{r['source10'] for r in parents})
                    incoming_anchor=any(x['target_segment']==ss and x['target_offset'] and number(x['target_offset'])==aa for x in b.fixups.values())
                    callee_anchors=0
                    for (p,x),(pp,xx) in zip(sorted(d['_ins'].items()),sorted(ii.items())):
                        f=bins[v].fixups.get((s,p));ff=b.fixups.get((ss,pp))
                        if not f or not ff or f['target_segment'] is None or ff['target_segment'] is None:continue
                        o=next((q for q in olds[v] if q['seg']==f['target_segment'] and q['start']<=number(f['target_offset'])<q['end']),None)
                        oo=next((q for q in olds[vv] if q['seg']==ff['target_segment'] and q['start']<=number(ff['target_offset'])<q['end']),None)
                        if o and oo and o['source10']==oo['source10']:callee_anchors+=1
                    matches.append((ss,aa,source_anchor,incoming_anchor,callee_anchors))
            anchored=[m for m in matches if m[2]]
            eligible=anchored if anchored else matches
            if vv==v:eligible=[m for m in matches if m[0]==s and m[1]==a]
            elif len(eligible)>1:
                score=max(m[4] for m in eligible)
                if score>=2:eligible=[m for m in eligible if m[4]==score]
            unique=len(eligible)==1
            chosen=eligible[0] if unique else None
            rel={'from_version':v,'from_entry':d['entry'],'to_version':vv,
                 'to_entry':address(chosen[0],chosen[1]) if chosen else '',
                 'to_end_offset_exclusive':hex(chosen[1]+len(data)) if chosen else '',
                 'to_file_offset':hex(b.segments[chosen[0]]['file_offset']+chosen[1]) if chosen else '',
                 'to_binary_sha256':b.sha,
                 'to_body_sha256':hashlib.sha256(b.segments[chosen[0]]['bytes'][chosen[1]:chosen[1]+len(data)]).hexdigest() if chosen else '',
                 'status':'unique-masked-binary-counterpart' if unique else ('ambiguous' if matches else 'unresolved-modified-or-unmapped'),
                 'confidence':'High' if unique and (chosen[2] or chosen[3] or vv==v) and len(data)>=16 else 'Medium' if unique else 'Unknown',
                 'byte_envelope_length':len(data),'fixed_byte_count':sum(bool(x) for x in mask),
                 'source10_interval_anchor':chosen[2] if chosen else False,'relocation_target_anchor':chosen[3] if chosen else False,
                 'internal_callee_source10_anchors':chosen[4] if chosen else 0,
                 'to_has_promoted_dossier':(vv,chosen[0],chosen[1]) in bykey if chosen else False,
                 'all_matches':' | '.join(address(ss,aa) for ss,aa,*_ in matches),
                 'semantic_equivalence':'not claimed','evidence':'full masked byte envelope + reachable instruction layout + import-symbol sequence; masked data/far-call addresses do not prove source semantics'}
            relations.append(rel)
    # Build an exact site ledger: reassign existing sites and add newly reachable
    # sites once, rather than adding per-dossier counts to the contaminated v5 sum.
    graph=[];indirect=[]
    v5graph=readcsv(args.v5_output/'win16_static_direct_callgraph_v5.csv')
    v5by={}
    for r in v5graph:
        old=next((q for q in olds[r['version']] if q['function']==r['caller']),None)
        if old:v5by[(r['version'],old['seg'],number(r['call_site_offset']))]=r
    for v,b in bins.items():
        owned={}
        for r in olds[v]:
            for p in r['reach']:
                x=r['ins'][p]
                if x['bytes']!=b.segments[r['seg']]['bytes'][p:p+len(x['bytes'])]:raise ValueError('v5 assembly differs from binary')
                if x['mn'] in {'call','lcall'}:owned[(r['seg'],p)]=(r['function'],r['source10'],x)
        for d in [q for q in dossiers if q['version']==v]:
            s=d['segment_ordinal'];a=number(d['start_offset']);end=number(d['end_offset_exclusive'])
            for key in list(owned):
                if key[0]==s and a<=key[1]<end:del owned[key]
            for p,x in d['_ins'].items():
                if x['mn'] in {'call','lcall'}:owned[(s,p)]=(d['function'],'',x)
        for (s,p),(caller,source,x) in sorted(owned.items()):
            row={'version':v,'source_segment':s,'source_selector':SELECTORS[s],'call_site_offset':hex(p),'call_site_file_offset':hex(b.segments[s]['file_offset']+p),
                 'caller':caller,'caller_source10':source,'instruction_bytes':x['bytes'].hex(), 'target_selector':'','target_offset':'','callee':'',
                 'target_exact_start':False,'target_containing_interval':'','fixup_provenance':'','import_symbol':''}
            if x['op'].startswith('*'):
                row.update(call_kind='far-indirect' if x['mn']=='lcall' else 'near-indirect',operand=x['op']);indirect.append(row);continue
            if x['mn']=='call':ts=s;to=target(x['op']);row['call_kind']='near-direct'
            else:
                f=b.fixups.get((s,p))
                if not f:raise ValueError(f'Unresolved direct far call {v} {s}:{p:x}')
                row['fixup_provenance']='';row['import_symbol']=f['import_symbol']
                row.update({k:f[k] for k in ('record_index','record_file_offset','record_bytes','source_type','flags','chain_index','source_fixup_offset','next_chain_offset','additive')})
                row['resolution_confidence']='High binary fixup target; runtime path not proven'
                row['call_kind']='far-import' if f['import_symbol'] else 'far-internal'
                ts=f['target_segment'];to=number(f['target_offset']) if f['target_offset'] else None
                if f['import_symbol']:row['callee']=f['import_symbol']
            if ts in SELECTORS and to is not None:
                row['target_selector']=SELECTORS[ts];row['target_offset']=hex(to)
                dd=bykey.get((v,ts,to));exact=next((q for q in olds[v] if q['seg']==ts and q['start']==to),None)
                parent=next((q for q in olds[v] if q['seg']==ts and q['start']<=to<q['end']),None)
                row['callee']=dd['function'] if dd else exact['function'] if exact else address(ts,to)
                row['target_exact_start']=bool(dd or exact);row['target_containing_interval']=parent['function'] if parent else ''
            old=v5by.get((v,s,p));row['v5_caller']=old['caller'] if old else '';row['change']='newly-reachable' if not old else 'owner-reassigned' if old['caller']!=caller else 'retained'
            graph.append(row)
    for d in dossiers:
        d['callees']=[r for r in graph if r['version']==d['version'] and r['caller']==d['function']]
        d['callers']=[r for r in graph if r['version']==d['version'] and r['target_selector']==d['selector'] and r['target_offset']==d['start_offset']]
        d['indirect_calls']=[r for r in indirect if r['version']==d['version'] and r['caller']==d['function']]
        d['cross_version_relations']=[r for r in relations if r['from_version']==d['version'] and r['from_entry']==d['entry']]
        # Structural wrappers are distinguished from compiler provenance. Lack of
        # writes is never sufficient to claim a compiler-generated thunk.
        ii=list(d['_ins'].values());calls=d['callees'];branches=d['branch_sites']
        writes=[x for x in ii if x['mn'].startswith(('mov','add','sub','inc','dec','or','and','xor','shl','shr','sar','neg','not','xchg')) and ('0x' in x['op'].split(',')[-1] or '(' in x['op'].split(',')[-1])]
        if len(ii)<=12 and calls and not writes and not branches:
            d['classification']='call-wrapper';d['classification_status']='Confirmed structural';d['classification_reason']='Closed short routine forwards calls; compiler/MFC authorship is unproved'
        elif d['segment_ordinal']==2:
            d['classification']='runtime-or-MFC-wrapper-candidate';d['classification_status']='Inferred';d['classification_reason']='Segment 1008 routine brackets far call with near calls; no compiler/MFC symbol provenance'
        else:
            d['classification']='application-logic-candidate';d['classification_status']='Inferred';d['classification_reason']='Closed routine with control/data work in application segments 1010/1018; exact Nitemare gameplay purpose remains Unknown'
        d['compiler_or_mfc_origin']='Unknown; not established by prologue, selector, or resemblance alone'
        del d['_ins']
    # Structural identity groups are not canonical semantic/source-function IDs.
    parent={}
    def root(k):
        parent.setdefault(k,k)
        if parent[k]!=k:parent[k]=root(parent[k])
        return parent[k]
    for d in dossiers:root((d['version'],d['entry']))
    for r in relations:
        if r['confidence']!='High' or not r['to_entry']:continue
        a=root((r['from_version'],r['from_entry']));b=root((r['to_version'],r['to_entry']))
        parent[max(a,b)]=min(a,b)
    groups=defaultdict(list)
    for k in sorted(parent):groups[root(k)].append(k)
    families=[]
    for i,members in enumerate(sorted(groups.values()),1):
        row={'structural_family':f'WIN16-HIGH-V6-{i:03d}','identity_scope':'binary structural relation only; source semantics unproved'}
        for v in VERSIONS:
            row['win16_'+v]=' | '.join(a for vv,a in members if vv==v)
        row['promoted_members']=sum((v,a) in {(d['version'],d['entry']) for d in dossiers} for v,a in members)
        row['multiple_entries_same_build']=any(sum(vv==v for vv,a in members)>1 for v in VERSIONS)
        families.append(row)
    writecsv(out/'structural_families.csv',families)
    summary={'schema_version':6,'binary_hashes':HASHES,'input_evidence_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.v5_output.glob('*.csv')) if p.name in {'win16_hidden_entry_candidates_aggregated_v5.csv','win16_ne_fixup_sites_cfg_refined_v5.csv','win16_static_direct_callgraph_v5.csv'} or (p.name.startswith('win16_') and p.name.endswith('machine_functions_v4.csv')) or p.name=='win16_10_machine_functions_cfg_v5.csv'},'high_only':True,'promotions_by_version':dict(Counter(d['version'] for d in dossiers)),
             'structural_families':len(families),'families_with_multiple_entries_same_build':sum(f['multiple_entries_same_build'] for f in families),'high_candidates_audited':len(audit),'promoted':len(dossiers),'deferred':sum(r['status']=='deferred' for r in audit),
             'medium_or_medium_high_promoted':0,'relations_by_status':dict(Counter(r['status'] for r in relations)),
             'classifications':dict(Counter(d['classification'] for d in dossiers)),
             'callgraph':[],'historical_counts_note':'v4/v5 counts are retained as historical artifacts; v6 is a High-only extension, not semantic completeness'}
    for v,b in bins.items():
        g=[r for r in graph if r['version']==v];ig=[r for r in indirect if r['version']==v]
        summary['callgraph'].append({'version':v,'ne_records':b.record_count,'ne_expanded_sites':b.site_count,
            'near':sum(r['call_kind']=='near-direct' for r in g),'far_internal':sum(r['call_kind']=='far-internal' for r in g),
            'far_import':sum(r['call_kind']=='far-import' for r in g),'direct_total':len(g),'indirect':len(ig),
            'new_direct_sites':sum(r['change']=='newly-reachable' for r in g),'reassigned_direct_sites':sum(r['change']=='owner-reassigned' for r in g),
            'indexed_intervals_v5':len(olds[v]),'new_machine_dossiers':sum(d['version']==v for d in dossiers)})
    writecsv(out/'dossier_index.csv',[{k:d[k] for k in ('version','entry','end_offset_exclusive','file_offset','file_end_exclusive','body_sha256','entry_confidence','boundary_confidence','classification','classification_status','instruction_count','semantic_status')} for d in dossiers]);writecsv(out/'promotion_audit.csv',audit);writecsv(out/'cross_version_relations.csv',relations)
    writecsv(out/'callgraph.csv',graph);writecsv(out/'indirect_calls.csv',indirect)
    with open(out/'machine_dossiers.jsonl','w') as f:
        for d in dossiers:f.write(json.dumps(d,sort_keys=True)+'\n')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
