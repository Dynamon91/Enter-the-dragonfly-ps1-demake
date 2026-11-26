# Spyro: Enter the Dragonfly PSX — milestone 0.22

Native MIPS-I experimental streamed gameplay. Original PS2 ISO not included. Preserves v0.21 gameplay and all prior assets.

## Compact transactional sector cache
- Replaces 16 fixed 64 KiB slots (8 active + 8 staging) with two 536 KiB arenas. Up to 16 active blocks, sized to actual CD-sector-rounded lengths. Retained blocks copied into staging only when the active set changes. Reads validate the existing CRC/metadata checks before publishing the new set. The prior active arena remains unchanged on failure.
- Exhaustive independent bounds scan and host loader checks: 11,515 nonempty 512-unit anchors, 1,021 unique nonempty sets, largest set 16 blocks / 542,720 bytes, maximum 47 texture groups (64 cache slots). All 380 original object coordinates load a complete neighborhood, including all 39 baskets and sheep; 367 of 380 have a collision candidate within 110 units of their source height. All 290 gems, 27 baskets, 12 sheep pass this floor check; 13 other NPC/character positions do not. This is not evidence of connected walkability.
- Previous 77-step route retains its eight block reads and identical collision results. 512,000 bytes copied between arenas over that route; CPU copy latency and actual CD timing unmeasured. Mock CD register transport successfully loads the largest neighborhood. Rollback verified when the third read is corrupted. Prior gameplay state persists across eviction.
- Native linked allocation 1,820,912 bytes, 79,632 bytes before reserved stack region (2 MiB physical RAM). 466,944-byte EXE. 156 regression tests passed (7 new). Host preview shows three formerly blocked locations with staged actor positions. Visible texture/shadow/pose and lighting artifacts remain. No emulator or console verification; CD reads still synchronous, actual speed unknown. Original object rewards and behavior remain provisional.

## Build
Python 3, NumPy, Pillow, Clang MIPS-I, LLD, llvm-objcopy. From project root:
```
python tools/build_m22.py
python tools/disc22.py
python -m unittest discover -s tests -v
python tools/preview_m22.py
```
Prior builds are preserved. Test suite includes inherited artifacts and host tests.

## Test
Extract BIN/CUE together and open CUE in DuckStation. ETD_DENSE.EXE requires the matching disc assets; fallback ETD_HUB.EXE is included. D-pad/left stick move, Square charge, Cross jump/glide, Circle fire, L1/R1 camera, Select recenter, L2 diagnostic damage, Start reset. No Sony authentication data; unmodified physical console requires a compatible homebrew loader.

Next: non-blocking prefetch, reduce copying and verify frame timing; improve collision, add enemies and additional breaths, convert other levels and cutscenes. Overall engineering estimate 55%; not measured playable content.
