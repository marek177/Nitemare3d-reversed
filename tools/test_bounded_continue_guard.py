from pathlib import Path
import sys,types,runpy,json
R=Path.cwd();calls=[];fake=types.ModuleType('runtime_probe');fake.root=R;fake.out=R/'outputs';fake.rpc=lambda *a,**k:calls.append((a,k));old=sys.modules.get('runtime_probe');sys.modules['runtime_probe']=fake
for arg in ['0','10000','invalid']:
 calls.clear();sys.argv=['runtime_continue_bounded.py',arg]
 try:runpy.run_path(str(R/'work/runtime_continue_bounded.py'),run_name='__main__')
 except (AssertionError,ValueError):pass
 else:raise AssertionError('Invalid argument accepted')
 assert calls==[],calls
if old:sys.modules['runtime_probe']=old
else:del sys.modules['runtime_probe']
O=R/'outputs/runtime_guard_20261107';O.mkdir(exist_ok=True);(O/'validation.json').write_text(json.dumps({'status':'PASS','invalid_arguments':['0','10000','invalid'],'emulator_calls':0,'scope':'Regression for invalid-input validation before execution.continue; no runtime parity claim.'},indent=2));print('PASS:3 invalid arguments, zero emulator calls')
