# Spyro: Enter the Dragonfly — PSX milestone 0.20

Native MIPS-I experimental streamed gameplay. This milestone restores source-positioned gems, Sparx and original pickup SFX in the streamed traversal, and corrects opaque hay-overlay rectangles using selective binary alpha. No original PS2 ISO is included.

## Changes
- 290 direct gem placement IDs and denominations validated against all sector object records (773 total value). Persistent collected-state array is independent of cache slots. Only resident gems render or participate in collection. Pickup path checks use the existing collision candidates; collection and Sparx flight are reconstructed behaviors, not the original AI. No memory-card persistence yet. Start resets state on successful respawn. Existing farm-only basket, sheep, health and fire damage remain separate fallback features.
- Original gem and Sparx meshes from v0.12, with provisional flat colors and wing animation. Counter at upper right. Both original gem sound samples from v0.13 are integrated via native SPU driver; audible playback not verified.
- Three source texture groups (84 onlyhay, 292 yellow_T, 359 sdgrass_T) converted to masked RGB555 CLUT: palette alpha below 32 becomes zero (transparent); other used entries retain original RGB555 values. Original indices unchanged, 138 other textures unchanged, updated CRCs validated. This is an approximation, not a full PS2 alpha-blending implementation. Native texture primitive uses standard opaque textured triangle command, which skips zero CLUT texels. Large dark rectangles no longer visible in the three tested host frames; residual aliased straw and other blending/lighting defects remain.
- Host route: 77 charge steps, 4 resident configurations, 8 geometry reads. Original green gem collected at step 7, score 2 retained on reverse traversal. Separate stationary Sparx assist test passes. All 290 unique IDs checked; direct collection of every gem in actual gameplay not yet verified.
- Linked allocation 1,709,728 bytes (~1.63 MiB) from 0x80010000; 190,816 bytes (186.3 KiB) before reserved stack. Native executable 405,504 bytes. 140 regression tests pass; no emulator or physical-console verification.

## Rebuild
Requires Python 3, NumPy, Pillow, Clang MIPS-I, LLD, llvm-objcopy. From project root:
```
# Optional: reproduce selective mask bank from your original ISO
python tools/material20.py /path/to/source.iso
python tools/build_m20.py
python tools/disc20.py
python -m unittest discover -s tests -v
python tools/preview_m20.py
```

## Test
Extract BIN/CUE together and open the CUE in DuckStation. ETD_GEM.EXE requires matching disc-resident data. Hold Left + Square from spawn for the host-tested route. D-pad/left analog moves, Square charges, Cross jumps/glides, L1/R1 rotates camera, Select recenters, Start resets. Circle is animation only in this streaming prototype. Top-left diagnostic counters retained, score at top right. Older native executables remain on disc; ETD_TEX.EXE uses updated texture bank on this disc. The prior complete disc remains separate. No Sony disc authentication data; physical unmodified hardware requires appropriate homebrew loader.

Remaining: actual emulator boot/playback and performance, asynchronous CD streaming, original blended material/lighting, terrain coverage, enemies, basket and sheep integrations, breath attacks, full levels, cutscenes, save system. Preview is a host reconstruction, not emulator screenshot.
