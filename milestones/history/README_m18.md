# Spyro: Enter the Dragonfly — PSX milestone 0.18

This is an experimental native MIPS-I streamed traversal build, separate from the previous textured farm gameplay and overhead sector viewer. The disc boots `ETD_WALK.EXE`. The two earlier executables are preserved as `ETD_FARM.EXE` and `ETD_CD.EXE` (also supplied separately in the test archive). No source PS2 ISO included.

## Changes
- The native CD/ISO9660 path now supplies terrain and collision data to the third-person gameplay diagnostic. A 16-slot pool (1 MiB) reserves up to eight active 64 KiB blocks and eight staging slots. New selections use full source AABBs within 1,536 units of a 512-unit grid anchor. Reuse active blocks; load and validate only newly needed blocks; publish only after all succeed. Over-capacity regions and failed reads reject the transition rather than dropping blocks silently. Loading is synchronous, not seamless. The CD fault latch still requires reboot after transport faults.
- Original textured, skinned Spyro and nine animation clips reused from earlier milestones. Camera-relative movement, charge, jump and glide logic use source collision-candidate polygons and nearest-height barycentric queries rather than the previous single-sector height grid. Walls, multi-level traversal, full BSP and complete collision behavior remain unresolved. Fire animation may play but damage, Sparx, gems, baskets, sheep and audio are not connected to the new streaming diagnostic; they remain in the fallback farm build.
- Terrain uses flat source texture-average colors; the original texture bank remains on disc, but dynamic VRAM caching is not implemented. The renderer uses original geometry, a local 1,200-unit triangle-AABB visibility cutoff, five-plane clipping, 1,024 depth buckets and a 10,000-packet cap with a dropped-packet counter. No actual console frame rate measured. Dense regions may block traversal; distant scenery and terrain texture detail are absent in this build. Original geometry remains intact on disc.
- Host collision and cache tests traversed 77 cardinal charge steps (2,926 world units), from (36848,-1200) to (33922,-1200), across four distinct resident sets; 8 block reads total including initial 5. Replayed successfully through the register-level CD mock against the authored disc. This is not an emulator playthrough. 124 host tests passed (116 inherited + 8 new). Disc integrity checks regenerated EDC/ECC on all 2,466 sectors.
- Native executable 362,496 bytes; linked allocation from 0x80010000 = 1,652,944 bytes (1.576 MiB), leaving 247,600 bytes before the reserved stack region at 0x801e0000. Static link check only; no measured runtime timing or physical hardware test.

## Build and verify
Requires Python 3, NumPy, Pillow, Clang with MIPS-I, LLD, llvm-objcopy. From project root:
```
python tools/build_m18.py
python tools/disc18.py
python -m unittest discover -s tests -v
python tools/preview_m18.py
```

## Test
Extract BIN/CUE together and boot the CUE in DuckStation with a suitable PS1 BIOS. The new executable requires the matching mounted disc. D-pad or left analog moves, Square charges, Cross jumps/glides, L1/R1 rotates camera, Select recenters, Start resets. Circle plays the fire animation only. The three HUD fields count active blocks, attempted new block reads and dropped GPU packets. Green status indicates successful current load; red indicates a rejected transition. To replicate the host-tested westward route from spawn, hold Left + Square without rotating the camera. Hardware may behave differently. Use ETD_FARM.EXE for previous textured gameplay, or ETD_CD.EXE for the overhead sector diagnostic. The included preview is a host software reconstruction, not an emulator screenshot.

Next: texture-cache upload and material states, asynchronous/prefetch CD reads, stronger collision validation, move previous gameplay systems onto streaming world coordinates, real emulator and hardware testing. No commercial disc authentication data; real unmodified hardware needs an appropriate homebrew loader.
