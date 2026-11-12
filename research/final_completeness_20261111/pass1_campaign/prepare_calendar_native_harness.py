"""OUTPUTS: freeze a native calendar-converter call capture, no game patches."""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'runtime_watch_image_retrieval.py').read_text(encoding='utf-8');a=s.index("  if stage=='image_retrieval_entry':");z=s.index('  if stage:\n',a)
block='''  if stage=='calendar_entry':
   prefix='calendar_00_';pre=reg
   def capture(name,seg,off,n):
    raw=dump(seg,off,n,prefix+name+'.bin');capture_files.append(work/(prefix+name+'.bin'));return raw
   def extra_regs():
    response=request('EXEC EV SI DI BP');line=next(x for x in response if re.fullmatch(r'[0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+',x));return dict(zip(('SI','DI','BP'),map(lambda x:int(x,16),line.split())))
   ext=extra_regs();frame=capture('frame_before',pre['SS'],pre['SP'],16);retip,retcs,year,month,day,hour,minute,second=struct.unpack('<8H',frame)
   capture('dgroup_before',pre['DS'],0,0xe030)
   request('EXEC BP %04X:%08X'%(retcs,retip));request('EXEC BP %04X:00002DE6'%(load+0x11ee));request('EXEC RUN')
   tzreg=wait_for(load+0x11ee,0x2de6,30);capture('dgroup_timezone_ready',pre['DS'],0,0xe030)
   request('EXEC RUN');post=wait_for(retcs,retip,30);postext=extra_regs()
   capture('dgroup_after',pre['DS'],0,0xe030);capture('frame_after',pre['SS'],pre['SP'],16)
   branch_returns.append(dict(stage=stage,prefix=prefix,pre_registers=pre,pre_extra=ext,timezone_ready_registers=tzreg,post_registers=post,post_extra=postext,year_since1980=year,month=month,day=day,hour=hour,minute=minute,second=second))
   success=True;break
'''
s=s[:a]+block+s[z:]
s=s.replace(" for cs,ip in points:request", " points[(load+0x11ee,0x2dc0)]='calendar_entry'\n for cs,ip in points:request")
s=s.replace("points[(load+0x768,0x402)]='image_retrieval_entry';request('EXEC BP %04X:00000402'%(load+0x768))","pass")
s=s.replace("'image_retrievals.json'","'calendar_calls.json'").replace('image_retrieval_runtime=True,image_retrievals=len(branch_returns)','calendar_runtime=True,calendar_calls=len(branch_returns)')
s=s.replace('original0768:0402 whole call with XMS destination readback and direct manager return; no whole-memory or renderer parity claim','original11EE:2DC0 whole calendar conversion with native arguments/timezone-ready/fullDGROUP snapshots; no renderer or global calendar parity claim')
# Calendar may be called before the keyboard/menu path; do not require that unrelated prefix.
s=s.replace(" assert any(s['stage']=='irq_after_port_read' and s['registers']['AX']&255==0x39 for s in input_stops)"," # Native calendar can precede keyboard input.")
# Stop after the relevant captures, avoiding menu/font assertions unrelated to this earlier endpoint.
a=s.index(" sound_directory=dump(");z=s.index(" request('EXEC BPDEL *')",a);s=s[:a]+s[z:]
(r/'runtime_watch_calendar.py').write_text(s,encoding='utf-8')
