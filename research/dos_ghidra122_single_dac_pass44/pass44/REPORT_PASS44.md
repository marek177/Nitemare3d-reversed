# Single-entry DAC writer — pass44

Confirmed, High confidence:150 complete original-code tests across six distinct DOS images recover the single-entry palette writer (V1.9 1156:0150–016c). Supplied1.8/1.9 share one image. Exact bodies, entries and hashes in evidence/single.json.

Far-call args are four16-bit words: index,R,G,B. Routine emits OUT3c8 byte(index&255), then three OUT3c9 byte(component&255), RGB order. It performs no software6-bit clamp:256 becomes0,65535 becomes255 in emitted data. Actual DAC hardware interpretation of these bytes is not tested.

Confirmed, High confidence: source palette,16-entry nearest-color lookup and dirty flag remain unchanged. Tests initialize these three regions to a5 and compare every byte afterward. Thus hardware-port updates do not automatically synchronize the software palette/cache through this local routine. Full-game callers may synchronize separately; their behavior remains Unknown.

Run `/usr/bin/python3 scripts/verify_dac_single.py` with Unicorn2.x. Six images × indices0/1/255/256/65535 × five RGB triples including6-bit values and high-byte probes=150. No callee mocks. Exact four-event port trace, far return, stack and DS verified. Ghidra12.2 preserved instruction export supplies locations; no project database edits. No real palette asset, VGA device, DAC scanout or gameplay parity claim.

Implementation-ready: preserve byte truncation,RGB ordering and separation of software palette/cache state from DAC output. Do not introduce automatic cache invalidation in a faithful local reconstruction.

Next test: trace writer callers and determine which perform independent software synchronization; test actual VGA initialization before treating port traces as full hardware parity. Overall confidence High for local routine, Unknown for complete palette lifecycle.
