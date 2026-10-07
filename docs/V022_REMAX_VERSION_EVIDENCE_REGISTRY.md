# v0.22 RE MAX — version profiles and evidence registry

v0.22 adds a machine-readable boundary between executable identity, reverse-engineering evidence and implementation claims.

## Version profiles

The registry has slots for:

- DOS v1.0
- DOS v1.2
- DOS v1.9
- DOS v2.0
- analyzed Win16 build

Only DOS v2.0 currently has a confirmed executable fingerprint in the registry:

- unpacked size: 171,360 bytes
- SHA-256: `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`

The other profiles intentionally have no invented size/hash. They remain OPEN until independently fingerprinted.

## Evidence registry

Each fact now carries:

- fact ID;
- build ID;
- confidence: CONFIRMED / STRONG / OPEN;
- evidence source;
- short evidence reference;
- closure experiment.

Examples:

- player X/Y: CONFIRMED, DOS v2.0, static disassembly;
- GUARD pool/stride: STRONG, requires runtime iteration proof;
- exact FAST/MAIN interleaving: OPEN;
- `0800:0E50` OBJECT-runtime identity: OPEN;
- projectile `+18/+19` stale-cache behavior: STRONG;
- build-specific address portability rule: CONFIRMED.

## Promotion rule

The helper `mayPromoteToImplementation()` returns true only for CONFIRMED facts.

This is intended to prevent future code from silently turning a hypothesis into a reconstructed gameplay rule.

## Why this matters

Several older addresses were correct only for another build/context. A version profile plus evidence record makes the required sequence explicit:

1. fingerprint executable;
2. select build profile;
3. use only facts scoped to that build;
4. keep STRONG/OPEN items behind runtime verification;
5. promote only after the closure experiment succeeds.

The next high-value work is filling the missing DOS v1.0/v1.2/v1.9 and Win16 fingerprints from known binaries, then attaching per-build symbol maps.
