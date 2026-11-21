from pathlib import Path
import json
R=Path.cwd();O=R/'outputs/bsf_native_q_20261107';v=json.loads((O/'validation.json').read_text());assert v['ordered_byte_stores']==54
for name in ['nite3d20_0FBA_01B2.json','nite3d20_083D_29CA.json']:
 p=R/'outputs/evidence/function_records'/name;x=json.loads(p.read_text());x['Q_native_startup_evidence']={'status':'VERIFIED_NATIVE_BOUNDED_INVOCATION','pid':58896,'loadbase':'0823','trace_events':719,'ordered_transform_sites':54,'actual_FAR_return':'083D:2A3A','checksum_branch':'2A3A ->2A3D ->2A3F ->2A4F','decoded_DS363B':1,'proof':'bsf_native_q_20261107/validation.json','scope':'One original startup invocation; current trace includes caller stop instruction without claiming it executed. Full file-read, error, arbitrary alias/IRQ and boundary domains remainopen.'};p.write_text(json.dumps(x,indent=2));(O/name).write_text(json.dumps(x,indent=2))
for name in ['runtime_trace_index.json','function_callgraph.json']:
 p=R/'outputs/evidence'/name;x=json.loads(p.read_text());x['Q_native_BSF_startup']={'status':'VERIFIED_NATIVE_BOUNDED','proof':'bsf_native_q_20261107/validation.json','call':'083D:2A35 ->0FBA:01B2 ->083D:2A3A','checksum_branch_target':'083D:2A4F','full_goal_complete':False};p.write_text(json.dumps(x,indent=2))
print('Updated two function records and canonical runtime/callgraph annotations.')
