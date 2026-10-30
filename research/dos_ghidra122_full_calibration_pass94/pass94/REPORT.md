# Pass94 — full calibration control flow, cached counter and threshold65

Confirmed, High confidence under explicit synthetic sampled-clock fixtures: original full calibration routine, original cached-counter reader and original work-counter increments execute across six distinct supplied DOS EXEs. Labels1.8/1.9 share one identical binary. Render/hardware/setup/flip effects are mocked; this is not real timing measurement or a complete game run.

## Control flow established
The routine performs one warmup work call, snapshots counter, runs10 work calls, snapshots again, computes wrap32(end-start)/10 using unsigned division. If the full32-bit first average is below65, it performs a second snapshot pair around10 work calls, each followed by an additional far helper (flip boundary). Otherwise second measurement is skipped. Average64 enters second branch;65 does not. Average65536 skips it even though low word is0.

The selected measurement is the second average if that branch runs, otherwise the first. Selected0 reaches original fatal callsite before derived-limit arithmetic, with no normal return. The work-count global is reset to0 before this fatal branch as well as on normal paths. Nonzero measurement continues through original ratio/rate/limit arithmetic and normal return. Tests assert all3 limit outputs from93 and normal stack restoration.

Version difference: DOS1.0 starts directly with warmup work;1.1 onward has two preceding setup calls with args1 and0. They are boundary mocks here. Static setup helper checks the same mode global as the counter reader and conditionally calls another far helper; its hardware effect remains Unknown.

## Counter and work evidence
Original counter reader checks a mode byte. In nonzero mode it returns two cached words through DX:AX. In zero mode it calls another original helper and caches returned AX/DX before returning. This pass executes only the nonzero cached branch. The harness writes configured32-bit cache values immediately before each native reader entry; it does not mock its return registers. Consequently units and update source remain Unknown despite the native read path.

Original work helper increments a32-bit global then calls six callees, including a rectangle-related call with geometry globals. The increment and caller cleanup execute; six callees are mocked. It is therefore reasonable to infer a repeated render/work benchmark (Medium), but real frame cost, timer frequency and physical units are not proven. Extra second-loop far helper is mocked and not claimed hardware-verified.

## Verification
240 cases =6 distinct binaries ×5 first averages(0,1,64,65,65536) ×2 second averages(0,100) ×2 start counters(100,fffffff0h) ×2 rate settings(18,70). End counters encode average*10+9, testing unsigned floor and counter wrap. Second snapshots use independent start12345678h. Tests assert2/4 native counter reads,11/21 native work calls,6 mocked subcalls per work,0/10 extra second-loop helper calls, fatal versus normal return, reset work counter and all3 derived limit words. Selected second average is ignored when first>=65.

No whole-function function-byte patch is made. Callsite boundary hooks skip render/setup/extra work and stop before fatal callee; native subtraction/division/branching, stack frames, work increment, cached reads and final arithmetic run unchanged. DS=SS,SPe000. Synthetic source samples are not a model of a particular timer interrupt; hardware IF/timing/parity are outside scope. Runtime EXE hashes, exact calibration instruction lists and per-case counts/results are included.

Fresh Ghidra12.2 exports cover work/counter in each binary and setup helper in1.1 onward. An early exploratory export labelled1.0 repeated work/counter as setup based on call order; final seeds/TSVs correct this, and obsolete C files are removed. Native1.0 call order is preserved in locations.json; helper indices2/3 identify work/counter. Decompiler success is not semantic completeness.

## Reproduce / next
Extract included pass76 and nested baseline58 dependency to baseline58/. Run python scripts/verify_full_calibration.py with Unicorn2.1.4 and included pass94 evidence:40 passed per binary. Ghidra script/seeds reproduce read-only helper exports against pass76/project N3D_Runtime54/inputs.

Unknown: zero-mode counter hardware helper, timer/cache updater and units, setup/flip/render effects, real measurements and ranges, physical keyboard flags and full parity. Next trace the counter's zero-mode helper and cached-global writers to establish its actual time source.
