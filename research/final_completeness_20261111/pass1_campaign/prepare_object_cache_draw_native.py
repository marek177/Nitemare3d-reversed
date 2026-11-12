"""OUTPUTS: extend the frozen04D8 capture through the first actual0156:05DE draw."""
import sys
from pathlib import Path
r=Path(sys.argv[1]);s=(r/'runtime_watch_object_cache.py').read_text(encoding='utf-8')
needle="   branch_returns.append(dict(stage=stage,prefix=prefix,pre_registers=pre"
block='''   request('EXEC BP %04X:000005DE'%(load+0x156));request('EXEC RUN');drawpre=wait_for(load+0x156,0x5de,30);drawext=extra_regs()
   drawframe=capture('draw_frame_before',drawpre['SS'],drawpre['SP'],6);drawretip,drawretcs,queue=struct.unpack('<3H',drawframe)
   drawslot=capture('draw_queue_before',drawpre['DS'],queue,18);assert struct.unpack_from('<H',drawslot,6)[0]==record
   drawrecord=capture('draw_record',drawpre['DS'],record,10);sourceoff,sourceseg=struct.unpack_from('<HH',drawrecord,6);capture('draw_source',sourceseg,sourceoff,area)
   objectoff,objectseg=struct.unpack_from('<HH',drawslot,2);capture('draw_object_prefix6',objectseg,objectoff,6)
   capture('draw_DS64_before',drawpre['DS'],0,65536)
   def planes(label):
    state={name:request('EXEC VGA '+name) for name in ('GC','SEQ','MODE','AC')};(out/('draw_VGA_'+label+'.json')).write_text(json.dumps(state,indent=2)+'\\n')
    palette={name:request('EXEC VGA '+name) for name in ('DAC','DACPAL')};(out/('draw_DAC_'+label+'.json')).write_text(json.dumps(palette,indent=2)+'\\n')
    gc='\\n'.join(state['GC']);gcindex=int(re.search(r'index=([0-9a-f]+)h',gc).group(1),16);readmap=int(re.search(r'rdmapsel=([0-9a-f]+)h',gc).group(1),16)
    request('EXEC OUTP 03CE 0004')
    for plane in range(4):
     request('EXEC OUTP 03CF %04X'%plane);capture('draw_'+label+'_plane%d'%plane,0xa000,0,65536)
    request('EXEC OUTP 03CF %04X'%readmap);request('EXEC OUTP 03CE %04X'%gcindex)
    restored={name:request('EXEC VGA '+name) for name in ('GC','SEQ','MODE','AC')};(out/('draw_VGA_'+label+'_restored.json')).write_text(json.dumps(restored,indent=2)+'\\n');assert all(state[name][1:-1]==restored[name][1:-1] for name in state)
   planes('before');request('EXEC BP %04X:%08X'%(drawretcs,drawretip));request('EXEC RUN');drawpost=wait_for(drawretcs,drawretip,30);drawpostext=extra_regs()
   capture('draw_DS64_after',drawpre['DS'],0,65536);capture('draw_frame_after',drawpre['SS'],drawpre['SP'],6);capture('draw_queue_after',drawpre['DS'],queue,18);planes('after')
   drawresult=dict(pre_registers=drawpre,pre_extra=drawext,post_registers=drawpost,post_extra=drawpostext,queue_offset=queue)
'''
assert s.count(needle)==1;s=s.replace(needle,block+needle).replace('slot_count=count,old_owner=owner))','slot_count=count,old_owner=owner,draw=drawresult))')
s=s.replace("'object_cache_calls.json'","'object_cache_draw_calls.json'").replace('object_cache_runtime=True,object_cache_calls=len(branch_returns)','object_cache_draw_runtime=True,object_cache_draw_calls=len(branch_returns)')
s=s.replace('original0768:04D8 whole object cache call,fullDGROUP/pointertable/index/slotowner/XMS readback; no full renderer or global parity claim','original0768:04D8 whole cache call then native0156:05DE first sprite draw with four65536B VGA planes; one draw,not full gameplay/global parity')
(r/'runtime_watch_object_cache_draw.py').write_text(s,encoding='utf-8')
