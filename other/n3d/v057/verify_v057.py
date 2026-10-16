#!/usr/bin/env python3
"""Nitemare 3-D v0.57: original-byte guarded LOS/damage/branch verifier.

Read-only. NO original EXE, graphic, or game-data bytes are distributed.
DOS addresses are offsets in the original headerless unpacked v2.0 load image;
Windows addresses are logical NE segment 3 offsets, not CS:IP runtime selectors.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path
from model_v057 import CLASS_PATH, STATE_MAP_3_TO_21, damage_scalar

PROFILES = {
 'dos20': dict(sha='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297',size=171360,geometry=0xBB60,damage=0x8590,hit=0x5F74,cs_hitbase=0x4C70,cs_damagebase=0x83D0),
 'win110':dict(sha='12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481',size=230400,geometry=0xD50A,damage=0x9FA2,hit=0x80F8,cs_hitbase=0,cs_damagebase=0),
 'winalt':dict(sha='144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22',size=230224,geometry=0xD45C,damage=0x9EF4,hit=0x8054,cs_hitbase=0,cs_damagebase=0),
}
GEOMETRY_SIZE=0x162 # entry ENTER .. two dedicated RETF exits
DAMAGE_SIZE=0x123   # from ENTER through last RETF
# Byte offsets that encode build-sensitive data addresses, explicit FAR targets
# or CS-relative jump-table targets; these are not arbitrary masked code bytes.
GEO_MUTABLE={0xE0,0xE1,0xE4,0xE5,0xF3,0xF4,
             0x10F,0x110,0x111,0x112,0x119,0x11A,0x11B,0x11C,
             0x135,0x136}
DAMAGE_OPERANDS=((0x12,2),(0x1E,4),(0x43,2),(0x46,40),
                 (0x76,2),(0x84,2),(0x90,2),(0x9B,2),(0x9E,4),
                 (0xAC,2),(0xB8,2),(0xC8,2),(0xD4,2),(0xE0,2),
                 (0xEC,2),(0xF8,2),(0x102,2),(0x10E,2))
DAMAGE_MUTABLE={i for off,size in DAMAGE_OPERANDS for i in range(off,off+size)}
# Destination rel offsets for 20 case entries (0C..1F), which are identical
# across DOS2/Win16 1.10/Win16 alternate after segment rebasing.
DAMAGE_CASE_REL=[0x6E,0x74,0x82,0x8E,0x8E,0x82,0xFD,0xFD,0x82,
                 0x98,0xAA,0xB6,0xC6,0xA5,0xDE,0xE5,0xE5,0x6E,
                 0xEA,0xF6]


def extract_win16_ne_segment3(raw:bytes)->tuple[bytes,int]:
    assert raw[:2]==b'MZ'
    ne = struct.unpack_from('<I',raw,0x3C)[0]
    assert raw[ne:ne+2]==b'NE'
    count=struct.unpack_from('<H',raw,ne+0x1C)[0]
    assert count>=3
    table=struct.unpack_from('<H',raw,ne+0x22)[0]
    align_shift=struct.unpack_from('<H',raw,ne+0x32)[0]
    ent=ne+table+16
    offs,length=struct.unpack_from('<HH',raw,ent)
    start=offs<<align_shift
    length=length or 65536
    segment=raw[start:start+length]
    assert len(segment)==length
    return segment,start


def require(c:bytes,at:int,hexbytes:str,why:str)->dict:
    expected=bytes.fromhex(hexbytes)
    actual=c[at:at+len(expected)]
    if actual!=expected:
        raise AssertionError(f'{why}: {at:05X} got {actual.hex()} expected {expected.hex()}')
    return dict(offset=f'{at:05X}',bytes_checked=len(expected),meaning=why)


def direct_offsets(c:bytes,pattern:bytes)->list[int]:
    matches=[];cursor=0
    while (i:=c.find(pattern,cursor))>=0:
        matches.append(i);cursor=i+1
    return matches


def normalized_masked_equal(a:bytes,b:bytes,mask:set[int])->bool:
    if len(a)!=len(b):return False
    return all(x==y for i,(x,y) in enumerate(zip(a,b)) if i not in mask)


def inspect_profile(tag:str,file:Path)->tuple[dict,dict]:
    p=PROFILES[tag]
    raw=file.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=p['sha'] or len(raw)!=p['size']:
        raise AssertionError(f'{tag} original mismatch SHA/size: {len(raw)} bytes sha={sha}')
    if tag=='dos20':code=raw;start=0;addr_type='DOS unpacked MZ load-image offset'
    else:code,start=extract_win16_ne_segment3(raw);addr_type='NE segment 3 logical offset'
    g=p['geometry'];d=p['damage'];h=p['hit']
    witnesses=[]
    # GEOMETRY all 354B live code; ensure branches and return endpoints.
    witnesses.append(require(code,g,'c8 18 00 00 57 56 8b 4e 0a 8b 5e 0c','LOS original function entry'))
    witnesses.append(require(code,g+0x85,'83 7e 0e 00 0f 8e cf 00','LOS maxSteps signed <=0 -> false'))
    witnesses.append(require(code,g+0xC9,'39 76 f2 75 07 39 7e f0 0f 84 81 00','endpoint compared before map lookup'))
    witnesses.append(require(code,g+0xF8,
        'f6 46 fa 02 74 26 f6 46 fa 04 75 58 f6 46 fa 08 74 1a',
        'nested WALL property 02,04,08 gate'))
    # Check incoming wall helper CALLs and object option conditional code
    witnesses.append(require(code,g+0x10A,'06 ff 76 fc 9a','dynamic WALL helper receives far MAP cell pointer'))
    witnesses.append(require(code,g+0x124,'80 7e 10 00 74 1c','object property check disabled by arg byte 0'))
    witnesses.append(require(code,g+0x13A,'f6 46 eb 02 74 06 f6 46 eb 20 74 16',
                             'OBJECT bit02 and !bit20 means block'))
    witnesses.append(require(code,g+0x156,'b0 01 5e 5f c9 cb','endpoint return AL=1'))
    witnesses.append(require(code,g+0x15C,'32 c0 5e 5f c9 cb','blocked/timeout return AL=0'))
    # explicit step-limit exit after increment, not a successful clear-line return
    witnesses.append(require(code,g+0x146,'8b 46 0e ff 46 f4 39 46 f4','loop counter increment compare'))
    # DAMAGE class+weapons: early unconditional RNG site and signed IDIV by25
    witnesses.append(require(code,d,'c8 04 00 00 57 56 8b 7e 0a 8e 46 0c 26 8b 75 18',
                             'damage scalar loads OBJECT+0x18'))
    assert code[d+0x1D]==0x9A,'unconditional direct RNG far call missing'
    witnesses.append(require(code,d+0x22,'b9 19 00 99 f7 f9 03 f2',
                             'unconditional RNG result modulo25, then SI+=DX'))
    witnesses.append(require(code,d+0x3F,'93 2e ff a7','20-entry class dispatch via CS word table'))
    witnesses.append(require(code,d+0x100,'83 3e','difficulty first gate'))
    witnesses.append(require(code,d+0x115,'8b c6 3d ff 00 7e 03 b8 ff 00',
                             'signed upper-255 clamp and no lower clamp'))
    # Jump entries are not x86 instructions; decode as WORD target offsets.
    case_targets=[]
    for index,rel in enumerate(DAMAGE_CASE_REL):
        actual=struct.unpack_from('<H',code,d+0x46+2*index)[0]+p['cs_damagebase']
        if actual!=d+rel:
            raise AssertionError(f'{tag} damage case {index+12:02X} target {actual:05X} != {d+rel:05X}')
        case_targets.append(dict(class_hex=f'{index+12:02X}',case_rel=f'{rel:03X}',path=CLASS_PATH[index+12]))
    # HIT consumes low 8 bits of the returned scalar and branches on <=HP
    witnesses.append(require(code,h,'c8 02 00 00 57 56 8b 7e 0a 8b 76 06','GUARD hit wrapper entry'))
    witnesses.append(require(code,h+0x1C,'2a e4 89 46 fe 8e 46 08 26 8a 44 10 3b 46 fe',
                             'damage producer AL zeroextended then GUARD HP <= damage gate'))
    witnesses.append(require(code,h+0xF1,'8a 46 fe 8e 46 08 26 28 44 10','nonlethal byte HP subtraction'))
    witnesses.append(require(code,h+0x12E,'2d 03 00 3d 12 00 77 2e 03 c0 93','GUARD state range 03..15h dispatch'))
    # Read all 19 state branch target WORDs, classify 3 canonical destinations.
    # DOS has 3 fewer bytes in trailing epilogue, but the case table order is identical.
    st_table=h+0x13E
    groups={'return':'return','transition_21':'transition_21','special_animation':'special_animation'}
    if tag=='dos20':
        target_roles={h+0x208:'return',h+0x164:'transition_21',h+0x1AA:'special_animation'}
    else:
        target_roles={h+0x20B:'return',h+0x164:'transition_21',h+0x1AA:'special_animation'}
    hit_routes=[]
    for i,expect in enumerate(STATE_MAP_3_TO_21):
        absolute=struct.unpack_from('<H',code,st_table+2*i)[0]+p['cs_hitbase']
        actual=target_roles.get(absolute,'UNKNOWN')
        if actual!=expect:
            raise AssertionError(f'{tag} hit state {3+i} route {actual}, wanted {expect}; raw_target={absolute:04X}')
        hit_routes.append(dict(state=3+i,role=expect,rel_offset=f'{absolute-h:03X}'))
    rec={
        'profile':tag,'sha256':sha,'original_executed':False,
        'entry_offsets':{'geometry':f'{g:05X}','damage_scalar':f'{d:05X}','guard_hit':f'{h:05X}'},
        'addr_type':addr_type,'ne_segment3_file_offset':f'{start:05X}' if start else None,
        'geometry_size':GEOMETRY_SIZE,'damage_scalar_size':DAMAGE_SIZE,
        'witnesses':witnesses,'class_case_targets':case_targets,'hit_state_routes':hit_routes,
        'unclosed':['WALL helper nested FAR side effects','per-class event helper for 0x15',
                    'damage/hit nested FAR routines','real map input reachability','runtime frame ordering'],
    }
    return rec,dict(geometry=code[g:g+GEOMETRY_SIZE],damage=code[d:d+DAMAGE_SIZE],hit=code[h:h+0x210],full=code)


def verify_all(dos:Path,win:Path,alt:Path)->dict:
    out={};blobs={}
    for tag,path in [('dos20',dos),('win110',win),('winalt',alt)]:
        out[tag],blobs[tag]=inspect_profile(tag,path)
    # Full-body original instruction windows, no blind fuzzy matching.
    geom_mismatch=[i for i,(a,b) in enumerate(zip(blobs['dos20']['geometry'],blobs['win110']['geometry'])) if a!=b]
    if set(geom_mismatch)!=GEO_MUTABLE:
        raise AssertionError(f'unexpected LOS differences at {[hex(x) for x in geom_mismatch]}')
    if not normalized_masked_equal(blobs['win110']['geometry'],blobs['winalt']['geometry'],GEO_MUTABLE):
        raise AssertionError('Win16 LOS has differences outside known build-specific operands')
    damagediff=[i for i,(a,b) in enumerate(zip(blobs['dos20']['damage'],blobs['win110']['damage'])) if a!=b]
    if not normalized_masked_equal(blobs['dos20']['damage'],blobs['win110']['damage'],DAMAGE_MUTABLE):
        raise AssertionError('damage scalar DOS vs Win differs outside operand windows')
    if not normalized_masked_equal(blobs['win110']['damage'],blobs['winalt']['damage'],DAMAGE_MUTABLE):
        raise AssertionError('damage scalar Win16 builds differ outside operand windows')
    # Direct FAR callsite counts for DOS image, not transitive/indirect calls.
    code=blobs['dos20']['full']
    los_calls=direct_offsets(code,bytes.fromhex('9a c0 0c ea 0a'))
    hit_calls=direct_offsets(code,bytes.fromhex('9a 04 13 c7 04'))
    if los_calls!=[0x01A5,0x542D,0x6A1B]:raise AssertionError(f'LOS call sites: {los_calls!r}')
    if hit_calls!=[0x6A2F,0x8125]:raise AssertionError(f'hit call sites: {hit_calls!r}')
    caller_checks=[
      require(code,0x196,'6a 00 51','selection caller: checkObject=0; dynamic limit CX'),
      require(code,0x541E,'50 6a 08','GUARD LOS caller: bool AX; limit=8'),
      require(code,0x6A0E,'66 68 10 00 01 00','hitscan caller: checkObject=1, steps=16'),
      require(code,0x6A23,'0a c0 74 10','weapon state 1 returns to scan on LOS AL=0'),
      require(code,0x6A37,'83 c6 1a','hitscan scan GUARD stride=26 after hit'),
    ]
    # The two nested far calls in DOS geometry, originally shown as unknown
    # callbacks in v0.56, are actual DOS 0:0000 and 0:01E0 routines.
    # No relocation guesses are needed for this DOS load-image mapping.
    nested_wall_checks=[
      require(code,0x0000,'55 8b ec 57 b8 fd 21 8e d8 33 c9 b8 76 30',
              'DOS lookup initializes ES:3076 18-byte moving record base'),
      require(code,0x0014,'39 0e 00 00',
              'DOS moving wall count is DS:0000'),
      require(code,0x0020,'26 39 7f 04 75 06 26 39 47 06 74 0e',
              'first matching FAR MAP cell pointer chosen by record+04/+06'),
      require(code,0x002C,'83 c3 12', 'lookup steps over 18B records'),
      require(code,0x0044,'68 42 00 9a 0c 00 ba 0f',
              'lookup miss triggers error-report routine with code 0x42'),
      require(code,0x01E0,
              '55 8b ec c4 5e 06 26 8b 4f 08 0b c9 74 0a 83 f9 04 74 05 32 c0 c9 cb 90 b0 01 c9 cb',
              'wall state+08 0 or 4 passes; everything else fails'),
      require(code,0xBC6E,'9a 00 00 00 00', 'geometry nested direct FAR call to DOS 0:0000'),
      require(code,0xBC78,'9a e0 01 00 00', 'geometry nested direct FAR call to DOS 0:01E0'),
      require(code,0xFBCC,'6a 01 9a eb 01 ee 11',
              'error helper routes through runtime exit-like routine with status 1'),
      require(code,0x120CB,'55 8b ec 33 c9',
              'DOS cleanup/exit mechanism normal entry'),
      require(code,0x12147,'8b 46 06 b4 4c cd 21',
              'DOS normal exit branch INT21/4C using caller exit code'),
    ]
    return dict(audit='REMAX v057 geometry + per-class GUARD damage scalar',
                provenance='verified against user-provided original DOS20 and Win16 NE binaries',
                original_game_executed=False,gameplay_runtime_trace=False,
                comparison=dict(geometry_byte_length=GEOMETRY_SIZE,
                    geometry_DOS_Win_equal_nonoperands=GEOMETRY_SIZE-len(GEO_MUTABLE),
                    geometry_DOS_Win_operand_only_mismatches=[f'{i:03X}' for i in geom_mismatch],
                    damage_byte_length=DAMAGE_SIZE,
                    damage_DOS_Win_differing_byte_count=len(damagediff),
                    damage_DOS_Win_equal_after_operand_mask=True,
                    damage_DOS_Win_operand_only_differences=[f'{i:03X}' for i in damagediff],
                    win_alt_geometry_equal_after_operand_mask=True,
                    win_alt_damage_equal_after_operand_mask=True),
                direct_DOS_callers=dict(geometry=[f'{i:05X}' for i in los_calls],
                                        guard_hit=[f'{i:05X}' for i in hit_calls],
                                        caller_opcode_checks=caller_checks),
                dos20_nested_wall_lookup=dict(
                    lookup='IMG:0000',state_gate='IMG:01E0',record_bytes=18,
                    record_pointer_fields=['+04','+06'],state_field='+08',
                    state_values_accepted=[0,4],
                    lookup_miss='IMG:FBAC invokes runtime exit path; ordinary exit contains INT 21h AH=4Ch',
                    raw_instruction_witnesses=nested_wall_checks,
                    win16_transitive_equivalence='OPEN'),
                input_domains=dict(damage_classes=list(f'{v:02X}' for v in range(12,32)),
                    damage_mode_examples=[0,1,2,3],difficulty_modes=[0,1,2]),
                profiles=out,
                evidence_policy='The full 354B geometry / 291B damage scalar body is checked across builds; nested callees and natural reachability OPEN')


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--dos20',type=Path,required=True)
    ap.add_argument('--win110',type=Path,required=True)
    ap.add_argument('--winalt',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    out=verify_all(args.dos20,args.win110,args.winalt)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Original-byte audit PASS: 3/3 fingerprints; 354B geometry; 291B damage; 20 class routes; 19 hit state routes each. JSON {args.out}')

if __name__=='__main__':main()
