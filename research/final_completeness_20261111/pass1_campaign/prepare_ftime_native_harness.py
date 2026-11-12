"""OUTPUTS: original game clock->ftime->DOS date/time capture."""
from pathlib import Path
import sys
r=Path(sys.argv[1]);s=(r/'runtime_watch_calendar.py').read_text(encoding='utf-8');a=s.index("  if stage=='calendar_entry':");z=s.index('  if stage:\n',a)
block='''  if stage=='clock_sample_entry':
   prefix='ftime_00_';pre=reg
   def capture(name,seg,off,n):
    raw=dump(seg,off,n,prefix+name+'.bin');capture_files.append(work/(prefix+name+'.bin'));return raw
   def extra_regs():
    response=request('EXEC EV SI DI BP');line=next(x for x in response if re.fullmatch(r'[0-9A-Fa-f]+ [0-9A-Fa-f]+ [0-9A-Fa-f]+',x));return dict(zip(('SI','DI','BP'),map(lambda x:int(x,16),line.split())))
   flags=capture('flags_%03d'%len(branch_returns),pre['DS'],0x3cc7,9)
   if flags[0]==0 and flags[8]!=0:
    branch_returns.append(dict(stage='skipped_BIOS_sample',pre_registers=pre));request('EXEC RUN');continue
   ext=extra_regs();frame=capture('frame_before',pre['SS'],pre['SP'],4);retip,retcs=struct.unpack('<2H',frame)
   capture('DS64_before',pre['DS'],0,65536)
   request('EXEC BP %04X:%08X'%(retcs,retip));request('EXEC BP %04X:00002AEA'%(load+0x11ee));request('EXEC RUN')
   ftreg=wait_for(load+0x11ee,0x2aea,30);ftframe=capture('ftime_frame',ftreg['SS'],ftreg['SP'],6);ftretip,ftretcs,timeb_ptr=struct.unpack('<3H',ftframe)
   capture('timeb_before',pre['DS'],timeb_ptr,14)
   request('EXEC BP %04X:00003A11'%(load+0x11ee));request('EXEC RUN');datereg=wait_for(load+0x11ee,0x3a11,30)
   request('EXEC BP %04X:00003A2B'%(load+0x11ee));request('EXEC RUN');timereg=wait_for(load+0x11ee,0x3a2b,30)
   assert (timereg['CX']>>8)!=0 or (timereg['CX']&255)!=0,'midnight reread requires separate capture harness'
   request('EXEC BP %04X:%08X'%(ftretcs,ftretip));request('EXEC RUN');ftpost=wait_for(ftretcs,ftretip,30)
   capture('timeb_after',pre['DS'],timeb_ptr,14);capture('DS64_ftime_return',pre['DS'],0,65536)
   request('EXEC RUN');post=wait_for(retcs,retip,30);postext=extra_regs()
   capture('DS64_after',pre['DS'],0,65536);capture('frame_after',pre['SS'],pre['SP'],4)
   branch_returns.append(dict(stage=stage,prefix=prefix,pre_registers=pre,pre_extra=ext,ftime_entry_registers=ftreg,date_return_registers=datereg,time_return_registers=timereg,ftime_return_registers=ftpost,post_registers=post,post_extra=postext,timeb_offset=timeb_ptr))
   success=True;break
'''
s=s[:a]+block+s[z:]
s=s.replace("points[(load+0x11ee,0x2dc0)]='calendar_entry'","points[(load+0xbde,0x18)]='clock_sample_entry'")
s=s.replace("'calendar_calls.json'","'ftime_calls.json'").replace('calendar_runtime=True,calendar_calls=len(branch_returns)','ftime_runtime=True,ftime_calls=sum(x[\'stage\']==\'clock_sample_entry\' for x in branch_returns)')
s=s.replace('original11EE:2DC0 whole calendar conversion with native arguments/timezone-ready/fullDGROUP snapshots; no renderer or global calendar parity claim','original0BDE:0018 whole CRT clock sample plus nativeftime output/DOS date-time/fullDS64 snapshots; no full calendar/BIOS path parity claim')
(r/'runtime_watch_ftime_v2.py').write_text(s,encoding='utf-8')
