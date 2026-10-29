# Enabled resource/playback dispatcher — pass47

1,740 original-dispatcher tests across six distinct DOS images recover priority arbitration,resource lookup/fallback and two backend paths. Backend and resource dependencies are mocked; no audio device or sample output executes. Supplied1.8/1.9 share one image.

Confirmed (High): V1.9 dispatcher1c27:03da–04cc first checks enable byteDS414e and nonzero word in6-byte resource entry DS3f64+6*id. It selects backend using DS3cc7, queries busy, and rejects only if busy AND unsigned current-priority byteDS17e4>low8(incoming priority). Equal priorities are accepted; an idle channel accepts even lower priority. Accepted busy paths call stop before lookup.

Confirmed (High): accepted path stores low8 incoming priority, queries resource cache by id, calls loader if returned DX:AX is zero, and passes resulting far pointer to selected playback backend. No loaded-pointer null validation is established here because loader mock returns nonzero. Failures inside dependencies remain unknown.

Confirmed (High for argument construction): backendA scales volume byteDS414b by15/100 with integer truncation, without clamping input to100. Pan argument1 sets first component low byte0; pan2 sets second component0; pan0 leaves both scaled. Input255 yields38. The first component is formed with MOV AL and its pushed word can retain a nonzero AH (notably pan1). Tests compare low-byte components and preserve raw pushed words in raw_trace. Backend acceptance/interpretation of high bits is not verified. BackendB bypasses this volume call.

The animation companion's dword20000 is therefore two argument words: pan0 and priority2, following id42. Sound/playback naming is strongly supported by dispatch structure and volume configuration, but exact sample identity and backend audio result remain unresolved.

Run `/usr/bin/python3 scripts/verify_sound_dispatch.py` with Unicorn2.x. Per image:288 active matrix cases (backend2 ×busy2 ×four priority pairs ×pan3 ×volume3 ×cache2),plus two disabled/missing-resource gates=290; six images=1,740. Inject busy/stop/cache/load/volume/play dependencies; execute original control flow, stack cleanup and arithmetic. Checks ordered dependency args, priority update, far return, SP and DS. Exact bodies, hashes, raw/normalized argument traces in dispatch.json. Ghidra12.2 preserved export used; no project database edits.

Implementation-ready: retain strict unsigned priority comparison, busy-only rejection, stop/cache/load order and backend-specific volume path. Do not silently clamp volume or assume every lower-priority request is rejected. Keep raw stack words until backend ABI is verified.

Unknown/next: recover resource cache/loader and playback backend ABI, especially volume high-byte interpretation. Trace actual id42 data and invocation cadence before assigning a concrete effect name. No complete audio, timing,VGA/DAC or gameplay parity claim. Overall confidence High for tested dispatcher behavior, unresolved for dependencies/hardware.
