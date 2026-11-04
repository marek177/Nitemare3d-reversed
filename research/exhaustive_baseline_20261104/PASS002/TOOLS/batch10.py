from pathlib import Path
import runpy,struct,json,csv,hashlib,collections,re
N=runpy.run_path(str(Path(__file__).with_name('pass002.py')));globals().update({k:v for k,v in N.items()if not k.startswith('__')})
B=O/'BATCH_01_10';B.mkdir(exist_ok=True)
def part(seg,entry):return traverse(seg,entry,{0x398:table}if(seg,entry)==(0x476,0x326)else None)
# Each dossier carries exact machine evidence plus function-specific interpretation.
dossiers=[
{'id':'DOS_2_0_0201_000A','seg':0x201,'entry':0xa,'title':'100-slot byte initializer','role':'Confirmed local effect: writes 1 to the first byte of 100 slots, each 18 bytes apart. Meaning of that byte and relation to geometry records remain unknown.','args':'No stack arguments read. Inputs: DS, a valid mapped memory range and a valid far-return stack.','algorithm':'BX starts at 0x50F2; store byte 1; add 18; repeat while BX<0x57FA unsigned. No loop wrap; exactly 100 iterations. Invariant BX=0x50F2+18*k and all prior target bytes equal 1.','pseudocode':'''BX=0x50F2; // 000A
 do { DS8[BX]=1; BX=u16(BX+18); } while (BX<0x57FA); // 000D–0017
far_return(); // 0019''','data':'DS bytes 0x50F2+18*k, k=0..99; no other direct memory access except return stack. Physical DS provenance is conditional: startup establishes DS=load_base+0x2771 but prior callees before this call remain a barrier.','stack':'No frame/local pushes; RETF consumes 4 bytes. BX modified; arithmetic flags final ZF/PF=1, CF/AF/SF/OF=0. Other registers preserved subject to return.','unknown':'All alternate entries, caller-path DS preservation, field meaning, actual in-game invocation.','validation':'128 prior randomized cases plus 72 cross-version cases from PASS001; no new re-test claimed for this body.'},
{'id':'DOS_2_0_0201_001A','seg':0x201,'entry':0x1a,'title':'Fixed-point slope and endpoint-field calculation','role':'Confirmed arithmetic on an 18-byte caller-supplied record; geometry/interpolation meaning is strongly inferred from endpoint formulas and caller fields. Not yet connected to rendering pixels.','args':'Far call, caller cleans 10 bytes: [BP+6]=record offset, +8=x1, +0A=y1, +0C=x2, +0E=y2; BP is frame pointer after ENTER. Record +2/+6 read as x-like inputs. DS:[4554] is a y-like origin.','algorithm':'dx=s16(x2-x1), dy=s16(y2-y1). If dx!=0 store slope=(s32(u16(dy)<<16)/dx) at record+0A, using truncation toward zero. dx==0 stores slope 0. dy==0 stores y1 to +4 and +8; else dx==0 stores y1 to +4 and y2 to +8. Otherwise each endpoint uses y1 + trunc(s16(record_x-x1)*dy/dx), with 16-bit wrapping. Fixed-point start +0E/+10 is low32(slope*s16(record[2]-x1) + (u16(y1-origin)<<16)) in general branch; simple branches store 0 low and u16(y1-origin) high. DX:AX operands and 32-bit IMUL/IDIV are preserved exactly; no host-language float replacement.','pseudocode':'''dx=s16(x2-x1); dy=s16(y2-y1); // 0020–0031
slope=(dx!=0)?idiv_s32(s32(u16(dy)<<16),dx):0; // 0034–0057
store32(record+10,slope);
if (dy==0) { outA=y1; outB=y1; frac=u16(y1-origin)<<16; } // 005F–0088
else if (dx==0) { outA=y1; outB=y2; frac=u16(y1-origin)<<16; } // 006E–0088
else { // 008C–0123
 outA=u16(y1+idiv_s32(s16(load16(record+2)-x1)*dy,dx)); // 008C–00C8
 outB=u16(y1+idiv_s32(s16(load16(record+6)-x1)*dy,dx)); // 00CB–00F3
 frac=u32(slope*s16(load16(record+2)-x1)+(u16(y1-origin)<<16)); // 00F6–0123
}
store16(record+4,outA); store16(record+8,outB); store32(record+14,frac); // write-site addresses above, 0126
AX=hi16(frac); restore(SI,DI,BP); far_return(); // 0126–012C''','data':'Reads 5 stack words, record words +2/+6, global DS:4554. Writes record +4,+8,+0A..+0D,+0E..+11. Fields +0/+2/+6 are preserved. Caller examples 0201:017D and 01D5 pass a record and two dword endpoint pairs using PUSH CS/near CALL.','stack':'ENTER 16,0; saves DI/SI (4 bytes); temporary mixed 16/32-bit pushes balance along normal paths; LEAVE restores BP; RETF consumes 4, args remain. SI/DI/BP preserved; AX final high16(frac). BX/CX/DX and high halves of EAX/ECX/EDX can change. FLAGS path-dependent; IDIV arithmetic flags undefined.','unknown':'Record meaning, input range at all callers, all aliases/entries. First division faults for wrapped dx=-1 and dy=-32768; observed #DE leaves a partial execution, no normal postcondition. DS alias/stack/code overlap excluded from model.','validation':'1,006 fresh model-vs-Unicorn cases, including vertical/horizontal/general branches, signed wrap and one divide overflow. Full 64 KiB DS checked in every normal case.'},
{'id':'DOS_2_0_0201_012E','seg':0x201,'entry':0x12e,'title':'Scan table and assemble 18-byte spans','role':'Confirmed local memory/call sequence scans DS word pointers indexed by a signed coordinate range, emits 18-byte records and calls function 0201:001A. Span/geometry terminology is inferred; original object type unknown.','args':'No input stack arguments read. Global bounds DS:4548 and DS:454A; source pointer table DS:4564+2*index. Output base DS:4D6E and count DS:4D64.','algorithm':'Initialize SI=0, count=0, DI=4D6E; CX=start bound. Compute wrapped pointer-table address 4564+2*CX. Signed bound comparison controls scanning. When table pointer differs from SI, close previous record if signed count>0: record[0]=SI, record[6]=index-1, then call 001A(record, dwords SI+14 and SI+18) and advance DI by18. Set SI=new pointer, record[2]=index, call 083D:143C(0,SI), increment count, call error helper when signed count>=50. After loop unconditionally close final record and call 001A. Empty bounds therefore still execute finalization with SI=0; cannot simplify to empty output without proof.','pseudocode':'''SI=0; DS16[0x4D64]=0; DI=0x4D6E; i=s16(DS16[0x4548]); // 0134–0148
if (i<=s16(DS16[0x454A])) do { // 014B–0151
 p=DS16[u16(0x4564+2*i)]; // 0154–0157
 if (p!=SI) {
  if (s16(DS16[0x4D64])>0) {
   DS16[DI]=SI; DS16[DI+6]=u16(i-1); old=DI; DI=u16(DI+18); // 0162–016E
   calc_0201_001A(old,DS32[SI+0x14],DS32[SI+0x18]); // 0171–0180
  }
  SI=DS16[u16(0x4564+2*i)]; DS16[DI+2]=u16(i); // 0183–018B
  far_083D_143C(0,SI); // 018E–0196
  DS16[0x4D64]++; if (s16(DS16[0x4D64])>=50) error_helper(0x0166,50); // 0199–01AE
 }
 i=s16(i+1); // 01B1–01C0; current end bound reloaded each iteration
} while (i<=s16(DS16[0x454A]));
DS16[DI]=SI; DS16[DI+6]=u16(i-1); // 01C3–01C6
calc_0201_001A(DI,DS32[SI+0x14],DS32[SI+0x18]); // 01C9–01D8
restore(SI,DI,BP); far_return(); // 01DB–01DE''','data':'Count word at4D64; output spans base4D6E stride18; source table word4564+2*i; pointed source dwords +14/+18. Error string DS:0166 is "MAXSEG exceeded (%d)" under the startup DS mapping, direct byte evidence. This output region differs from initializer base50F2; do not conflate the two lists.','stack':'ENTER8,0; DI/SI saved. Calls push 10 bytes for 001A and use explicit PUSH CS+near CALL for far-return semantics. Error/helper return behavior affects global paths. Restores local frame and DI/SI on ordinary return.','unknown':'Source table producers and valid bounds, whether error helper exits, callback/callee memory effects, all entry aliases. If a callee changes bounds the loop is not statically bounded by its original values.','validation':'Static closure and cross-checked 001A call arguments. No function-wide runtime test claimed.'},
{'id':'DOS_2_0_0476_0326','seg':0x476,'entry':0x326,'title':'Argument dispatcher with proven 24-entry switch','role':'Confirmed argument-list dispatcher with lowercase second-character selector. CLI option effects are direct assignments/calls; full user-facing option meanings inferred only where supporting strings exist.','args':'[BP+6]=signed argc-like count; [BP+8]=near pointer to an argv-like near-pointer vector. Locals BP-5 byte mode, BP-4 and BP-2 words initially1; BP-8 pointer-table cursor.','algorithm':'Calls initialization helper then 0476:0000. Passes string "windir" to 11EE:248A; nonzero result writes byte3CCF=0 and word3CC2=18. SI starts1; if signed argc<=1 skip loop. Loop checks first byte of arg equals45 ("-"); otherwise calls error helper0314, but if it returns control still reads second byte. CBW sign-extends second byte, subtracts97, JA rejects unsigned values>23. BX=2*index; CS:[039E+BX] dispatches among 24 entries and16 distinct targets. Cases a/c/d/e/f/l/q/w consume extra argv words; q consumes two. All returning paths reach incrementSI then signed loop comparison. Epilogue calls 00CE, 0D29:274C and 01D0; global callee semantics remain open.','pseudocode':'''mode=0; argE=argL=1; // 032C–0336
far_0277_0C6E(); far_0476_0000(); // 0339–033F
if (far_11EE_248A(near_string(0x0A9F))!=0) { DS8[0x3CCF]=0; DS16[0x3CC2]=18; } // 0342–0356
for (i=1; i<s16(argc); ++i) { // 035C–0362,04E9–04ED
 arg=DS16[u16(argv+2*i)]; // 0366–0372
 if (DS8[arg]!=45) error_0476_0314(argc,argv); // 0374–0381
 key=u16(s8(DS8[arg+1])-97); // 0384–038D: CBW, not CWDE
 if (key>23) error_case(); else goto CS16[0x039E+2*key]; // 0390–0398
 // See CLI_dispatch_table.json and CASE_EFFECTS.md for all 24 mappings and case writes.
}
far_0476_00CE(); far_0D29_274C(argE,argL,mode); far_0476_01D0(mode,0); // 04F1–050F
restore(SI,DI,BP); far_return(); // 0512–0515''','data':'Table CS:039E..03CD is48 bytes of DATA, not instructions; padding at039D. Selector byte DS:[argv[i]+1]. Direct globals and formats listed in case table. Under startup DS, string0A9F="windir", decimal/hex scan formats at0AA6..0ABE.','stack':'ENTER8,0, savesDI/SI. Near calls preceded by PUSH CS are far-call-compatible, return address occupies4 bytes. 0476:0314 and format helper stack args explicitly cleaned at callers. AL mode pushed as AX with unconstrained AH; callee byte-vs-word contract not yet proved.','unknown':'Real exit/non-return semantics of error helper; argv bounds on options consuming more args; callee preservation of DS; meaning of all global fields; full runtime behavior.','validation':'1,024 exhaustive selector cases: all256 bytes ×4 initial upper-EAX patterns; all outgoing targets and valid indices match. Local static instruction graph grows69→159 rows after table recovery.'},
{'id':'DOS_2_0_0476_00CE','seg':0x476,'entry':0xce,'title':'Subsystem initialization sequence with progress logging','role':'Confirmed fixed sequence of helper calls alternating with debug strings. Sound/timer/display/memory/keyboard/mouse descriptions follow actual nearby strings, but successful return alone does not prove subsystem initialization success.','args':'No direct stack parameters read; DS provides string offsets and globals. External helpers receive explicit zero words where shown.','algorithm':'Log Initializing; call083D:29CA(0); log Bootstrap ok; call0C2B:00DC(0); log Sound ok; call0BDE:0004(0); log Timer ok; call0156:00D8(0); log Display ok; call0201:000A(); call0768:0024(0); log Memory ok; call06B0:0134(0); log Keyboard ok; call06B0:018C(0); log Mouse ok; call0D29:2696(); forward AX to0277:0336; call0277:02A6 and0277:0AE0; write byte3CD1=0; log Initialize complete. Exact meaning of first two helpers is inferred from subsequent message labels.','pseudocode':'''log_0476_0078(0x085C); call_083D_29CA(0); // 00CE–00DF
log_0476_0078(0x086D); call_0C2B_00DC(0); // 00E2–00F3
log_0476_0078(0x087B); call_0BDE_0004(0); // 00F6–0107
log_0476_0078(0x0885); call_0156_00D8(0); // 010A–011B
log_0476_0078(0x088F); call_0201_000A(); call_0768_0024(0); // 011E–0134
log_0476_0078(0x089B); call_06B0_0134(0); // 0137–0148
log_0476_0078(0x08A6); call_06B0_018C(0); // 014B–015C
log_0476_0078(0x08B3); AX=call_0D29_2696(); call_0277_0336(AX); // 015F–0174
call_0277_02A6(); call_0277_0AE0(); DS8[0x3CD1]=0; // 0177–0181
log_0476_0078(0x08BD); far_return(); // 0186–0190''','data':'Progress strings DS:085C,086D,087B,0885,088F,089B,08A6,08B3,08BD; only direct data write DS:3CD1=0. Callees have broader unknown side effects.','stack':'No frame. Logger uses PUSH CS+near CALL and caller removes one word. Zero-arg callees FAR call; explicit word arguments cleaned2. One AX return forwarded to next callee. Registers depend on all callees; function does not save them.','unknown':'Callee error behavior, register/segment preservation, execution timing, global interaction and failure recovery.','validation':'Static call ordering and source strings, direct xref to0201:000A confirmed in baseline graph. No full execution test.'},
{'id':'DOS_2_0_0476_0078','seg':0x476,'entry':0x78,'title':'Conditional variadic debug-file writer','role':'Strongly inferred debug writer using file-open/format-write/close-like helpers, supported by "debug.txt", "w", "a", error text and argument forwarding. Direct control and data effects confirmed; libc names remain inferred.','args':'Far-return compatible variadic frame: [BP+6]=format pointer; &SS:[BP+8] is variadic argument area; passes this near offset without explicit segment, so SS=DS or helper-specific interpretation is a precondition to the usual C model.','algorithm':'If DS byte3CD0=0 leave immediately. Otherwise choose mode offset082E ("w") when word082C=0, else0830 ("a"); call11EE:06E6(filename0832,mode); reset SP=BP; storeAX at082C. On AX=0 call error helper0FBA:000C("Error opening file %s", "debug.txt") without an unconditional local exit. If helper returns, continue to output helper with handle,format,&arguments, then close helper using082C.','pseudocode':'''push(BP); BP=SP; // 0078–0079
if (DS8[0x3CD0]!=0) { // 007B–0080
 mode=(DS16[0x082C]==0)?0x082E:0x0830; // 0082–008E
 AX=call_11EE_06E6(0x0832,mode); SP=BP; DS16[0x082C]=AX; // 0091–009C
 if (AX==0) { call_0FBA_000C(0x0846,0x083C); SP=BP; } // 009F–00AE
 call_11EE_2822(DS16[0x082C],SS16[BP+6],u16(BP+8)); SP=BP; // 00B0–00C0
 call_11EE_05FA(DS16[0x082C]); // 00C2–00C6
}
leave(); far_return(); // 00CB–00CC''','data':'Reads3CD0 and082C; writes082C only after open. Last closed handle/pointer retained as boolean choosing append mode on later calls. Does not zero082C after close. DS strings082E="w",0830="a",0832/083C="debug.txt",0846="Error opening file %s".','stack':'PUSH BP/MOV BP,SP, no fixed locals. MOV SP,BP drops variadic helper args. After close, LEAVE drops remaining pushed handle. RETF4. SavedBP restored. Other registers/FLAGS depend on branch/callees.','unknown':'Exact helper signatures and ownership, fatal-error termination behavior, validity of retained closed-handle-as-sentinel, DS=SS assumption at variadic area use.','validation':'Static bytes + direct source strings + inspected helper wrappers11EE:06E6 and2822. No host file-write execution test.'},
{'id':'DOS_2_0_0476_0000','seg':0x476,'entry':0,'title':'Conditional defaults and always-reset state','role':'Confirmed one-time guarded initialization plus unconditional resets. Semantic labels for most fields remain unknown.','args':'No stack args; input byteDS:082A is initialization guard.','algorithm':'If guard!=0 write dword3CCA=0x00070220; set bytes3CC6,3CC7,3CCE,3CCF to1; set words3CBC,3CBE,3CC0 toFFFF; clear guard082A and bytes3CC8,3CD0; word3CC2=25; word3CD6=0; byte3CDC=0. Then always write byte3CD1=1,byte3CD2=0,dword3CD8=0,word3CC4=FFFF. First and later calls differ intentionally.','pseudocode':'''if (DS8[0x082A]!=0) { // 0000–0005
 DS32[0x3CCA]=0x00070220; // 0007
 AL=1; DS8[0x3CC6]=DS8[0x3CC7]=DS8[0x3CCE]=DS8[0x3CCF]=AL; // 0010–001B
 AX=0xFFFF; DS16[0x3CBC]=DS16[0x3CBE]=DS16[0x3CC0]=AX; // 001E–0027
 AL=0; DS8[0x082A]=DS8[0x3CC8]=DS8[0x3CD0]=0; // 002A–0032
 DS16[0x3CC2]=25; DS16[0x3CD6]=0; DS8[0x3CDC]=0; // 0035–0041
}
DS8[0x3CD1]=1; DS8[0x3CD2]=0; DS32[0x3CD8]=0; DS16[0x3CC4]=0xFFFF; // 0044–0057
far_return(); // 005D''','data':'Writes listed byte/word/dword fields; first branch uses XOR AL,AL, so AX becomesFF00 (AH remainsFF from001E). On guard-zero path AX is preserved. Later instructions leave FLAGS untouched; guarded path final arithmetic flags from XOR (AF undefined), unguarded path from CMP guard,0.','stack':'No local frame/pushes; RETF4; AX changed toFF00 only in nonzero-guard branch. No calls; all other general/segment regs preserved except return.','unknown':'Names/units of globals and why25 changes to18 when windir is nonzero. Whether all valid calls share same DS.','validation':'Static complete local closure, all direct stores enumerated. Whole-program alternate-entry proof open.'},
{'id':'DOS_2_0_0768_0008','seg':0x768,'entry':8,'title':'Word getter at DS:3504','role':'Confirmed 16-bit state getter. Returned state meaning unknown.','args':'No stack args; reads word DS:3504.','algorithm':'MOV AX,word DS:[3504]; RETF. Little-endian word; no sign extension or arithmetic; all FLAGS unchanged.','pseudocode':'''AX=DS16[0x3504]; // 0008
far_return(); // 000B''','data':'Exactly2 bytes read atDS:3504/3505; no memory writes. Under nominal startup DS maps to module offset0x2AC14, but entry DS cannot yet be universally assumed.','stack':'No frame. RETF consumes4. AX modified; other registers preserved except CS/IP/SP return state; FLAGS unchanged.','unknown':'Global writers, meaning/range, entry aliases, caller-path DS provenance.','validation':'Static bytes and baseline direct-call candidate identity; no new runtime test claimed.'},
{'id':'WIN_1_10_0003_0D9E','seg':3,'entry':0xd9e,'title':'Unsigned byte getter at DS:4BE1','role':'Confirmed returns unsigned byte in AX; application meaning unknown.','args':'No stack args. NE segment index3, DS supplied by Windows/caller; do not equate index with a real-mode segment.','algorithm':'MOV AL,DS:[4BE1]; SUB AH,AH; RETF. SUB zeroesAH and fixes arithmetic flags unlike a flag-preserving zero-extension instruction.','pseudocode':'''AL=DS8[0x4BE1]; // 0D9E
AH=0; set_SUB_flags_for_equal_operands(); // 0DA1
far_return(); // 0DA3''','data':'One byte read atDS:4BE1, no stores. Full AX result0..255; upper16 EAX unchanged by16/8-bit operations in the CPU experiment.','stack':'No frame, RETF4. AX modified, FLAGS CF/AF/OF/SF=0,ZF/PF=1; other modeled flags preserved. Other registers preserved except return.','unknown':'Field producer and meaning, NE selector validation and protected-mode execution, alternate entries.','validation':'Exhaustive all256 byte values in isolated Unicorn with return-stack and zero-write checks.'},
{'id':'WIN_1_10_0003_0DA4','seg':3,'entry':0xda4,'title':'Unsigned byte getter at DS:4BE2','role':'Confirmed second adjacent byte getter with same operations as0D9E. It accesses a different field; semantic interchangeability is not established.','args':'No stack args; NE segment index3; DS context external.','algorithm':'MOV AL,DS:[4BE2]; SUB AH,AH; RETF. Independent field lookup; no conditional branches, loops, calls, RNG or time read.','pseudocode':'''AL=DS8[0x4BE2]; // 0DA4
AH=0; set_SUB_flags_for_equal_operands(); // 0DA7
far_return(); // 0DA9''','data':'One byte atDS:4BE2; no writes. Difference against0D9E is immediate absolute memory offset+1; algorithms same, inputs distinct.','stack':'No frame, RETF4. AX result0..255; CF/AF/OF/SF=0,ZF/PF=1, other modeled flags preserved.','unknown':'Field meaning, producers, whether first/second fields relate to input or other state; Win16 runtime selector and calling context.','validation':'Exhaustive all256 byte values in isolated Unicorn. Cross-version candidate search uses adjacent getter-pair signature.'}
]
# Build callable local NE model without applying arbitrary selector values to raw bytes.
NE=(R.parent/'inputs/nite3/windows/nite3w - 110.exe').read_bytes();lay=json.loads((R/'VERSIONS/WIN16/nite3w - 110.exe.layout.json').read_text());cg=json.loads((R/'CALLGRAPH/FUNCTION_CALLGRAPH.json').read_text());mat=[];newcounts={}
for number,d in enumerate(dossiers,1):
 fid=d['id'];dos=fid.startswith('DOS');f=part(d['seg'],d['entry'])if dos else None
 if dos:
  export_function(fid,f);ins=sorted(f['instructions'].values(),key=lambda i:i.address)
 else:
  sg=lay['segments'][d['seg']-1];raw=NE[sg['file_offset']+d['entry']:sg['file_offset']+d['entry']+6];ins=list(md.disasm(raw,d['entry']));f={'segment':d['seg'],'entry':d['entry'],'exits':[d['entry']+5],'calls':[],'unknown':[],'overlap':[],'blocks':[{'start':d['entry'],'instructions':[i.address for i in ins]}],'edges':[{'from':ins[0].address,'to':ins[1].address,'kind':'fallthrough'},{'from':ins[1].address,'to':ins[2].address,'kind':'fallthrough'}]};save('CFG/'+fid+'.json',f)
 lengths=[]
 for i in ins:
  if lengths and lengths[-1][1]==i.address:lengths[-1][1]=i.address+i.size
  else:lengths.append([i.address,i.address+i.size])
 total=sum(b-a for a,b in lengths);end=max(i.address+i.size for i in ins);start=min(i.address for i in ins);span=end-start;holes=[];cursor=start
 for a,b in lengths:
  if cursor<a:holes.append([cursor,a])
  cursor=b
 callers=[]
 for src,calls in cg.items():
  for c in calls:
   if c.get('target')==[d['seg'],d['entry']]and src.startswith('DOS')==dos:callers.append({'function_id':src,'address':c['address']})
 # Include newly recovered direct callers within this batch (e.g.012E ->001A).
 for other in dossiers:
  if not other['id'].startswith('DOS')or not dos:continue
  otherf=part(other['seg'],other['entry'])
  for c in otherf['calls']:
   if c['target']==[d['seg'],d['entry']]and not any(x['function_id']==other['id']and x['address']==c['address']for x in callers):callers.append({'function_id':other['id'],'address':c['address'],'source':'PASS002_recovered_call'})
 summ={'number':number,'function_id':fid,'entry':f'{d["seg"]:04X}:{d["entry"]:04X}','last_instruction':f'{d["seg"]:04X}:{ins[-1].address:04X}','end_exclusive':hex(end),'span_bytes':span,'decoded_instruction_bytes':total,'instruction_count':len(ins),'decoded_ranges':lengths,'gaps':holes,'local_returns':f['exits'],'local_unresolved_jumps':len(f['unknown']),'overlap_detected':f['overlap'],'local_block_count':len(f['blocks']),'direct_callsites':len(f['calls']),'full_boundaries_verified':False,'all_entry_points_verified':False,'complete_behavior_verified':False};mat.append(summ)
 instrtable='| Address | Original bytes | Corrected ASM |\n|---|---|---|\n'+'\n'.join(f'|{d["seg"]:04X}:{i.address:04X}|{i.bytes.hex()}|{corrected(i)} {i.op_str}|'for i in ins)
 memtable=[]
 for i in ins:
  for op in i.operands:
   if op.type==X86_OP_MEM:
    m=op.mem;segname=i.reg_name(m.segment)or('SS'if m.base in (X86_REG_BP,X86_REG_EBP,X86_REG_SP,X86_REG_ESP)else'DS');ea=' + '.join(x for x in [i.reg_name(m.base),i.reg_name(m.index),str(m.disp)if m.disp else'']if x)or'0';access=('R'if op.access&1 else'')+('W'if op.access&2 else'');memtable.append(f'|{i.address:04X}|{segname}|{ea}|{op.size}|{access or "decoder_unspecified"}|')
 memory='|IP|Segment|Effective address expression|Bytes|Decoder access|\n|---|---|---|---:|---|\n'+'\n'.join(memtable)if memtable else'No explicit memory operands (implicit stack accesses still apply).'
 calls='\n'.join(f'- {d["seg"]:04X}:{c["address"]:04X} → '+(f'{c["target"][0]:04X}:{c["target"][1]:04X}'if c['target']else'UNKNOWN')+f' ({c.get("near_far","FAR")}; PUSH CS prefix={c.get("push_cs_prefix",False)})'for c in f['calls'])or'No direct calls in the decoded body.'
 regrows=[]
 for i in ins:
  rd,wr=i.regs_access();rds=[i.reg_name(x)for x in rd];wrs=[i.reg_name(x)for x in wr]
  if bytes(i.bytes)==b'\x98':rds=['al'];wrs=['ax']
  elif bytes(i.bytes)==b'\x99':rds=['ax'];wrs=['dx']
  flags=[]
  for k,v in vars(__import__('capstone.x86_const',fromlist=[''])).items():
   if k.startswith('X86_EFLAGS_')and isinstance(v,int)and v and i.eflags&v:flags.append(k.removeprefix('X86_EFLAGS_'))
  sp='0 (ordinary instruction)'
  if i.mnemonic=='push':sp='-4'if i.bytes[0]==0x66 else'-2'
  elif i.mnemonic=='pop':sp='+4'if i.bytes[0]==0x66 else'+2'
  elif i.mnemonic=='enter':sp=f'-2-{i.operands[0].imm}; BP=oldSP-2 (nesting=0)'
  elif i.mnemonic=='leave':sp='SP=BP; BP=pop16(); delta path/frame dependent'
  elif i.group(CS_GRP_CALL):sp='-4 before FAR target'if i.mnemonic=='lcall'else'-2 before NEAR target; prior PUSH CS adds2'
  elif i.group(CS_GRP_RET):sp='+4 for RETF'if i.mnemonic.startswith('retf')else'+2 for RET'
  elif i.mnemonic in ('add','sub','mov')and i.operands and i.operands[0].type==X86_OP_REG and i.operands[0].reg==X86_REG_SP:sp=i.mnemonic+' '+i.op_str
  regrows.append({'address':f'{d["seg"]:04X}:{i.address:04X}','bytes':i.bytes.hex(),'mnemonic':corrected(i),'operands':i.op_str,'reads':','.join(rds),'writes':','.join(wrs),'FLAGS_decoder_actions':','.join(flags),'stack_effect':sp,'operand_sizes':','.join(str(x.size)for x in i.operands),'control_flow':'CALL'if i.group(CS_GRP_CALL)else'JUMP'if i.group(CS_GRP_JUMP)else'RETURN'if i.group(CS_GRP_RET)else'NEXT','verification':'static_decoder_annotations_with_98_99_correction; verify undefined flags and implicit segment context before implementation'})
 with (B/(f'{number:02d}_{fid}_INSTRUCTIONS.csv')).open('w',newline='')as out:
  w=csv.DictWriter(out,list(regrows[0]));w.writeheader();w.writerows(regrows)
 state={**summ,'caller_evidence':callers,'callee_evidence':f['calls']};save('DATAFLOW/'+fid+'.json',state)
 sha=hashlib.sha256((R.parent/'inputs/nite3/dos/N3D-UNFU.exe').read_bytes()if dos else NE).hexdigest()
 sections=[('Identity, build and proof scope',f'{fid}; SHA-256 `{sha}`. Reference version label from supplied filename; release provenance not independently established. Claim labels: Confirmed for machine effects, Inferred for semantic names, Unknown for unproved scope.'),('Entries and exact decoded boundaries','```json\n'+json.dumps(summ,indent=2)+'\n```\nRanges are half-open. These are exact locally decoded ranges under modeled call returns, not proof of all aliases/external entries. No next-function-end assumption.'),('Original bytes and ASM',instrtable),('CFG and blocks','See ../CFG/'+fid+'.json for all instruction edges, basic-block partition and local returns. Calls have explicit assumed-return continuations; non-returning callee proof is unresolved.'),('Caller/callee relationships','Callers:\n```json\n'+json.dumps(callers,indent=2)+'\n```\nCallees:\n\n'+calls),('Arguments and calling convention',d['args']),('Registers and FLAGS','Complete instruction-by-instruction read/write, FLAGS-action metadata and operand sizes are in '+f'{number:02d}_{fid}_INSTRUCTIONS.csv. Corrections98/99 applied to printed names and register sets. Metadata alone does not prove values/flags across external calls.'),('Stack frame and return state',d['stack']),('Memory operations and effective addresses',memory+'\n\nImplicit stack accesses and external callee accesses are additional. Segment defaults use BP/SP→SS; overrides take precedence. String-instruction destination ES context requires explicit review if present.'),('Globals and data structure fields',d['data']),('Dataflow and alias constraints','DS-origin evidence and caller references are in ../DATAFLOW/. Byte/word/dword aliases remain significant; do not collapse overlapping stores. All high-level models assume code, stack and described data do not destructively alias. Effective16-bit offsets wrap unless a narrower no-wrap argument is stated.'),('Constants, tables and strings',d['data']+'\nRelevant immediate values and their exact use sites are preserved in the ASM/CSV; numerical constants alone do not establish units.'),('Branches, loops and invariants',d['algorithm']),('Reconstructed algorithm',d['role']+'\n\n'+d['algorithm']),('RAW Ghidra/IDA decompilation','Unavailable. No raw Ghidra/IDA output was supplied or produced. This report preserves decoded bytes and marks hand reconstruction separately.'),('Corrected hand pseudocode','```c\n'+d['pseudocode']+'\n```\nFunctions named by addresses preserve unknown helper identity. FLAGS and register postconditions are specified separately; do not delete machine-state effects.'),('Behavioral reconstruction and pre/postconditions',d['role']+'\n\nPreconditions: '+d['args']+'\n\nSupported normal effects: '+d['algorithm']+'\n\nFault/non-return paths may invalidate normal postconditions; see unknowns.'),('Cross-version matching','See ../ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json and existing PASS001 matrices. Byte signatures are correspondence candidates. Missing match is UNKNOWN_MATCH, not ADDED/REMOVED. Field-address differences need data-layout mapping before semantic equivalence.'),('Instruction additions/removals/modifications','No unproved additions/removals claimed. Candidate signatures and differing operands are retained exactly; Win getter pair differs only in DS address between the two local bodies. Math prototype changes and global displacements are not normalized away without evidence.'),('CFG changes and error paths',d['unknown']+'\n\nLocal unresolved targets: '+json.dumps(f['unknown'])+'. Zero local unresolved jumps is not a whole-program CFG-complete claim.'),('Dependencies and platform assumptions','DOS addresses are load-module-relative segment:offset; capture used load_segment0x1000. Win addresses use NE segment index:offset and original physical segment table; copied-code Unicorn execution does not validate Windows selectors. No rendering/platform equivalence implied.'),('Timing, RNG and observable state','No supported timing/cadence claim. Direct instruction set and calls are shown; any time/RNG/I/O behavior of called functions remains a dependency. Leaf bodies without such reads have no direct RNG/time access.'),('Runtime/emulation evidence',d['validation']+'\nAll new experiments are isolated CPU or startup-prefix simulations, not original game gameplay.'),('Unresolved questions and next discriminating tests',d['unknown']+'\nNext: establish caller contexts and DS at actual entry, trace producers for each field, validate alternate/tail/shared entries, and compare same inputs against original runtime. Breakpoints at entry/return with stack/segment snapshots distinguish calling-convention hypotheses.'),('Verification status and history','2026-11-04 PASS002/BATCH01–10. Static local analysis only unless explicit experiment listed. Complete per-function verification false until all relevant global-entry/boundary/context/runtime gates are met. Original bytes, scripts and output hashes retained. Confidence High for decoded byte-local operations; Medium/Low for semantic naming depending on unresolved data provenance.')]
 text=f'# Function {number}/10 — {fid}\n\n{d["title"]}\n\n'+''.join(f'## {ix}. {heading}\n\n{body}\n\n'for ix,(heading,body)in enumerate(sections,1));(B/(f'{number:02d}_{fid}.md')).write_text(text)
