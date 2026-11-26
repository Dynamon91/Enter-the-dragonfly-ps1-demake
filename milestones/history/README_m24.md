# Spyro: Enter the Dragonfly PSX — milestone 0.24

Native MIPS-I experimental streamed gameplay continuing v0.23. Original PS2 ISO not included. v0.23 is retained as a fallback executable on the disc.

## Shared sector residency
- Replaces the two fixed 536 KiB banks with a shared 1,072 KiB pool. Up to 16 active blocks and 16 staging slots; 2 KiB allocation granularity. Active slots remain pinned; retained blocks are referenced by address, not copied. A candidate is published only after every new block passes existing index, bounds and CRC checks. Cancel/failure releases only unpinned allocations. If the pool becomes fragmented, active extents are packed down in address order with overlap-safe forward copies; active content remains identical, although its address can change during this fallback.
- The established 77-step charge route still requires nine block reads including startup and one speculative block. Zero held updates, zero retained bytes copied, zero compactions (v0.23 copied 512,000 bytes). The test of retained addresses used actual successive neighborhoods on that route. Another 1,500 deterministic randomized transitions over original object positions produced zero compactions; a synthetic fragmented layout separately verifies fallback compaction, contents and successful reallocation. All 1,021 distinct nonempty neighborhoods and all 380 source placements still load. These are host tests, not optical timing or emulator tests.
- 175 regression tests passed, including 11 new tests. Native executable size 471,040 bytes; linked main RAM from load address 1,825,104 bytes (1.741 MiB); 75,440 bytes before reserved stack region. No geometry, texture, collision or gameplay assets changed. CD and texture reads are synchronous; compaction may cause a stall in fragmented cases. No measured FPS or real hardware execution.

## Reproduce
Python 3, NumPy, Pillow, Clang MIPS-I, LLD, llvm-objcopy.
```
python tools/build_m24.py
python tools/disc24.py
python -m unittest discover -s tests -v
python tools/preview_m24.py
```
Reports in build_m24/play: report.json, pool_report.json, test_results.txt, pool_preview.png. The preview renders source-derived terrain and animation at recorded route positions, not emulated frames.

## Test disc
Extract BIN/CUE together and open the CUE in DuckStation. Boots ETD_POOL.EXE; ETD_PREF.EXE is the v0.23 fallback. D-pad/left stick move, Square charge, Cross jump/glide, Circle fire, L1/R1 camera, Select recenter, L2 diagnostic damage, Start reset. Direct executable needs disc assets. No authentication data; stock hardware requires an appropriate homebrew loader. Emulator execution remains unverified.

## Next priorities
Nonblocking CD reads, graphics and collision fixes, more breath abilities, Dragonfly Dojo conversion. Overall engineering estimate 57%, not a percentage of the original adventure playable. No new level or gameplay feature was added in this revision.
