# Nitemare 3D RE MAX v0.72 — first DOS2 DEMO RNG actor/tick identity

**Date:** 19 October 2026

A controlled original DOS2 DEMO startup captures the first RNG call after the explicit seed=1 reset together with the live actor record and global update counter.

At RNG entry:
- CS:IP = 17DE:01A0;
- DS = 2F95;
- ES = 2A21;
- SI = 2A92;
- global update counter DS:[1738] = 58;
- adjacent counter DS:[173C] = 57.

The live 26-byte actor list and static scheduler math identify SI=2A92 as zero-based actor record index 42 in the 50-record table. Its state is 3. The record points to descriptor index 258 through the known 28-byte descriptor layout.

Static/runtime call chain:
- outer 26-byte scheduler at 0CEB:12B6;
- state dispatcher 0CEB:0D80;
- state-3 branch 0CEB:0E64;
- actor behavior 0CEB:07D2;
- RNG callsite 0CEB:0A36 -> 17DE:01A0.

The first RNG call therefore has a concrete actor identity and occurs with the global update counter at 58. This does **not** prove that counter 58 equals a particular DEMO record index; the first six DEMO time values are 8,23,27,43,49,67 and the player cursor mapping remains open.

This v0.72 result sharpens the first-draw consumer context already covered by the broader RNG ledgers; it does not replace the reproducibility proof in v0.63.