# Cross-version candidate signatures, no false automatic function identity.
patterns={
 'DOS_2_0_0201_000A':re.escape(b'\xbb')+b'..'+re.escape(bytes.fromhex('c6070183c31281fb'))+b'..'+re.escape(bytes.fromhex('72f4cb')),
 'DOS_2_0_0201_001A':re.escape(bytes.fromhex('c810000057568b7e0a8b460c2b46088946fe')),
 'DOS_2_0_0201_012E':re.escape(bytes.fromhex('c8080000575633f68936'))+b'..'+re.escape(b'\xbf')+b'..'+re.escape(bytes.fromhex('8b0e'))+b'..'+re.escape(bytes.fromhex('8bc103c1')),
 'DOS_2_0_0476_0326':re.escape(bytes.fromhex('c80800005756c646fb00b801008946fc8946fe')),
 'DOS_2_0_0476_00CE':re.escape(b'\x68')+b'..'+re.escape(bytes.fromhex('0ee8'))+b'..'+re.escape(bytes.fromhex('83c4026a009a')),
 'DOS_2_0_0476_0078':re.escape(bytes.fromhex('558bec803e'))+b'..'+re.escape(bytes.fromhex('0074'))+b'.'+re.escape(bytes.fromhex('833e'))+b'..'+re.escape(bytes.fromhex('007505b8')),
 'DOS_2_0_0476_0000':re.escape(bytes.fromhex('803e'))+b'..'+re.escape(bytes.fromhex('00743d66c706'))+b'..'+re.escape(bytes.fromhex('20020700')),
 'DOS_2_0_0768_0008':re.escape(b'\xa1')+b'..'+re.escape(b'\xcb')}
