# Recovered Nite3W core — 2026-09-25

This directory contains a conservative C++17 transcription of currently recovered Nitemare 3D / Nite3W behavior.

Implemented:
- runtime capacities and record strides;
- partial byte-accurate GUARD, OBJECT, projectile and Win16 DEMO records;
- Win16/DOS LCG;
- corrected Win16 score table;
- recovered damage formula and class/weapon transforms;
- fire damage;
- GUARD state/strategy enums and conservative confirmed transitions;
- event flags 51A4..51AB;
- complete current MAP.1–3 GUARD placement counts E1M1–E3M10 + E1M11 demo;
- special-object categories.

Important: inferred and unknown behavior is not silently converted into fake engine logic. In particular the exact maximum achievable score, full renderer parity, projectile ownership/friendly fire, all animation tokens and complete wall/use side effects remain open.

Known placement totals:
- Episode 1: 375
- Episode 2: 501
- Episode 3: 390
- playable total: 1266
- E1M11 demo: +50

One-award-per-placement analytical score baseline:
- signed: 145775
- excluding Penelope penalties: 147775

These are analytical baselines, not the true maximum score, because score is reached through the damage path.
