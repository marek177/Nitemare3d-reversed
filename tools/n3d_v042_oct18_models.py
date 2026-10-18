#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
def damage_order(build:str)->str:return "gate_before_calc" if build=="dos10_19" else "calc_before_gate"
def rng_mask(c:int)->int:
 c&=255
 if c==0x08:return 7
 if c in (0x09,0x0A):return 15
 if 0x11<=c<=0x14:return 31
 return 0
def feedback_step(timer:int)->dict:
 if timer<0:return {"timer_after":timer,"selector":None,"active":False}
 after=timer-1
 return {"timer_after":after,"selector":4 if after>=0 else 3,"active":True}
def secret_save(count:int)->dict:
 n=max(0,min(int(count),32))
 return {"meaningful_local_bytes":n,"disk_bytes":32,"undefined_tail_bytes":32-n}
def io_success(ax:int)->bool:return int(ax)>=0
def door_load(platform:str)->dict:
 return {"records":64,"record_bytes":22,"runtime_prefix":12,"save_tail":10} if platform=="win16" else {"records":64,"record_bytes":18,"runtime_prefix":8,"save_tail":10}
def win_mode4_ack(count:int)->dict:
 after=int(count)-1
 if after>0:return {"count_after":after,"forced_present":True,"display_another":True,"end_message_mode":False,"next_index":after}
 return {"count_after":after,"forced_present":False,"display_another":False,"end_message_mode":True,"next_index":None}
POOL_LAYOUTS={"dos_dynamic_wall":{"capacity":64,"stride":18},"dos_class3_geometry":{"capacity":32,"stride":14},"win_dynamic_wall":{"capacity":64,"stride":22},"win_class3_geometry":{"capacity":32,"stride":22}}
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--secret-count",type=int);p.add_argument("--feedback",type=int);p.add_argument("--message-count",type=int);a=p.parse_args()
 out={"writer_sites_reclassified":62,"direct_object_pointer_call_edges":72,"pool_layouts":POOL_LAYOUTS,"timing_import_ordinals":[604,605,606,607,13]}
 if a.secret_count is not None:out["secret_save"]=secret_save(a.secret_count)
 if a.feedback is not None:out["feedback"]=feedback_step(a.feedback)
 if a.message_count is not None:out["win_mode4_ack"]=win_mode4_ack(a.message_count)
 print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