cv=[]
for p in sorted((R/'VERSIONS/DOS').glob('*.loaded.bin')):
 data=p.read_bytes()
 for fid,pattern in patterns.items():
  hits=[{'image_offset':hex(m.start()),'signature_bytes':m[0].hex()}for m in re.finditer(pattern,data,re.S)];cv.append({'function_id':fid,'file':p.name,'candidate_matches':hits,'classification':'UNKNOWN_MATCH','scope':'raw_image_signature_locators; instruction_boundary_and_full_correspondence_not_proved'})
for x in win_matches:
 for fid in ['WIN_1_10_0003_0D9E','WIN_1_10_0003_0DA4']:cv.append({'function_id':fid,'file':x['file'],'candidate_matches':x['candidate_pairs'],'classification':x['classification'],'scope':x['equivalence_scope']})
save('ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json',cv)
with (B/'FUNCTIONS_01_10_BOUNDARIES.csv').open('w',newline='')as out:
 fields=list(mat[0]);w=csv.DictWriter(out,fields);w.writeheader();w.writerows({k:json.dumps(v)if isinstance(v,(list,dict))else v for k,v in row.items()}for row in mat)
save('REPORTS/BATCH10_SUMMARY.json',mat)
# Case-by-case exact effect map from recovered table and bytes.
effects={'a':'consume next argv; format%s into DS:3CDC; call0277:0C6E','b':'local byte[BP-5]=1','c':'consume next argv; scan%d into DS:3CC0','d':'consume next argv; scan%d into DS:3CBC','e':'consume next argv; scan%d into local[BP-4]','f':'consume next argv; scan%d into DS:3CBE','l':'consume next argv; scan%d into local[BP-2]; AX==0 calls default helper','o':'DS8[3CD0]=1 (enables debug writer)','p':'DS8[3CC7]=0','q':'DS8[3CC8]=1; consume next argv scan%x into3CCA; require AX==1 else default; consume another scan%d into3CCC; require AX==1 else default','r':'DS16[3CD6]=1','s':'DS8[3CC6]=0','t':'DS8[3CCF]=0; DS16[3CC2]=18','w':'consume next argv scan%d into4144; AND low byte4144 withF8; call0277:0BC2(word4144)','x':'DS8[3CCE]=0'}
(O/'REPORTS/CASE_EFFECTS.md').write_text('# 0476:0326 case map\n\n|Key|Target|Direct effect|\n|---|---|---|\n'+'\n'.join(f'|{chr(97+k)}|0476:{t:04X}|{effects.get(chr(97+k),"Default/error helper0314; continuation depends on helper return") }|'for k,t in enumerate(table))+'\n\nScan-helper names/scanf-like behavior inferred from input/format/output call shape; helpers are not fully proven. Signed argc and extra-argument bounds remain open.\n')
report='''# PASS002 — deep static analysis, functions 1–10

Ten individually numbered dossiers preserve exact bytes, decoded reachable ranges, CFG/basic blocks, direct callsites, instruction register/FLAGS/operand metadata, memory expressions, stack effects and hand pseudocode. This batch combines eight DOS functions and two Win16 functions. It is a focused batch, not a claim that these are the game's canonical first ten functions.

## New established evidence

- DOS0476:0326: the previously unresolved switch at0398 reads24 word entries atCS:039E..03CD. The full256-value selector domain is proven by unsigned guard afterCBW/subtraction. There are16 distinct targets; local closure increases69→159 instruction rows. The table is DATA, not code. All24 case effects are mapped separately.
- DOS0201:001A: 111 instructions, mixed16/32-bit signed fixed-point arithmetic on an18-byte caller record; recovered slope, endpoint values and fractional start, preserving wrapped16-bit differences and signed truncation. One input class causes real#DE: wrapped dx=-1 anddy=-32768 in firstIDIV. This is observed in isolated CPU execution, not assumed safe.
- DOS0201:012E: source table scan emits18-byte spans and invokes001A with two endpoint dwords. Error string is"MAXSEG exceeded (%d)". Output base4D6E differs from the100-slot initializer base50F2; shared stride does not prove same list.
- DOS0476:0078: debug.txt writer with first-write"w" and later"a" mode; file handle retained as sentinel after close. Helper library names remain inferred until deeper review.
- Startup prefix establishes DS=0x3771 at load_base0x1000, module-relative0x2771, under explicit syntheticDOS services. This does not propagate through unverified callees to the initializer.
- Win16 getters0003:0D9E and0DA4 return byte fieldsDS:4BE1/4BE2 zero-extended toAX and alterFLAGS viaSUB AH,AH. Adjacent getters are not the same field.
- Capstone5.0.7 in16-bit mode prints unprefixed98/99 asCWDE/CDQ. Original raw output retained; correctedCBW/CWD and register effects are attached and independently cross-checked with objdump and CPU behavior. PASS001 raw metadata remains historical, not silently rewritten.

## Experiments and limits

1,006 arithmetic-model cases,512 exhaustive getter cases,1,024 dispatch cases and1 synthetic startup-prefix experiment pass:2,543 new experiments. Of1,006 arithmetic cases, one deliberately expects#DE; remaining1,005 verify the entire64KiBDS region plus return/preserved-state properties. These are not original gameplay tests. Static-boundary completeness still requires alternate-entry,alias and caller-context proof; no fully exhaustive function-completion claim.

RAW Ghidra/IDA decompilation remains unavailable. Corrected pseudocode is explicitly hand reconstruction, with address comments. Cross-version signature locators retain UNKNOWN_MATCH where uniqueness/identity is not established; missing signatures never imply ADDED/REMOVED. A complete subsequent pass must recover cross-version CFGs at located functions before semantic classifications.

## Numbered function batch

|No.|Function|Instructions|Decoded bytes|Span bytes|Blocks|Local unresolved jumps|
|---|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(f'|{x["number"]}|{x["function_id"]}|{x["instruction_count"]}|{x["decoded_instruction_bytes"]}|{x["span_bytes"]}|{x["local_block_count"]}|{x["local_unresolved_jumps"]}|'for x in mat)+'''

