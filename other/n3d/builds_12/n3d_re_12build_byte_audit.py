#!/usr/bin/env python3
"""RE MAX: static, read-only byte audit of 7 DOS and 5 Windows Nitemare 3D builds.

Only reads original EXE files. Writes evidence CSV/JSON files (NEVER copies EXE bytes).
The names/paths below are local examples; override via --dos-dir and --win-dir.
Exact DOS CALL inventory: five-byte FAR CALL opcode 0x9A whose segment word has
an original EXEPACK relocation. This is conservative, not a full CFG/XREF audit.
No original program is executed. No runtime chronology is claimed.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import struct
from collections import Counter
from pathlib import Path

DOS_INPUTS = {
    "1.0": "N3D-E-10.EXE", "1.1": "N3D-11.exe", "1.2": "N3D-12(1).exe",
    "1.5": "N3D-15(2).exe", "1.7": "N3D-E-17.EXE",
    "1.9": "N3D-E-19.EXE", "2.0": "N3D-E-20.EXE",
}
WIN_INPUTS = {
    "1.0": "NITE3W -10.EXE", "1.3": "NITE3W - 13.EXE",
    "1.6": "NITE3W - 16.EXE", "1.8": "NITE3W - 18.EXE",
    "1.10": "nite3w.exe",
}
DOS_UNPACK_SHA = {
    "1.0": "113ea529e4247a5991f9dde2bd49e04b61f5714a8ea838d027014cac261e004a",
    "1.1": "c1d429fda9ffc1b2086db4bdfa51927254cd6d2fdcbc27943acf2868aba1e823",
    "1.2": "16aaddd455bbe98d76f4d566be4e6533fd049c24e08f6f63f1f9776f5e4957c6",
    "1.5": "4990b06e82da3cc8fbd304b49243c8e20c1c116ed867312d13fe39c4bf12e2b2",
    "1.7": "df85d457e752860dc8fc8c39c4c36ba1c62f03b0e704f1365ee618d8ed8447ff",
    "1.9": "e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e",
    "2.0": "e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297",
}
WIN_RAW_SHA = {
    "1.0": "6476e259a3a763e2985f22ea6655929e5b313f63ca4bcb976f98b6d50b72140c",
    "1.3": "926c0001944b9822cdae10b35c92c2d6cd3772bc774c4c88fb17df7465d1f156",
    "1.6": "5851849bacd8b03e93444d8a8f34d51c23fecddc73d6b8df7f016885c3b9d418",
    "1.8": "144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22",
    "1.10": "12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481",
}
# Anchor addresses for Win16 v1.3+ from static disassembly and prior audit.
WIN_ANCHORS = {
    "1.3": {"read_time":0xD4A4,"slow_clock":0xD4E8,"frame_clock":0xD528,
            "render":0xD56A,"calibrate":0xD5AE,"slow_AI":0xD752,
            "plan":0xD7A4,"player_input":0x95E4,"shoot_gate":0xA86E,"contact_fire":0xBC40},
    "1.6": {"read_time":0xD618,"slow_clock":0xD65C,"frame_clock":0xD69C,
            "render":0xD6DE,"calibrate":0xD722,"slow_AI":0xD8C6,
            "plan":0xD918,"player_input":0x9758,"shoot_gate":0xA9E2,"contact_fire":0xBDB4},
    "1.8": {"read_time":0xD618,"slow_clock":0xD65C,"frame_clock":0xD69C,
            "render":0xD6DE,"calibrate":0xD722,"slow_AI":0xD8C6,
            "plan":0xD918,"player_input":0x9758,"shoot_gate":0xA9E2,"contact_fire":0xBDB4},
    "1.10":{"read_time":0xD6C6,"slow_clock":0xD70A,"frame_clock":0xD74A,
            "render":0xD78C,"calibrate":0xD7D0,"slow_AI":0xD974,
            "plan":0xD9C6,"player_input":0x9806,"shoot_gate":0xAA90,"contact_fire":0xBE62},
}
# v1.0 only entries for which byte-level evidence is available independently.
WIN10_PROVEN = {"read_time":0xD498,"slow_clock":0xD4DC,"frame_clock":0xD51C,
                "render":0xD55E,"calibrate":0xD5A2,"player_input":0x9608,
                "shoot_gate":0xA88E,"contact_fire":0xBC34}

def sha(bs): return hashlib.sha256(bs).hexdigest()
def u16(bs,i): return struct.unpack_from('<H',bs,i)[0]
def putcsv(path,rows,fields):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def parse_exepack_reloc(data,begin,end,image_len):
    matches=[]
    for pos in range(begin,end-31):
        q=pos; reloc=[];counts=[];valid=True
        for sec in range(16):
            if q+2>end:valid=False;break
            cnt=u16(data,q);q+=2
            if q+cnt*2>end:valid=False;break
            addresses=[(sec<<16)+u16(data,q+i*2) for i in range(cnt)]
            if any(a+1>=image_len for a in addresses):valid=False;break
            reloc.extend(addresses);counts.append(cnt);q+=cnt*2
        if valid and q==end and len(counts)==16:
            matches.append((pos,reloc,counts))
    if len(matches)!=1:raise ValueError(f'EXEPACK reloc table ambiguous ({len(matches)} candidates)')
    return matches[0]

def unpack_dos(path):
    src=path.read_bytes()
    if src[:2]!=b'MZ' or len(src)<1024:raise ValueError(f'not DOS MZ: {path}')
    header_size=u16(src,8)*16
    pack_pos=header_size+u16(src,22)*16
    if pack_pos+16>len(src):raise ValueError('EXEPACK entry outside file')
    origin_ip,origin_cs,_,packed_length,_,_,len_paras,signature=struct.unpack_from('<8H',src,pack_pos)
    if signature!=0x4252 or pack_pos+packed_length!=len(src):raise ValueError('not supported RB EXEPACK')
    dest_bytes=len_paras*16
    source_len=pack_pos-header_size
    if not 0<source_len<dest_bytes<1024*1024:raise ValueError('bad EXEPACK size')
    out=bytearray(dest_bytes);out[:source_len]=src[header_size:pack_pos]
    r=source_len;w=dest_bytes
    while r>0 and out[r-1]==255:r-=1
    ncommands=0
    while True:
        if r<3:raise ValueError('EXEPACK command underflow')
        opcode=out[r-1];r-=1
        qty=(out[r-1]<<8)|out[r-2];r-=2
        typ=opcode&0xfe
        if typ==0xb0:
            if r<1 or qty>w:raise ValueError('fill underflow')
            r-=1;out[w-qty:w]=bytes([out[r]])*qty;w-=qty
        elif typ==0xb2:
            if qty>min(r,w):raise ValueError('copy underflow')
            for _ in range(qty):r-=1;w-=1;out[w]=out[r]
        else:raise ValueError(f'invalid EXEPACK opcode {opcode:02x}')
        ncommands+=1
        if ncommands>100000:raise ValueError('too many commands')
        if opcode&1:break
    if r!=w:raise ValueError('decompressed prefix mismatch')
    rel_start,rels,counts=parse_exepack_reloc(src,pack_pos+16,len(src),dest_bytes)
    return {'raw':src,'image':bytes(out),'rels':rels,'rel_counts':counts,
            'unpacked_sha':sha(out),'entry_cs':origin_cs,'entry_ip':origin_ip,
            'packed_start':pack_pos,'reloc_start':rel_start,'ncommands':ncommands}

def extract_calls(bs,relocs):
    calls=[]
    for r in relocs:
        if r>=3 and bs[r-3]==0x9a:
            off=u16(bs,r-2);seg=u16(bs,r)
            calls.append({'caller_offset':r-3,'callee_offset':off+16*seg,
                          'target_segment':seg,'target_ip':off,'reloc_at':r})
    assert len(calls)==len(set(c['caller_offset'] for c in calls))
    if any(c['callee_offset']>=len(bs) for c in calls):raise ValueError('out-of-image direct FAR target')
    return calls

def find_all(bs,needle):
    at=0;out=[]
    while True:
        at=bs.find(needle,at)
        if at<0:return out
        out.append(at);at+=1

def parse_damage(bs):
    starts=find_all(bs,b'\xc8\x02\x00\x00\x57\x56')
    candidates=[]
    for p in starts:
        body=bs[p:p+170]
        old=(body[6:8]==b'\x80\x3e' and body[10:14]==b'\x00\x75\x74\x83' and
             body[14]==0x3e and body[17:20]==b'\x02\x74\x6d')
        new=(body[6:12]==b'\x8b\x7e\x0a\x8b\x76\x06' and
             b'\x0a\xc0\x74\x06\xc7\x06' in body[:60])
        if not old and not new:continue
        ep=body.find(b'\x5e\x5f\xc9\xcb')
        if ep<0:continue
        body=body[:ep+4]
        producer_idx=body.find(b'\xff\x76\x0c\x57\xff\x76\x08\x56\x9a')
        if producer_idx<0:continue
        producer_call=producer_idx+8
        if body[-14:-12]!=b'\x6a'+body[-13:-12] or body[-12]!=0x9a:continue
        pr_off=u16(body,producer_call+1);pr_seg=u16(body,producer_call+3)
        dispatch_off=u16(body,len(body)-11);dispatch_seg=u16(body,len(body)-9)
        hp_read=body.find(b'\x88\x46\xff\xa0')
        if not new:
            if hp_read<0:continue
            hp=u16(body,hp_read+4)
            if body[6:8]!=b'\x80\x3e' or body[13:15]!=b'\x83\x3e':continue
            pro=u16(body,8);state=u16(body,15)
            if body[11]!=0x75 or body[12]!=0x74:continue
            order='protection_state_before_damage_producer'
        else:
            # Cmp-byte-protection (80 3E) and cmp-word-terminal (83 3E) appear AFTER call.
            q=body.find(b'\x80\x3e',producer_call+5)
            if q<0 or body[q+5] not in (0x75,):continue
            state_idx=body.find(b'\x83\x3e',q+5)
            if state_idx<0 or body[state_idx+4]!=2:continue
            pro=u16(body,q+2);state=u16(body,state_idx+2)
            hp_idx=body.find(b'\xa0',state_idx+5)
            if hp_idx<0 or body[hp_idx+3:hp_idx+6]!=b'\x38\x46\xff':continue
            hp=u16(body,hp_idx+1)
            order='damage_producer_before_protection_state'
        candidates.append({
            'damage_wrapper_offset':p,'damage_wrapper_bytes':len(body),'producer_callsite':p+producer_call,
            'damage_producer_target':pr_seg*16+pr_off,'protection_ds':pro,
            'game_state_ds':state,'hp_ds':hp,'hp_dispatch_index':body[-13],
            'hp_dispatcher_target':dispatch_seg*16+dispatch_off,
            'protection_vs_producer_order':order,
            'timer3_before_protection':new and b'\xc7\x06\x7a\x41\x03\x00' in body,
        })
    if len(candidates)!=1:raise ValueError(f'cannot uniquely identify damage wrapper; found={len(candidates)}')
    return candidates[0]

def analyze_dispatcher(bs,d):
    s=d['hp_dispatcher_target']
    prefix=bs[s:s+160]
    if prefix[:4]!=b'\xc8\x24\x00\x00':raise ValueError('dispatcher ENTER 24 missing')
    idx=prefix.find(b'\x3d')
    if idx<0 or prefix[idx+3:idx+5]!=b'\x0f\x87':raise ValueError('unknown dispatcher CMP/JA layout')
    max_case=u16(prefix,idx+1)
    marker=prefix.find(b'\x2e\xff\xa7')
    if marker<0:raise ValueError('near computed CS JMP missing')
    table_off=u16(prefix,marker+3)
    # Damage wrapper's FAR selector is the segment containing dispatcher & CS-relative table.
    wrapper=d['damage_wrapper_offset'];w=bs[wrapper:wrapper+170]
    ep=w.find(b'\x5e\x5f\xc9\xcb')+4
    dispatch_seg=u16(w,ep-9)
    table_linear=dispatch_seg*16+table_off
    cases=[u16(bs,table_linear+i*2) for i in range(max_case+1)]
    index=d['hp_dispatch_index']
    if index>max_case:raise ValueError('HP dispatch index out of range')
    code=bs[dispatch_seg*16+cases[index]:][:14]
    hp=d['hp_ds']
    expected=b'\xa0'+struct.pack('<H',hp)+b'\x2c\x64\x1a\xc9\x22\xc1\x04\x64\xa2'+struct.pack('<H',hp)
    assert len(expected)==14
    if code!=expected:
        raise ValueError('HP handler missing canonical unsigned min(HP,100) code')
    d.update({'dispatcher_code_slot_count':max_case+1,
              'dispatcher_jump_table_linear':table_linear,
              'hp_handler_linear':dispatch_seg*16+cases[index],
              'hp_cap_opcode_validated':True,
              'dispatcher_uses_pending_flag':bs[s+6:s+8]==b'\x80\x3e',
              'dispatcher_segment':dispatch_seg,
              'dispatcher_jump_table':cases})
    return d

def analyze_rng(bs,calls):
    points=find_all(bs,b'\xb8\xfd\x43\xba\x03\x00\x52\x50')
    if len(points)!=1:raise ValueError(f'RNG multiply-constant site count={len(points)}')
    p=points[0];f=bs[p:p+40]
    if (f[8:10]!=b'\xff\x36' or f[12:14]!=b'\xff\x36' or
        f[16]!=0x9a or f[21:28]!=b'\x05\xc3\x9e\x83\xd2\x26\xa3' or
        f[34:40]!=b'\x8b\xc2\x80\xe4\x7f\xcb'):
        raise ValueError('LCG 32-bit update shape mismatch')
    low=u16(f,14);high=u16(f,10)
    if high!=low+2 or u16(f,28)!=low or u16(f,32)!=high:
        raise ValueError('RNG state reads/writes inconsistent')
    hit=[c for c in calls if c['callee_offset']==p and bs[c['caller_offset']+5]==0xcb]
    if len(hit)!=1:raise ValueError(f'LCG wrapper count={len(hit)}')
    w=hit[0]['caller_offset']
    sites=sorted(c['caller_offset'] for c in calls if c['callee_offset']==w)
    return {'rng_lcg_offset':p,'rng_wrapper_offset':w,'rng_state_ds_low':low,
            'rng_state_ds_high':high,'direct_rng_callsite_count':len(sites),
            'lcg_mul_constant':'0x000343FD','lcg_add_constant':'0x00269EC3',
            'rng_return':'(new_state >> 16) & 0x7FFF','rng_calls':sites}

def parse_ne(path):
    data=path.read_bytes();mz_off=struct.unpack_from('<I',data,0x3c)[0]
    if data[:2]!=b'MZ' or data[mz_off:mz_off+2]!=b'NE':raise ValueError('expected Win16 NE EXE')
    N=mz_off;n=u16(data,N+0x1c);shift=u16(data,N+0x32);segtable=u16(data,N+0x22)
    if not (n==10 and shift in range(1,10)):raise ValueError('unexpected NE segment table')
    modref_count=u16(data,N+0x1e)
    modref_base=N+u16(data,N+0x28)
    impname_base=N+u16(data,N+0x2a)
    modules=[]
    for module_idx in range(modref_count):
        relname=u16(data,modref_base+module_idx*2)
        namepos=impname_base+relname
        namelen=data[namepos]
        modules.append(data[namepos+1:namepos+1+namelen].decode('latin1'))
    s=[]; import_calls=[]
    for i in range(n):
        block=u16(data,N+segtable+i*8);length=u16(data,N+segtable+i*8+2)
        flags=u16(data,N+segtable+i*8+4);alloc=u16(data,N+segtable+i*8+6)
        off=block<<shift
        length=length or (0x10000 if off else 0)
        nfixups=0
        if off:
            if off+length>len(data):raise ValueError('NE segment out of range')
            if flags&0x100:
                fpos=off+length;nfixups=u16(data,fpos)
                if fpos+2+8*nfixups>len(data):raise ValueError('NE fixup list out of range')
                for fixup_i in range(nfixups):
                    q=fpos+2+8*fixup_i
                    source_type, relocation_type, source_ip, target_module, target_ord=struct.unpack_from('<BBHHH',data,q)
                    # Fixup type 1 = imported by ordinal, not an internal NE code segment!
                    if source_type==3 and relocation_type==1 and source_ip>=1 and data[off+source_ip-1]==0x9a:
                        if not 1<=target_module<=len(modules):raise ValueError('bad NE module reference')
                        import_calls.append({'caller_segment':i+1,'caller_ip':source_ip-1,
                          'import_module_index':target_module,'import_module':modules[target_module-1],
                          'import_ordinal':target_ord,'ne_fixup_at':q})
        seg=data[off:off+length] if off else b''
        s.append({'segment':i+1,'raw_file_offset':off,'bytes':length,
                  'flags':f'{flags:04X}','min_alloc_bytes':alloc or 65536,
                  'fixups':nfixups,'sha256':sha(seg) if off else '', 'data':seg})
    matches=re.findall(rb'Nitemare-3D for Windows V(\d+\.\d+)',data)
    if len(matches)!=1:raise ValueError(f'internal Win16 version strings={matches}')
    return {'raw':data,'segments':s,'modules':modules,'import_calls':import_calls,
            'version_string':matches[0].decode('ascii'),'sha':sha(data)}

def write_audit(dospaths,winpaths,out):
    out.mkdir(parents=True,exist_ok=True)
    buildrows=[];callrows=[];rngrows=[];damage=[];tables=[];nerows=[];anchorrows=[];wincalls=[];json_out={}
    for version,path in dospaths.items():
        a=unpack_dos(path);img=a['image'];dg=analyze_dispatcher(img,parse_damage(img))
        rng=analyze_rng(img,extract_calls(img,a['rels']))
        calls=extract_calls(img,a['rels'])
        if a['unpacked_sha']!=DOS_UNPACK_SHA[version]:raise ValueError(f'fingerprint changed DOS {version}')
        b={'platform':'DOS','version':version,'original_filename':path.name,
           'raw_bytes':len(a['raw']),'sha256_raw':sha(a['raw']),
           'code_image_bytes':len(img),'sha256_code_image':a['unpacked_sha'],
           'image_hash_domain':'EXEPACK unpacked MZ load image',
           'relocations':len(a['rels']),'direct_far_calls':len(calls),
           'distinct_far_targets':len({c['callee_offset'] for c in calls}),
           'rng_direct_calls':rng['direct_rng_callsite_count']}
        buildrows.append(b)
        for c in calls:
            callrows.append({'DOS_version':version,**{k:f'0x{v:05X}' if isinstance(v,int) else v for k,v in c.items()}})
        for s in rng.pop('rng_calls'):
            rngrows.append({'DOS_version':version,'rng_callsite_in_unpacked_image':f'0x{s:05X}',
                            'RNG_wrapper_unpacked_image':f"0x{rng['rng_wrapper_offset']:05X}"})
        dg['version']=version
        for i,offs in enumerate(dg.pop('dispatcher_jump_table')):
            tables.append({'DOS_version':version,'slot':i,'handler_near_ip':f'0x{offs:04X}',
                           'handler_load_image_linear':f"0x{dg['dispatcher_segment']*16+offs:05X}"})
        damage.append({k:(f'0x{v:05X}' if isinstance(v,int) and k not in ('damage_wrapper_bytes','hp_dispatch_index','dispatcher_code_slot_count','dispatcher_segment','hp_cap_opcode_validated','dispatcher_uses_pending_flag','timer3_before_protection') else v) for k,v in dg.items()})
        json_out[f'DOS_{version}']={'build':b,'damage':dg,'rng':rng}
    for version,path in winpaths.items():
        a=parse_ne(path)
        if a['sha']!=WIN_RAW_SHA[version]:raise ValueError(f'fingerprint changed Win16 {version}')
        if a['version_string']!=version:raise ValueError(f'internal Win16 version mismatch {version}')
        fixups=sum(x['fixups'] for x in a['segments']);seg3=a['segments'][2]['data']
        buildrows.append({'platform':'Win16','version':version,'original_filename':path.name,
           'raw_bytes':len(a['raw']),'sha256_raw':a['sha'],
           'code_image_bytes':'','sha256_code_image':'','image_hash_domain':'entire raw NE',
           'relocations':fixups,'direct_far_calls':len(a['import_calls']),
           'distinct_far_targets':len({(c['import_module'],c['import_ordinal']) for c in a['import_calls']}),
           'rng_direct_calls':''})
        ordinal_labels={('MMSYSTEM',201):'midiOutGetNumDevs',
           ('MMSYSTEM',202):'midiOutGetDevCaps',
           ('MMSYSTEM',211):'midiOutGetVolume',
           ('MMSYSTEM',415):'waveOutGetVolume'}
        for c in a['import_calls']:
            wincalls.append({'Win16_version':version,'caller_segment':c['caller_segment'],
                'caller_ip':f"0x{c['caller_ip']:04X}",'import_module':c['import_module'],
                'import_ordinal':c['import_ordinal'],
                'api_name_external_reference':ordinal_labels.get((c['import_module'],c['import_ordinal']),'UNKNOWN'),
                'fixup_file_offset':f"0x{c['ne_fixup_at']:05X}"})
        for s in a['segments']:
            nerows.append({'Win16_version':version,**{k:v for k,v in s.items() if k!='data'}})
        amap=WIN10_PROVEN if version=='1.0' else WIN_ANCHORS[version]
        for name,at in amap.items():
            anchorrows.append({'Win16_version':version,'behavior':name,'NE_segment':3,
                               'offset':f'0x{at:04X}', 'first_16_bytes':seg3[at:at+16].hex(' ')})
        json_out[f'WIN16_{version}']={'size':len(a['raw']),'sha256':a['sha'],
             'loaded_segments':sum(bool(s['bytes']) for s in a['segments']),
             'relocation_records':fixups, 'far_import_calls':len(a['import_calls'])}
    # Local byte equivalence for three timing primitives in Win16 v1.0 & 1.3.
    w10=parse_ne(winpaths['1.0'])['segments'][2]['data'];w13=parse_ne(winpaths['1.3'])['segments'][2]['data']
    windows=[('read_time',0xD498,0xD4A4,26),('slow_clock',0xD4DC,0xD4E8,63),
             ('frame_clock',0xD51C,0xD528,65)]
    eq=[]
    for name,a,b,n in windows:
        same=(w10[a:a+n]==w13[b:b+n]);eq.append({'behavior':name,'Win1_0_offset':f'0x{a:04X}',
                 'Win1_3_offset':f'0x{b:04X}','compared_bytes':n,'byte_identical':same})
        if not same:raise ValueError(f'expected Win16 early timing identity failed: {name}')
    json_out['Win10_to_Win13_exact_timings']=eq
    json_out['Win10_calibration_entry']=w10[0xd5a2:0xd5a2+22].hex(' ')
    json_out['Win13_calibration_entry']=w13[0xd5ae:0xd5ae+30].hex(' ')
    putcsv(out/'N3D_12build_identities.csv',buildrows,list(buildrows[0]))
    putcsv(out/'N3D_DOS_reloc_anchored_FAR_CALLs.csv',callrows,list(callrows[0]))
    putcsv(out/'N3D_DOS_rng_22_calls_each.csv',rngrows,list(rngrows[0]))
    putcsv(out/'N3D_DOS_damage_dispatch_by_version.csv',damage,list(damage[0]))
    putcsv(out/'N3D_DOS_dispatch_jump_tables.csv',tables,list(tables[0]))
    putcsv(out/'N3D_Win16_NE_segments.csv',nerows,list(nerows[0]))
    putcsv(out/'N3D_Win16_reloc_anchored_import_CALLs.csv',wincalls,list(wincalls[0]))
    putcsv(out/'N3D_Win16_NE3_anchors.csv',anchorrows,list(anchorrows[0]))
    putcsv(out/'N3D_Win16_10_vs_13_exact_windows.csv',eq,list(eq[0]))
    # Global import API set progression, not just a file-size delta.
    stages=['1.0','1.3','1.6','1.8','1.10']
    newapis=[];earlier=set()
    for stage in stages:
        stagecalls=[x for x in wincalls if x['Win16_version']==stage]
        now={(x['import_module'],int(x['import_ordinal'])) for x in stagecalls}
        for module,ordinal in sorted(now-earlier):
            relevant=[x for x in stagecalls if x['import_module']==module and int(x['import_ordinal'])==ordinal]
            newapis.append({'first_observed_in_build':stage,'module':module,'ordinal_decimal':ordinal,
              'api_name_external_reference':relevant[0]['api_name_external_reference'],
              'direct_far_call_sites':'; '.join(f"{x['caller_segment']}:{x['caller_ip']}" for x in relevant)})
        earlier=now
    putcsv(out/'N3D_Win16_import_APIs_first_observed.csv',newapis,list(newapis[0]))
    json_out['Win16_import_API_first_observed']=newapis
    (out/'N3D_12build_core_evidence.json').write_text(json.dumps(json_out,indent=2,ensure_ascii=False),encoding='utf-8')

    return buildrows,json_out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path('/mnt/data'),help='Folder with recent DOS inputs')
    p.add_argument('--dos-compare-dir',type=Path,default=Path('/mnt/data/compare'))
    p.add_argument('--win-dir',type=Path,default=Path('/mnt/data/win'))
    p.add_argument('--output-dir',type=Path,default=Path('/mnt/data/static_byte_evidence'))
    a=p.parse_args()
    dos={v:(a.root if v in ('1.1','1.2','1.5') else a.dos_compare_dir)/f for v,f in DOS_INPUTS.items()}
    win={v:a.win_dir/f for v,f in WIN_INPUTS.items()}
    absent=[str(x) for x in [*dos.values(),*win.values()] if not x.exists()]
    if absent:raise SystemExit('Missing original input files: '+', '.join(absent))
    results,_=write_audit(dos,win,a.output_dir)
    for row in results:
        print(f"{row['platform']:5s} {row['version']:4s} {row['raw_bytes']:>7} B | reloc {row['relocations']:>4} | FAR CALLs {str(row['direct_far_calls']):>4} | rng {str(row['rng_direct_calls']):>2}")
    print('EVIDENCE ONLY — static byte scan, not 1:1 behavioral proof')
    print('Results:',a.output_dir)
if __name__=='__main__':main()
