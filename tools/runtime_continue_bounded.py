from runtime_probe import rpc,root,out
import json,sys
p={'session_id':json.loads((root/'work/runtime/palette_control.json').read_text())['session_id']}
wait_ms=int(sys.argv[1]) if len(sys.argv)>1 else 5000
assert 1<=wait_ms<=5000
s=rpc('session.status',p);assert s['result']['state']=='stopped'
r=rpc('execution.continue',p);op=r['result']['operation_id']
(root/'work/runtime/bounded_continue_control.json').write_text(json.dumps({**p,'operation_id':op}))
for _ in range(1 if len(sys.argv)>1 else 4):
    r=rpc('execution.wait',{**p,'operation_id':op,'timeout_ms':wait_ms})
    if r.get('result',{}).get('state')=='stopped':break
if r.get('result',{}).get('state')!='stopped':
    pause=rpc('execution.pause',p)
    pause_op=pause.get('result',{}).get('operation_id')
    if pause_op:
        for _ in range(3):
            r=rpc('execution.wait',{**p,'operation_id':pause_op,'timeout_ms':1000})
            status=rpc('session.status',p)
            if status.get('result',{}).get('state')=='stopped':break
status=rpc('session.status',p)
assert status['result']['state']=='stopped','Operation still live: retain existing handle'
regs=rpc('state.get_registers',p)
(out/f'bounded_stop_revision_{regs["result"]["state_revision"]}.json').write_text(json.dumps({'status':status,'registers':regs},indent=2))