See BATCH_01_10/ for ten25-section dossiers and per-instructionCSVs. Exact ranges are in FUNCTIONS_01_10_BOUNDARIES.csv; holes include padding/data and are not forcibly assigned as function instructions. CFG continuations aftercalls assume return and remain conditional on each callee's behavior.

Reproduce from the package parent directory: `python N3D_FUNCTION_RESEARCH/PASS002/TOOLS/batch10.py` after installing the pinned Capstone/Unicorn versions fromPASS001. Outputs are deterministic apart from generated filesystem metadata.
'''
(O/'REPORTS/PASS002_FUNCTIONS_01_10.md').write_text(report)
# The cumulative package retains prior original artifacts and adds a separately versioned pass.
(R/'REPORTS/LATEST_PASS.md').write_text(report)
all_ids={x['function_id']for x in csv.DictReader((R/'MASTER_DATABASE/FUNCTION_MASTER.csv').open())};new_ids={d['id']for d in dossiers}-all_ids
summary.update(numbered_function_dossiers=10,batch_instruction_rows=sum(x['instruction_count']for x in mat),new_explicit_function_candidates=sorted(new_ids),cumulative_reference_candidate_ids=1206+len(new_ids),cumulative_isolated_experiments=328+2543,local_semantics_emulation_audited_bodies=5)
save('REPORTS/PASS002_metrics.json',summary)
print('BATCH10',json.dumps(mat,indent=2));print('METRICS',json.dumps(summary,indent=2))
