"""Read-only geometry descriptor domain; not a witnessed RNG helper entry."""
import json,base64,struct,collections
from pathlib import Path
import runtime_probe as rp
R=rp.root;O=rp.out;DS=0x2f94;P={'session_id':'ses-1'}
def rpc(m,a):
 x=rp.rpc(m,a);assert rp.last_server_pid==23808 and 'result' in x;return x
def read(o,n):return rpc('memory.read',{**P,'address':{'space':'segmented','segment':f'0x{DS:04X}','offset':f'0x{o:08X}'},'length':n})
def data(x):return base64.b64decode(x['result']['data_base64'])
status=rpc('session.status',P);assert status['result']['state']=='stopped';r=rpc('state.get_registers',P);assert int(r['result']['segments']['cs'],16)==0xed3 and int(r['result']['instruction_pointer'],16)==0x2e0
count=read(0x626e,2);n=int.from_bytes(data(count),'little');assert n==960;buffer=read(0x62ac,n*28);b=data(buffer);source=json.loads((O/'wall_record_pass_observation.json').read_text());changed_from_pass=sum(x!=y for x,y in zip(b,data(source['after_return']['buffer'])[:n*28]));descriptors={}
for index in sorted({b[28*i+4] for i in range(n)}):
 x=read(0x4310+8*index,8);d=data(x);ptr=struct.unpack_from('<H',d,4)[0];descriptors[str(index)]={'read':x,'words':list(struct.unpack('<4H',d)),'timing_table':read(ptr,16) if ptr else None}
groups=collections.Counter();candidate=[]
for i in range(n):
 rec=b[28*i:28*i+28];d=descriptors[str(rec[4])]['words'];excluded=rec[6] in (7,0x2d,0x2f);groups[(rec[6],rec[4],d[2]!=0,d[1]!=0,excluded)]+=1
 if not excluded and d[1] and d[2]:candidate.append(i)
v={'status':'READ_ONLY_RUNTIME_ENDPOINT_SNAPSHOT','registers':r,'status_response':status,'count':count,'buffer':buffer,'descriptors':descriptors,'group_counts':[{'class6':k[0],'descriptor_index4':k[1],'timing_table_nonzero':k[2],'caller_speed_nonzero':k[3],'local_class_excluded':k[4],'count':n} for k,n in sorted(groups.items())],'candidate_indices':candidate,'buffer_bytes_changed_since_pass':changed_from_pass,'scope':'At first Demo header after native parent return; future frame/deferred-load mutations remainopen. FormulaDS4310+8*byte4 and gates are static0201:04F0/040E evidence; actual caller pointer ownership/visibility/list membership and activation thresholds not witnessed. Not a new RNG target capture.'};(O/'near_rng_descriptor_post_init.json').write_text(json.dumps(v,indent=2));print(json.dumps({'records':n,'descriptors':len(descriptors),'candidate_indices':candidate,'buffer_bytes_changed_since_pass':changed_from_pass,'groups':v['group_counts']}))
