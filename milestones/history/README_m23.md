# Spyro: Enter the Dragonfly PSX — milestone 0.23

Native MIPS-I experimental streamed gameplay, continuing v0.22. Original PS2 ISO not included. The full v0.22 executable is included on the disc as a fallback.

## Cooperative sector lookahead
- Predicts eight movement updates ahead. Each movement update stages at most one block (one retained-block copy or one CD read). The actual next player anchor takes priority when crossing. Commit only when the complete candidate set has validated. Cancel on changes in predicted target; an incomplete or invalid staging bank never overwrites active sector data.
- Startup/reset remain blocking. Individual CD block reads (up to 32 sectors) and texture refresh remain synchronous. No claim of real-time nonblocking I/O, zero loading latency or measured FPS. If staging is incomplete at a boundary, movement is held until ready. On the established 77-step route, no holds and no sector reads on the three resident-set changes; nine total block reads including five at startup, versus eight previously, because the route ends during speculative prefetch. Retained data copied on committed transitions: 512,000 bytes (unchanged). Tests use host movement scheduling, not emulated optical timing.
- Sector CRC-32 uses a 16-entry nibble lookup table (two lookups per byte) rather than eight bit steps. Validated identical metadata for all 174 source blocks and rejection of one-byte corruption in each block. No hardware timing measurement.
- All 1,021 distinct neighborhood sets and all 380 original object positions remain loadable. All original gem, basket and sheep placements retain candidate floor coverage; 13 other character locations remain unresolved. Cache supports 16 active blocks, 536 KiB per arena. Texture mappings and gameplay assets unchanged.
- Native linked RAM from load: 1,822,992 bytes; 77,552 bytes before reserved stack region. 468,992-byte EXE. 164 host regression tests passed, including eight new tests. CD register mock verifies staged readback, atomic commit, cancellation and rejection of corruption. Emulator and real console execution still unverified.

## Build and reproduce
Python 3, NumPy, Pillow, Clang MIPS-I, LLD, llvm-objcopy. From project root:
```
python tools/build_m23.py
python tools/disc23.py
python -m unittest discover -s tests -v
python tools/preview_m23.py
```
The report and host trace are in `build_m23/play/`. Preview contains software renders of extracted assets at recorded test positions, not actual emulated frames. Known graphical artifacts and provisional object behavior remain.

## Test disc
Extract BIN/CUE together, open CUE in DuckStation. Disc boots `ETD_PREF.EXE`; `ETD_DENSE.EXE` is the preserved v0.22 fallback. D-pad/left stick move, Square charge, Cross jump/glide, Circle fire, L1/R1 camera, Select recenter, L2 diagnostic damage, Start reset. A small blue progress bar appears when sector preparation is active. No Sony authentication data; physical stock console requires a compatible homebrew loader.

Next: true nonblocking CD transport and safe texture lookahead, collision/lighting, additional breath abilities and Dragonfly Dojo. Overall project estimate 56% (engineering estimate, not fraction of adventure playable).
