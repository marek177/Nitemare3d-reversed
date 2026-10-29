# Texture edge correction and mask — pass36

## Finding
33,600 original second-helper executions match an independent branch model. This helper applies orientation-dependent edge correction and then bitwise AND with width-1. Both formerly mocked helpers are now separately verified; their unmocked integration remains next.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Inputs are near object record, screen x, signed candidate, width; return AX | V1.9 1201:02ba–040d, original execution and caller pushes | High |
| Confirmed | Edge flags use signed wrapped distance<8 from record+14/+18 | V1.9 02c6–02ec | High |
| Confirmed | Object byte+5 bit08 bypasses corrections | V1.9 02f9–02fd; flags0/8 tests | High |
| Confirmed | Class2, orientations0/3 have special edge behavior | V1.9 031a–033a and distinct paths | High |
| Confirmed | Final result is (width-1)&candidate, not general modulo | V1.9 0404–0408; widths0/1/63/64/65 | High |
| Unknown | Valid record span ranges and width values in full gameplay | Synthetic record span16 only | Unresolved |

## Behavior model
Analytical object fields: flags byte+5, class byte+6, orientation byte+7; endpoints word+0c/+10 for orientations0/1, or +0e/+12 otherwise; screen edges word+14/+18. Endpoint difference gives signed span. Names reflect local use, not complete object-structure recovery.

Let L/R be screen edges, x current screen column, d signed candidate, S signed span. leftNear=s16(x-L)<8; rightNear=s16(R-x)<8. Corrections run only when either near flag is true and flags&8 is clear. Unknown orientation values follow raw candidate path.

| Path | First-priority correction | Second correction |
|---|---|---|
| Normal orientations0/2 | if(rightNear and d>=0) or x==R: d=-1 | else if(leftNear and -S>d) or x==L: d=-S |
| Normal orientations1/3 | if(leftNear and d<0) or x==L: d=0 | else if(rightNear and S<=d) or x==R: d=S-1 |
| Class2 orientation0 | if(rightNear and d<0) or x==R: d=0 | else if(leftNear and S<=d) or x==L: d=S-1 |
| Class2 orientation3 | if(leftNear and d>=0) or x==L: d=-1 | else if(rightNear and -S>d) or x==R: d=-S |

Otherwise retain d. Return ((width-1)&0xffff)&(d&0xffff). Signed comparisons and 16-bit subtraction/negation wrapping are material. Table tested with S16; extreme/negative spans are not dynamically verified. Width64 yields usual low6-bit wrapping. Width0 yields maskffff; width1 yields0; non-power-of-two widths retain only mask bits, not remainder semantics.

## Verification
`/usr/bin/python3 scripts/verify_texture_edge.py` with Unicorn2.x: six images × class2/3 × orientations0..4 × flags0/8 × eight x positions around L100,R120 × seven candidates around -16/0/16 × widths0/1/63/64/65 =33,600. Complete original helper executes without mocks and no dependencies. Independent branch model checks AX; far return, stack and restored DS also checked. Both object endpoint axes have span16 here, so endpoint-axis selection is statically supported but not independently distinguished by these runtime values.

Input hashes and complete bodies in edge.json. No full-game reachability, pixel or VGA/DAC claim in this helper pass. Preserved Ghidra12.2 exports supply locations; no project database edits. Supplied1.8/1.9 EXEs are identical.

## Implementation-ready findings
Preserve class/orientation-specific edge correction, bit08 bypass, signed near tests and final bit mask. Avoid replacing mask with generic modulo. Combine with pass35 signed projection before restoring the complete caller pipeline.

## Unknowns and next test
Run caller inner loop with both helpers unmocked and distinguish endpoint-axis spans. Verify valid record inputs and projected scale bounds from outer renderer. Negative/extreme spans, framebuffer/DAC and menu limits remain open.

## Confidence
High for tested positive-span helper behavior; general object semantics and complete renderer parity remain unresolved.
