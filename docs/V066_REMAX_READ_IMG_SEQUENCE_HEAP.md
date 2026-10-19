# Nitemare 3D RE MAX v0.66 — DOS2 Read_img_sequence near-heap closure

**Date:** 19 October 2026

Static analysis of the SHA-pinned DOS2 unpacked executable closes the local failure branch behind the diagnostic:

`Insufficient memory (near heap), Read_img_sequence()`.

The relevant loader:
- seeks to `0x800 + 0x5A * sequence_index`;
- reads one 90-byte descriptor;
- reads `N = descriptor[2]`;
- computes `10*N` with 16-bit arithmetic;
- calls the near-heap allocator;
- enters the named fatal diagnostic if the returned pointer is zero.

This separates the failing allocation from nearby unrelated 1024-byte and 90-byte allocations in `Read_images()`.

For IMG.1, the audited layout is:
- 512 dword offsets at 0x0000..0x07FF;
- 512 descriptors × 90 bytes at 0x0800..0xBBFF;
- first image data at 0xBC00;
- descriptor[2] values 1..54, so this specific allocation is 10..540 bytes.

A controlled E1M1 map experiment shows that adding four distinct guard classes together (Skeleton, Mrs. H., Zelda, Vampira) reproduces the exact near-heap failure, while removing any one of the required class combination loads successfully in the tested subspace. This strongly points to pressure from unique sprite-class resources rather than a geographic coordinate or raw Skeleton count.

Still open: the exact final image/sequence ID that fails in the live allocation, near-heap free-list state, fragmentation versus segment exhaustion, and a targeted instruction trace at the failing malloc.
