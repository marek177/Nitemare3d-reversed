# Nitemare 3D RE MAX v0.47 — WORX natural DMA start / automatic stop

Date: 18 October 2026.

## Evidence boundary

This pass records one new original DOSBox-X runtime closure from the tested DOS build SHA-256 32029326da3e9e356f5d17ca98e420dee178486f1384af8e7ccc662671c12511. No runtime memory/register patch was used to force the playback-active flag. The triggering gameplay event is naturally reached, but this capture does not prove that the sample was specifically a weapon shot.

## Natural DMA start

The runtime reached WORX code at 1DB6:48FE with CS:4740 already set to 1 during the hardware-transfer setup.

A 65,536-instruction trace confirms completion of the start sequence through 48FE..495D, including:
- Sound Blaster DSP port 022Ch;
- DMA controller ports 0Ch, 0Bh, 02h, 83h and 03h;
- DMA channel unmask through port 0Ah with AL=01h;
- DMA mode 59h;
- DMA address low/high DB6Eh;
- page 01h;
- count 0FFFh.

This proves that the playback-active bit is associated with an actually executed DMA/DSP transfer setup, not merely the configuration toggle.

## Natural automatic stop

After the start trace, the original runtime later stopped at 1DB6:5F59 with CS:4740 still equal to 1.

The automatic-stop trace then observed:
- 5F59 clears CS:4740;
- DSP command D0h is written through port 022Ch;
- DMA mask port 0Ah receives 05h;
- a later call to the explicit stop helper at 4741 occurs only after the active flag has already been cleared.

The post-stop memory snapshot confirms CS:4740=0.

Therefore the captured stop is the automatic path at 5F59, not an active shutdown stop at 4741.

## What this closes

For the tested build and run, natural runtime now proves:
- a real DMA/DSP output-start sequence;
- active flag 0 -> 1 as part of that playback setup;
- hardware DMA unmasking;
- later automatic D0h plus DMA-mask stop;
- active flag 1 -> 0 before the later explicit stop helper.

## What remains open

- entering the central game shutdown while CS:4740 bit0 is still 1;
- runtime execution of the active branch inside the explicit 4741 stop helper;
- exact identity of the gameplay event that triggered this sample;
- audible PCM waveform parity because the emulator configuration still used nosound=true;
- exact DSP/DMA timing and interrupt latency;
- cross-build and Win16 behavior.

This is a bounded original-runtime closure, not complete audio parity.
