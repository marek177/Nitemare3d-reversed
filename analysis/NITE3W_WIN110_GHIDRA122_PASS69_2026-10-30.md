# Win110 pass 69 — integrated static initializer

## Finding
Confirmed / High: the complete 1000:45CE initializer executes the metadata-link constructors, installs both exception-object tables, and attempts exit callback registration. 99 original-code microexecutions passed without function stubs or Windows imports.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | 0752 takes return/object at BP+6 and metadata node at BP+8; writes node+0E=old head, then head=node, returns object in AX, RETF 4 | 1000:0752–0766 | High |
| Confirmed | Calls 4410,4530,4570 produce head 0524, links 0532=0514,0522=0500,050E=original head | 45CE and integrated verification | High |
| Confirmed | Final object 41BC stores 1018:48E4; 41C2 stores 1018:48F8 | 4542,4582 and integrated verification | High |
| Confirmed | Registration writes far 1000:45A4 at current exit slot and increments pointer by four unless pointer equals 4688 | 45BE→1008:73CC/73D9, verification | High |
| Confirmed | Full exit table yields AX=FFFF after initializer return, but object and metadata writes still occur | Full-table cases for three initial heads | High |

The metadata getters 453C and 457C return 0514 and 0524 respectively (RETF 2). Earlier preserved annotations identify these as CMemoryException and CNotSupportedException; this pass's new evidence establishes the integrated linking and construction behavior, rather than independently re-proving class-name strings.

## Behavior model
0752 links metadata, not the nearby four-byte instance: 4410 supplies object 41B6/node 0500; 4530 supplies object 41BA/node 0514; 4570 supplies object 41C0/node 0524. The three nodes prepend in that order. 4542/4582 independently construct the corresponding static exception objects. 45BE ignores registration failure and returns normally; 45CE also returns normally.

## Verification and reproduction
Run `python3 pass69/verify_initializer.py` from the unpacked archive. Requires Unicorn 2.1.4. Tests cover every aligned normal exit-pointer state 4608..4688 (33 states), crossed with heads 0000,6000,FFFF. Checks include all four link/head words, both final table pointers, exit-slot content on success, pointer advance or saturation, AX, restored BP and final SP. BP= BEEF, initial SP=D000; final far return leaves SP=D004. Initial heads are synthetic pointer words and are not dereferenced by the tested routine.

The executable hash is checked: 12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. CS is mapped to 2000/3000, DS=1048, SS=4000. Loaded bytes for 036A/4542/4582/45BE are normalized from preserved native Ghidra 12.2 listing, including relocated immediate selectors and callback selector PUSH; internal far-call selectors are remapped to the test code segments. This corrects raw NE relocation-chain words, which cannot be executed as loaded selector values. The script declares all normalization. No Windows APIs or emulated callback bodies are substituted. No fresh Ghidra analysis/database update occurred.

## Unknowns and next test
Actual Windows initialization, callback execution at process exit, and real exception propagation remain untested. The semantic consumers of metadata-node fields other than +0E remain to be traced. Break on accesses to nodes 0500/0514/0524 to distinguish class lookup from exception matching. Full-table failure is a tested synthetic condition, not a claim that ordinary gameplay fills the table.

## Implementation-ready findings
Use node.next at +0E and prepend semantics; preserve the original head word even FFFF. Construct objects before registering cleanup. Registration tests equality with 4688, not a general bounds condition; this pass covers only aligned normal states. Report successful construction separately from successful cleanup registration.

Confidence: High for the isolated original-code initializer under declared relocation normalization; real Win16 lifecycle remains Unknown.
