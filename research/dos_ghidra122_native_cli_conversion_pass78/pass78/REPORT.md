# Pass 78 — native numeric conversion and CLI failure-count policies

## Finding
Confirmed across six distinct supplied DOS binaries: original CRT sscanf returns different counts for matching failure and EOF, and the parser handles those counts differently by option. Native conversion now executes rather than being replaced. Supplied1.8/1.9 are identical.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | `%d` bad text returns0 without writing | Original CRT execution | High |
| Confirmed | Empty/whitespace text and isolated+ returnffffh for tested `%d` | Native fixtures, preserved destination | High |
| Confirmed | c,d,e,f ignore conversion count | Original parser+CRT paths | High |
| Confirmed | l rejects only0; EOFffffh passes | Actual parser control flow and tail argument | High |
| Confirmed | q requires exactly1 for each conversion | First/second failure fixtures | High |
| Confirmed | Tested16-bit conversions65536 decimal /10000 hex store0 | Original CRT and destination bytes | High for tested values |
| Unknown | All overflow/malformed text behavior and complete CRT initialization | Finite fixture set; explicit stack precondition | Not generalized |

## Native conversion observations
| Format/input | AX | Written word |
|---|---|---|
| %d /123 |1|007b|
| %d /-123 |1|ff85|
| %d /space+42tail |1|002a|
| %d /0x10 |1|0000|
| %d /bad |0|unchanged|
| %d /empty, spaces, or+ |ffff|unchanged|
| %d /32768 |1|8000|
| %d /65535 |1|ffff|
| %d /65536 |1|0000|
| %d /-32769 |1|7fff|
| %x /ff,0x1234,ffff,10000,-1,bad |1|00ff,1234,ffff,0000,ffff,0bad respectively|
| %x /z |0|unchanged|
| %x /empty |ffff|unchanged|

These values are observed CRT behavior, not an assumption that all arithmetic overflow follows portable modern C semantics. Adjacent sentinel bytes remain intact in direct fixtures.

## Parser behavior model
c,d,e,f consume one following argv entry and ignore AX from numeric conversion. Their destination remains unchanged on no assignment, and parsing continues. e writes the low word of the local pair, while l writes its high word. l also consumes one entry, but calls usage only when AX==0. Consequently EOFffffh with no assignment retains its initial high word1 and continues to the final call. This is an input-parsing distinction, not evidence of memory corruption.

From DOS1.1 onward q converts its first value with%x, requires AX==1, then consumes a second value with%d and again requires AX==1. On first failure no second conversion runs. On second failure the first successful destination value remains; no rollback occurs in the observed branch. The word `bad` is a valid hexadecimal number0badh and is accepted for q's first argument. DOS1.0 has no q conversion path.

## Verification
120 direct CRT cases pass (20 per binary).215 original-parser/native-CRT cases pass (30 inDOS1.0,37 in each other binary): c,d,e,f,l × six inputs plus seven q pairs where present. Every conversion's format, return AX, destination word and preserved-value behavior are checked. l usage-vs-success and q first/second failure are asserted; local-pair forwarding is checked for e/l. Original sscanf wrapper, scan core and internal helpers execute unchanged. There are no mocked conversion calls or DOS interrupts in successful tests.

Direct CRT tests supply DS=SS, SPe000h and stack-limit global8000h. Initial probing without this valid test-stack limit entered CRT stack-overflow handling; the explicit fixture is therefore essential. This is not full startup initialization. Parser tests still mock startup/final helpers and stop at the usage boundary, preserving focus on conversion policy. No actual process exit/OS, native configuration startup or gameplay is executed.

## Ghidra evidence
Fresh Ghidra12.2 exports successfully decompile all six native wrappers. Entries: DOS10 219b:28e0; DOS11 21bc:27e4; DOS12 21c2:27e4; DOS15 21c7:27e8; DOS17 21d1:27e4; DOS18 21ea:27e8. Per-build scan-core/stack-guard entries, guard instructions and initialized limit addresses are in native_scan_tests.json. Recovered parser source comes from the pass76 repaired project. No native project mutation was needed here.

## Unknowns and next test
Native%s path handling, missing argv entries, unusual prefixes/large numeric overflow and order-sensitive option combinations remain. Trace final local-pair consumers to assign precise gameplay meanings rather than inferring from option letters. Full parser semantics and complete renderer/runtime parity remain open. Confidence High for tested native conversions and parser return-count policies; incomplete beyond stated input/domain/setup conditions.
