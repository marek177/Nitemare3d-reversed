#!/usr/bin/env python3
"""RE MAX v0.58: original-byte-identified DOS/Win16 GUARD death/SFX contract.

Read-only original inputs; output is evidence metadata/decoded numeric records.
DOS offsets = unpacked unrelocated MZ load-image offsets, not runtime CS:IP.
Windows offsets = logical NE segment 3 offsets, not loaded selectors.
No game execution, no runtime parity claims, and no redistributed original bytes.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, struct
from pathlib import Path

PROFILES={
    'dos20':dict(size=171360,sha='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297',
       csbase=0x83D0,hit=0x5F74,score=0x84FE,death_sound=0x9CF2,state7_sound=0x9EB4,
       fatal_variant=0x9FB4,nonfatal_variant=0xA018),
    'win110':dict(size=230400,sha='12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481',
       csbase=0,hit=0x80F8,score=0x9F10,death_sound=0xB6A0,state7_sound=0xB862,
       fatal_variant=0xB94E,nonfatal_variant=0xB9B2),
    'winalt':dict(size=230224,sha='144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22',
       csbase=0,hit=0x8054,score=0x9E62,death_sound=0xB5F2,state7_sound=0xB7B4,
       fatal_variant=0xB8A0,nonfatal_variant=0xB904),
}
BODY_SIZES={'score':0x91,'death_sound':0xC2,'state7_sound':0xEC,
            'fatal_variant':0x64,'nonfatal_variant':0x64}
# Whitelist ONLY location-dependent encoded operands, WORD switch tables,
# and the one nonexecuted padding byte. Every other byte is compared.
SKIP={
    'score':set(range(0x1C,0x50)),
    'death_sound':set(range(0x1F,0x21))|set(range(0x22,0x52))|
                  set(range(0x7D,0x81))|set(range(0xAE,0xB2))|set(range(0xB8,0xBC)),
    'state7_sound':set(range(0x1F,0x21))|set(range(0x22,0x52))|
                   set(range(0x59,0x5D))|set(range(0x83,0x87))|
                   set(range(0xD8,0xDC))|set(range(0xE2,0xE6)),
    'fatal_variant':{0x1D,0x1E,0x30,0x31,0x32,0x33,0x54,0x55,0x63},
    'nonfatal_variant':{0x1D,0x1E,0x30,0x31,0x32,0x33,0x54,0x55,0x63},
}
# Independent expected snapshots of the decoded source tables. Build-specific
# raw offsets are deliberately not copied to these expected semantic maps.
EXPECT_SCORE=[25,75,50,100,250,150,200,100,100,0,150,150,200,-1000,1000,
              100,200,0,25,100,100,250,250,200,50] # classes 08..20
EXPECT_DEATH_SOUND=[35,8,7,36,4,19,14,'rng%3+11','rng%3+11',0,7,7,35,0,0,
                    70,70,0,74,2,2,9,70,70]  # classes 08..1F
EXPECT_STATE7_SOUND=[34,'rng%3+56','rng%3+56',59,20,21,16,'rng%2+54',
                     'rng%2+54',6,63,60,0,0,18,72,71,0,73,13,13,56,61,61]
EXPECTED_VALUES={'score':EXPECT_SCORE,'death_sound':EXPECT_DEATH_SOUND,'state7_sound':EXPECT_STATE7_SOUND}
assert len(EXPECT_SCORE)==25 and len(EXPECT_DEATH_SOUND)==24 and len(EXPECT_STATE7_SOUND)==24


def word(b:bytes,p:int)->int:return struct.unpack_from('<H',b,p)[0]
def signed16(x:int)->int:return x-65536 if x&0x8000 else x


def win_seg3(raw:bytes)->tuple[bytes,int]:
    if raw[:2]!=b'MZ':raise AssertionError('MZ header missing')
    ne=struct.unpack_from('<I',raw,0x3C)[0]
    if raw[ne:ne+2]!=b'NE':raise AssertionError('NE header missing')
    if word(raw,ne+0x1C)<3:raise AssertionError('NE fewer than 3 segments')
    table=ne+word(raw,ne+0x22)
    sh=word(raw,ne+0x32)
    off,ln=struct.unpack_from('<HH',raw,table+16)
    start=off<<sh;length=ln or 65536
    seg=raw[start:start+length]
    if len(seg)!=length:raise AssertionError('truncated NE segment 3')
    return seg,start


def require(c:bytes,where:int,signature:str,meaning:str)->dict:
    expected=bytes.fromhex(signature)
    actual=c[where:where+len(expected)]
    if expected!=actual:
        raise AssertionError(f'{meaning} at {where:05X}: wanted {expected.hex()} got {actual.hex()}')
    return dict(image_offset=f'{where:05X}',bytes=len(expected),meaning=meaning)


def decode_audio_case(c:bytes,target:int,sink:int)->tuple[int|str,str]:
    op=c[target]
    if target==sink:return 0,'default_zero_selector'
    if op==0xBE: return word(c,target+1),'fixed_selector'
    if op==0x9A:
        # CALL FAR RNG, MOV CX,div, CWD, IDIV CX, MOV SI,DX, ADD SI,const
        if c[target+5]!=0xB9 or c[target+8:target+14]!=bytes.fromhex('99 f7 f9 8b f2 83') or c[target+14]!=0xC6:
            raise AssertionError(f'unexpected SFX random subpath at {target:05X}')
        return f'rng%{word(c,target+6)}+{c[target+15]}','draw_rng_once_then_mod'
    raise AssertionError(f'unrecognized audio switch target {target:05X}, opcode {op:02X}')


def decode_profile(tag:str,path:Path)->tuple[dict,dict]:
    prof=PROFILES[tag];raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    if len(raw)!=prof['size'] or sha!=prof['sha']:
        raise AssertionError(f'{tag}: binary profile mismatch: size={len(raw)} sha256={sha}')
    if tag=='dos20':c=raw;seg_file_offset=None
    else:c,seg_file_offset=win_seg3(raw)
    records={};raw_bodies={}
    for key,size in BODY_SIZES.items():
        p=prof[key];body=c[p:p+size]
        if len(body)!=size:raise AssertionError(f'{tag}: {key} truncated')
        raw_bodies[key]=body
        if key=='score':
            require(c,p,'55 8b ec 33 c9 c4 5e 0a 2a e4 26 8a 47 06 2d 08 00 3d 18 00',f'{tag} score class 08..20 input range')
            require(c,p+0x19,'2e ff a7',f'{tag} 25-case score jump')
            table=p+0x1E;count=25;sink=p+0x8D
        elif key in ('death_sound','state7_sound'):
            require(c,p,'55 8b ec 56 33 f6 c4 5e 0a 2a e4 26 8a 47 06 2d 08 00 3d 17 00',f'{tag} {key} class 08..1F input range')
            require(c,p+0x1C,'2e ff a7',f'{tag} 24-case {key} jump')
            table=p+0x22;count=24;sink=p+(0xA3 if key=='death_sound' else 0xCD)
        else:
            # Distinct high-descriptor flag / variant rejection slot location
            require(c,p,'55 8b ec 57 56 c4 5e 06 26 80 7f 12 00',f'{tag} {key} early GUARD+12 check')
            require(c,p+0x25,'b8 07 00 5e 5f c9 cb',f'{tag} {key} fast return 7 without RNG')
            require(c,p+0x2F,'9a',f'{tag} {key} RNG entry')
            require(c,p+0x34,'b9 07 00 99 f7 f9 8b f2 3b f1 74 ef',f'{tag} {key} modulo7, mathematically dead cmp remainder==7')
            field_hi=0x59 if key=='fatal_variant' else 0x49
            field_slots=0x4B if key=='fatal_variant' else 0x3B
            require(c,p+0x1F,f'80 7f {field_hi:02x} 00',f'{tag} {key} nonzero high variant flag')
            require(c,p+0x58,f'38 6f {field_slots:02x} 74 d2',f'{tag} {key} retry when selected descriptor byte is zero')
            records[key]={'start':f'{p:05X}','size':size,'high_flag_offset':f'{field_hi:02X}',
                'rejection_base_byte_offset':f'{field_slots:02X}','rejection_stride':2,
                'fast_seven_requires':['GUARD+12==0','descriptor high_flag !=0'],
                'rng_remainder_set':[0,1,2,3,4,5,6],
                'last_relative_byte_nonexecuted_padding':f'{p+0x63:05X}',
                'effect':'invariant local selector, transitive resource effects not proven'}
            continue
        routes=[]
        for i in range(count):
            rawtarget=word(c,table+2*i)
            target=rawtarget+prof['csbase']
            if target<p or target>=p+size:
                raise AssertionError(f'{tag} {key}: target outside body class {i+8:02X}: {target:X}')
            if key=='score':
                if target==sink:
                    if c[target:target+4]!=bytes.fromhex('8b c1 c9 cb'):
                        raise AssertionError(f'{tag} invalid zero score epilogue')
                    value=0;kind='default_zero'
                elif c[target]==0xB9:
                    value=signed16(word(c,target+1));kind='constant_signed16'
                else:raise AssertionError(f'{tag} unusual score case at {target:05X}')
            else:value,kind=decode_audio_case(c,target,sink)
            if value!=EXPECTED_VALUES[key][i]:
                raise AssertionError(f'{tag} {key} class {i+8:02X} value={value} expected={EXPECTED_VALUES[key][i]}')
            routes.append(dict(class_hex=f'{i+8:02X}',relative_target=f'{target-p:03X}',
                               selected_value=value,behavior=kind))
        records[key]={'start':f'{p:05X}','size':size,'classes':routes,
                      'fallback_for_out_of_range':0,
                      'value_kind':'signed score points' if key=='score' else 'event selector (not proof of actual played audio)'}
    # Witness original hit order, with native per-build exact relative addresses.
    h=prof['hit']
    witness=[]
    witness.append(require(c,h,'c8 02 00 00 57 56',f'{tag} hit function entry'))
    witness.append(require(c,h+0x1C,'2a e4 89 46 fe 8e 46 08 26 8a 44 10 3b 46 fe',f'{tag} lethal threshold after damage scalar'))
    witness.append(require(c,h+0xFB,'26 c6 44 12 08',f'{tag} GUARD+12=8 before nonfatal variant'))
    damage_entry={'dos20':0x8590,'win110':0x9FA2,'winalt':0x9EF4}[tag]
    witness.append(require(c,damage_entry+0xA5,'33 f6 eb 57',f'{tag} damage class15 zeroes scalar after FAR callback'))
    # This is deliberate build-independent relative sequence; additional exact
    # targets of FAR calls are checked by decoding their operands below.
    # Instead of trusting speculative rel offsets, strict scans within hit:
    # count FAR targets to the known callee in the local decoded region.
    hit_blob=c[h:h+(0x20B if tag!='dos20' else 0x208)]
    targets={}
    for field in ('fatal_variant','death_sound','score','state7_sound','nonfatal_variant'):
        needle=prof[field].to_bytes(2,'little') if tag!='dos20' else (prof[field]-prof['csbase']).to_bytes(2,'little')
        matches=[]
        for i in range(len(hit_blob)-4):
            if hit_blob[i]==0x9A and hit_blob[i+1:i+3]==needle:
                if tag=='dos20':
                    if hit_blob[i+3:i+5]!=(0x83D).to_bytes(2,'little'):continue
                matches.append(h+i)
        expected=2 if field=='nonfatal_variant' else 1
        if len(matches)!=expected:
            raise AssertionError(f'{tag} {field} {len(matches)} direct callsite(s) != {expected}: {matches}')
        targets[field]=[f'{x:05X}' for x in matches]
    # All nonfatal calls follow GUARD+12=8 as visible direct path; except
    # when strategy==4, that handler bypasses both nonfatal selectors.
    # Observe immediate byte region from timer writer to first nonfatal call.
    first_nonfat=int(targets['nonfatal_variant'][0],16)
    if not h+0xFB < first_nonfat:
        raise AssertionError(f'{tag} nonfatal timer writer not before first variant call')
    if c[h+0xFB:h+0x100]!=bytes.fromhex('26 c6 44 12 08'):
        raise AssertionError(f'{tag} timer writer does not set GUARD+12 to 8')
    # Witness score signed-extension and 32-bit add on lethal (DS differs by platform).
    if tag=='dos20':
        witness += [require(c,h+0xAA,'99 01 06 82 41 11 16 84 41','fatal score 32bit signed addition'),
                    require(c,h+0x44,'83 3e 90 41 01 74 10','death sound conditional gate')]
    else:
        witness += [require(c,h+0xAB,'99 01 06 16 4c 11 16 18 4c','fatal score 32bit signed addition'),
                    require(c,h+0x44,'83 3e 26 4c 01 74 10','death sound conditional gate')]
    return {'original_sha256':sha,'seg3_file_offset':f'{seg_file_offset:05X}' if seg_file_offset is not None else None,
            'tables':records,'hit':{'entry':f'{h:05X}','direct_nested_calls':targets,
                      'extra_witnesses':witness,
                      'guaranteed_nonfatal_variant_rng_if_entered':True,
                      'guarantee_scope':'only direct hit nonfatal GUARD+12=8 paths; no callback reentry proof'}},raw_bodies


def audit(dos20:Path,win110:Path,winalt:Path)->dict:
    data={};body={}
    for key,path in [('dos20',dos20),('win110',win110),('winalt',winalt)]:
        data[key],body[key]=decode_profile(key,path)
    compare={}
    for field,length in BODY_SIZES.items():
        a,b,z=[body[k][field] for k in ('dos20','win110','winalt')]
        if len(a)!=length or len(b)!=length or len(z)!=length:raise AssertionError('bad body length')
        mismatches_ab={i for i,(x,y) in enumerate(zip(a,b)) if x!=y}
        mismatches_bz={i for i,(x,y) in enumerate(zip(b,z)) if x!=y}
        if not mismatches_ab<=SKIP[field] or not mismatches_bz<=SKIP[field]:
            raise AssertionError(f'{field} cross-build difference outside specified operands/padding: '
                                 f'DW={sorted(mismatches_ab-SKIP[field])} WAlt={sorted(mismatches_bz-SKIP[field])}')
        compare[field]=dict(bytes=length,allowed_operands_and_tables=len(SKIP[field]),
                            dos_win_differing_bytes=len(mismatches_ab),win_alt_differing_bytes=len(mismatches_bz),
                            semantic_routes_equal=True,normalization_only=True)
        if field in ('score','death_sound','state7_sound'):
            cols=[[v['relative_target'] for v in data[tag]['tables'][field]['classes']]
                  for tag in ('dos20','win110','winalt')]
            if cols[0]!=cols[1] or cols[1]!=cols[2]:
                raise AssertionError(f'cross-build {field} route target mismatch')
    # Extra DOS sound backend entry witness: selector 0 is still passed to
    # a handler. Whether anything plays depends on DS:414E and DS:3F64,
    # not merely on this numeric selector being zero.
    sound_code=dos20.read_bytes()
    sound_witness=[
        require(sound_code,0xC686,'c8 06 00 00 56 80 3e 4e 41 00 0f 84 e2 00',
                'DOS SFX backend rejects when global sound enabled byte is zero'),
        require(sound_code,0xC694,'8b 5e 06 8b c3 03 db 03 d8 03 db 83 bf 64 3f 00 0f 84 ce 00',
                'DOS SFX backend checks six-byte slot directory word for chosen selector'),
    ]
    result={'audit':'RE MAX v0.58 — GUARD death score/sound selector and variant gates',
            'version_note':'local evidence package, not GitHub release version',
            'original_game_executed':False,'runtime_trace_executed':False,
            'original_binaries_included':False,'cross_build':compare,'profiles':data,
            'dos20_sound_zero_selector_gate':{'selector_zero_reaches_backend':True,
              'global_enable_byte':'DS:414E','slot0_directory_word':'DS:3F64',
              'if_slot0_word_zero':'early return before external playback',
              'if_slot0_word_nonzero':'continues to downstream routines; final audible outcome OPEN',
              'witnesses':sound_witness},
            'open':[
                'Transitive SFX playback including selector zero, priority, resource type and memory cache',
                'GUARD class 0x15 negative-score reachability via normal gameplay (damage scalar class 0x15 returns 0 after external callback)',
                'All indirect callers of score, sound selectors and variant selectors',
                'Full rare-boss morph, drop and object/map mutation effects in hit/death helpers',
                'Loaded descriptor selector bytes +3B/+4B and fast flag +49/+59 for every resource',
                'RNG seed/order beyond local call graph (IRQ, render, DEMO, LOAD)',
                'OBJECT+18 writer/readers including clipping and stale projection cache',
                'DOS/Win16 world-state/pixel/timing 1:1 original trace'
            ]}
    return result


def write_results(report:dict,directory:Path)->None:
    directory.mkdir(parents=True,exist_ok=True)
    (directory/'evidence_v058.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    tab=report['profiles']['dos20']['tables']
    with (directory/'class_score_sound_v058.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['object_class_hex','score_signed','fatal_event_selector','state7_event_selector','note'])
        for clazz in range(0x00,0x100):
            si=clazz-8
            score=tab['score']['classes'][si]['selected_value'] if 0<=si<25 else 0
            death=tab['death_sound']['classes'][si]['selected_value'] if 0<=si<24 else 0
            state7=tab['state7_sound']['classes'][si]['selected_value'] if 0<=si<24 else 0
            note='special score -1000, fatal sound selector 0' if clazz==0x15 else ('class20 score exists, SFX default selector0' if clazz==0x20 else '')
            w.writerow([f'{clazz:02X}',score,death,state7,note])
    with (directory/'branch_event_order_v058.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['branch','step','trigger','local_effect','evidence_scope'])
        rows=[
            ('all_hit',1,'entry','damage scalar called; guaranteed initial RNG draw','DOS+Win16 original static'),
            ('fatal',2,'HP <= unsigned low8 damage','GUARD HP byte cleared to 0','DOS+Win16 original static'),
            ('fatal',3,'after HP cleared','fatal variant selector GUARD+12, descriptor+59; optional RNG repeats','DOS+Win16 original static'),
            ('fatal',4,'DS:4190 != 1 (DOS), DS:4C26 !=1 (Win16)','class death SFX selection invoked (optional RNG for 0F/10)','DOS+Win16 original static'),
            ('fatal',5,'all lethal after selector','sequence state update + score lookup','DOS+Win16 original static'),
            ('fatal',6,'score value returned','signed CWD; 32-bit score add with carry','DOS+Win16 original static'),
            ('fatal',7,'after score update','event dispatcher with argument 4; MAP/object pointer byte write','DOS+Win16 original static'),
            ('nonfatal',2,'HP > low8 damage and damage!=0 AND old state == 7','state7 event selector called before HP decrease','DOS+Win16 original static'),
            ('nonfatal',3,'HP > low8 damage and damage!=0','HP decrease and GUARD+12=8','DOS+Win16 original static'),
            ('nonfatal',4,'strategy == 4','skip nonfatal variant selector','DOS+Win16 original static'),
            ('nonfatal',5,'strategy != 4','nonfatal variant selector GUARD+12 nonzero forces RNG','DOS+Win16 original static'),
        ]
        w.writerows(rows)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dos20',type=Path,required=True)
    ap.add_argument('--win110',type=Path,required=True)
    ap.add_argument('--winalt',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ns=ap.parse_args()
    result=audit(ns.dos20,ns.win110,ns.winalt)
    write_results(result,ns.out)
    print(f'PASS: 3 fingerprints, 25+24+24 class routes x 3 builds, 5 function bodies x 3 builds; out={ns.out}')

if __name__=='__main__':main()
