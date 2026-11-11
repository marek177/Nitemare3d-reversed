"""Controlled execution of original read312E bytes, with explicit DOS adapter.
Usage: python replay_worx_read.py EMULATOR_DIR DECODER_DIR IMAGE INVENTORY OUT_DIR
Evidence kind: controlled_instruction_replay, NOT DOSBox-X/original-runtime.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path

def main():
    emudep,decdep,ipath,hpath,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(emudep),str(decdep)]
    from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR,UC_HOOK_CODE
    from unicorn.x86_const import UC_X86_REG_AX,UC_X86_REG_BX,UC_X86_REG_CX,UC_X86_REG_DX,UC_X86_REG_SI,UC_X86_REG_DI,UC_X86_REG_BP,UC_X86_REG_DS,UC_X86_REG_ES,UC_X86_REG_SS,UC_X86_REG_SP,UC_X86_REG_CS,UC_X86_REG_IP,UC_X86_REG_EFLAGS
    from iced_x86 import Decoder
    image=ipath.read_bytes();image_hash=hashlib.sha256(image).hexdigest()
    if image_hash!='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297':raise ValueError('image mismatch')
    inv=json.loads(hpath.read_text());rows=sorted((r for r in inv if 0x18d1e<=r['image_offset']<0x18dba),key=lambda r:r['image_offset'])
    cursor=0x18d1e;gaps=[]
    for r in rows:
        a=r['image_offset'];code=bytes.fromhex(r['bytes']);ins=Decoder(16,code,ip=r['ip']).decode()
        if a<cursor or image[a:a+len(code)]!=code or ins.is_invalid or ins.len!=len(code):raise ValueError('decoder mismatch')
        if a>cursor:gaps.append(dict(start=cursor,end_exclusive=a,hex=image[cursor:a].hex(),status='UNKNOWN'))
        cursor=a+len(code)
    if cursor!=0x18dba:raise ValueError('function end mismatch')
    cases=[dict(name='memory_full',mode=1,size=100,position=0,request=44),dict(name='memory_short',mode=1,size=20,position=0,request=44),dict(name='memory_eof',mode=1,size=20,position=20,request=44),dict(name='memory_position_past_end',mode=1,size=20,position=21,request=44),dict(name='file_full',mode=0,size=100,position=0,request=44,read_return=44),dict(name='file_short',mode=0,size=100,position=0,request=44,read_return=10),dict(name='file_eof',mode=0,size=100,position=100,request=44,read_return=0),dict(name='file_high_position_low_word_smaller',mode=0,size=100,position=0x10001,request=44,read_return=44),dict(name='file_read_error',mode=0,size=100,position=0,request=44,read_return=5,read_error=True),dict(name='file_seek_error_then_adapter_read',mode=0,size=100,position=6,request=44,read_return=10,seek_error=True)]
    cases += [dict(name='file_clamped_to_ten_remaining',mode=0,size=100,position=90,request=44,read_return=10),dict(name='file_size_high_word',mode=0,size=0x10064,position=0,request=44,read_return=44)]
    base=0x15bf0;results=[];boundaries={r['image_offset'] for r in rows}
    for case in cases:
        uc=Uc(UC_ARCH_X86,UC_MODE_16);uc.mem_map(0,0x100000);uc.mem_write(0,image)
        def w16(a,v):uc.mem_write(a,struct.pack('<H',v&65535))
        def w32(a,v):uc.mem_write(a,struct.pack('<I',v&0xffffffff))
        uc.mem_write(base+0x312d,bytes([case['mode']]))
        w16(base+0x3129,0x100);w16(base+0x312b,0x4000)
        w32(base+0x2df7,case['size']);w32(base+0x2dff,case['position'] if case['mode'] else 0)
        w16(base+0x2df3,7)
        payload=bytes((i%251)+1 for i in range(512));uc.mem_write(0x40100,payload)
        destination=0x30100;uc.mem_write(destination,b'\xcc'*128)
        registers={UC_X86_REG_CS:0x15bf,UC_X86_REG_IP:0x312e,UC_X86_REG_SS:0x7000,UC_X86_REG_SP:0x8000,UC_X86_REG_DS:0x2222,UC_X86_REG_ES:0x3000,UC_X86_REG_DI:0x100,UC_X86_REG_SI:0x7777,UC_X86_REG_BP:0x8888,UC_X86_REG_AX:0x9999,UC_X86_REG_BX:case['request'],UC_X86_REG_CX:0x4567,UC_X86_REG_DX:0xabcd,UC_X86_REG_EFLAGS:2}
        for reg,value in registers.items():uc.reg_write(reg,value)
        w16(0x78000,0x6000)  # synthetic caller's near return address
        calls=[];trace=[];returned=[False]
        def setcf(value):
            flags=uc.reg_read(UC_X86_REG_EFLAGS);uc.reg_write(UC_X86_REG_EFLAGS,(flags|1) if value else (flags&~1))
        def interrupt(engine,number,unused):
            if number!=0x21:raise ValueError('unexpected interrupt')
            ax=uc.reg_read(UC_X86_REG_AX)
            if ax==0x4201:
                calls.append(dict(service='DOS_seek_query_adapter',position=case['position'],error=bool(case.get('seek_error'))))
                uc.reg_write(UC_X86_REG_AX,case['position']&65535);uc.reg_write(UC_X86_REG_DX,(case['position']>>16)&65535);setcf(case.get('seek_error',False))
            elif ax>>8==0x3f:
                count=uc.reg_read(UC_X86_REG_CX);reply=case['read_return'];error=case.get('read_error',False)
                calls.append(dict(service='DOS_read_adapter',requested=count,returned_ax=reply,error=error))
                if not error:
                    if reply>count:raise ValueError('adapter returned too many bytes')
                    target=uc.reg_read(UC_X86_REG_DS)*16+uc.reg_read(UC_X86_REG_DX);uc.mem_write(target,bytes([0x5a])*reply)
                uc.reg_write(UC_X86_REG_AX,reply);setcf(error)
            else:raise ValueError('unexpected DOS service '+hex(ax))
        def codehook(engine,address,size,unused):
            if address==base+0x6000:returned[0]=True;uc.emu_stop();return
            trace.append(address)
            if address not in boundaries:raise ValueError('execution escaped validated instruction boundaries')
        uc.hook_add(UC_HOOK_INTR,interrupt);uc.hook_add(UC_HOOK_CODE,codehook)
        uc.emu_start(0x18d1e,0,count=10000)
        if not returned[0]:raise ValueError('helper did not return')
        preserved={name:uc.reg_read(reg)==registers[reg] for name,reg in [('BX',UC_X86_REG_BX),('CX',UC_X86_REG_CX),('DX',UC_X86_REG_DX),('SI',UC_X86_REG_SI),('DI',UC_X86_REG_DI),('BP',UC_X86_REG_BP),('DS',UC_X86_REG_DS),('ES',UC_X86_REG_ES)]}
        if not all(preserved.values()) or uc.reg_read(UC_X86_REG_SP)!=0x8002:raise ValueError('register/stack contract mismatch')
        if case['mode']:
            count=uc.reg_read(UC_X86_REG_AX);p=case['position']
            expected=payload[p:p+count]+b'\xcc'*(128-count)
            if bytes(uc.mem_read(destination,128))!=expected:raise ValueError('memory copy result or untouched tail mismatch')
        results.append(dict(input=case,ax=uc.reg_read(UC_X86_REG_AX),cf=uc.reg_read(UC_X86_REG_EFLAGS)&1,sp=uc.reg_read(UC_X86_REG_SP),preserved=preserved,calls=calls,destination_first64=bytes(uc.mem_read(destination,64)).hex(),instruction_trace=trace,evidence_kind='controlled_instruction_replay_with_DOS_adapter'))
    byname={r['input']['name']:r for r in results}
    for name,expected in [('memory_full',(44,0)),('memory_short',(20,0)),('memory_eof',(0,0)),('file_short',(10,0)),('file_eof',(0,1)),('file_read_error',(5,1))]:
        r=byname[name]
        if (r['ax'],r['cf'])!=expected:raise ValueError('unexpected controlled result '+name)
    if not any(c['service']=='DOS_read_adapter' for c in byname['file_high_position_low_word_smaller']['calls']):raise ValueError('high-position path did not issue read')
    if byname['file_clamped_to_ten_remaining']['calls'][-1]['requested']!=10:raise ValueError('remaining-byte clamp not observed')
    out.mkdir(parents=True,exist_ok=True)
    with (out/'instructions.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    function=dict(name='read_helper_312e',start=0x18d1e,end_exclusive=0x18dba,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows),inventory_gaps=gaps,status='PARTIAL',pass320_membership='UNKNOWN')
    result=dict(image_sha256=image_hash,function=function,cases=results,controlled_replay_cases=len(results),union_executed_instruction_starts=len({a for r in results for a in r['instruction_trace']}),emulator='Unicorn 2.1.4, UC_MODE_16',emulator_native_files=[dict(path=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in emudep.rglob('*.dll')],DOSBox_X_tests=0,original_runtime_tests=0,new_deep_verified_bytes=0,scope='Original helper bytes execute; DOS/OS responses and initial state controlled; no natural reachability or full-game behavior proof')
    (out/'read_replay_evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(function=function,cases=[dict(name=r['input']['name'],ax=r['ax'],cf=r['cf'],calls=r['calls']) for r in results]),indent=2))

if __name__=='__main__':main()
