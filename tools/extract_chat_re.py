#!/usr/bin/env python3
"""Extract Nitemare 3-D RE evidence from a ChatGPT data export."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any

KEYWORDS = ('nitemare3d','nitemare 3d','nitemare 3-d','nite3w','nite3d','n3d')
RE_TERMS = ('reverse','reverzn','ida','ghidra','disasm','decomp','offset','address','funkci','function','renderer','raycast','guard','object','weapon','collision','demo','bsf','user.sav','walls','map.','objects.','snd.dat','uif.dat','ending.fli','game.pal','hud','palette','automap','mfc','win16')

def hit(s, terms):
    t=s.casefold()
    return any(k in t for k in terms)

def msg_text(msg: dict[str, Any]) -> str:
    c=msg.get('content') or {}
    parts=c.get('parts') or []
    out=[]
    for p in parts:
        if isinstance(p,str): out.append(p)
        elif isinstance(p,dict) and isinstance(p.get('text'),str): out.append(p['text'])
    if not out and isinstance(c.get('text'),str): out.append(c['text'])
    return '\n'.join(out).strip()

def conversations(path: Path):
    data=json.loads(path.read_text(encoding='utf-8'))
    if isinstance(data,list): return [x for x in data if isinstance(x,dict)]
    if isinstance(data,dict) and isinstance(data.get('conversations'),list): return data['conversations']
    return [data] if isinstance(data,dict) else []

def messages(conv):
    rows=[]
    mp=conv.get('mapping')
    if isinstance(mp,dict):
        for order,node in enumerate(mp.values()):
            if not isinstance(node,dict) or not isinstance(node.get('message'),dict): continue
            m=node['message']; txt=msg_text(m)
            if not txt: continue
            role=((m.get('author') or {}).get('role') or 'unknown')
            ct=m.get('create_time'); stamp=float(ct) if isinstance(ct,(int,float)) else 0.0
            rows.append((stamp,order,role,txt))
        return [(r,t) for _,_,r,t in sorted(rows)]
    return []

def collect(path: Path, radius: int):
    found=[]
    for ci,conv in enumerate(conversations(path)):
        title=str(conv.get('title') or f'conversation-{ci}')
        ms=messages(conv)
        direct=[i for i,(_,t) in enumerate(ms) if hit(t,KEYWORDS)]
        title_hit=hit(title,KEYWORDS)
        if not direct and not title_hit: continue
        keep=set()
        seeds=direct or [i for i,(_,t) in enumerate(ms) if hit(t,RE_TERMS)]
        for i in seeds:
            keep.update(range(max(0,i-radius),min(len(ms),i+radius+1)))
        if title_hit or len(direct)>=2:
            keep.update(i for i,(_,t) in enumerate(ms) if hit(t,KEYWORDS) or hit(t,RE_TERMS))
        found.append((title,[(i,ms[i][0],ms[i][1]) for i in sorted(keep)]))
    return found

def render(records):
    out=['# Nitemare 3-D Chat Recovery Ledger','',
         '> Chat text is provenance, not proof. Validate addresses, layouts, algorithms and constants against executable/data evidence.','']
    for title,items in records:
        out += ['## '+title,'']
        for i,role,txt in items:
            out += [f'### message {i} — {role}','', '```text', txt, '```','']
    return '\n'.join(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('inputs',nargs='+',type=Path)
    ap.add_argument('-o','--output',type=Path,default=Path('chat_recovery_ledger.md'))
    ap.add_argument('--context',type=int,default=2)
    a=ap.parse_args(); rec=[]
    for p in a.inputs:
        if p.suffix.lower()=='.json': rec.extend(collect(p,max(0,a.context)))
        else:
            txt=p.read_text(encoding='utf-8',errors='replace')
            if hit(txt,KEYWORDS): rec.append((p.name,[(0,'unknown',txt)]))
    seen=set(); uniq=[]
    for title,items in rec:
        key=json.dumps([title,[(r,t) for _,r,t in items]],ensure_ascii=False)
        if key not in seen: seen.add(key); uniq.append((title,items))
    a.output.write_text(render(uniq),encoding='utf-8')
    print(f'Wrote {a.output} ({len(uniq)} conversations)')

if __name__=='__main__': main()
