# Spyro: Enter the Dragonfly PSX — milestone 0.27

Wider Dragonfly Dojo traversal, based on v0.26. Native compilation verified; emulator/hardware execution not verified.

- Repacked existing quantized source records into 441 2048-unit cells, 446 blocks. Canonical comparison proves exact global coordinates, UVs, source IDs, collision flags and materials for all 127733 terrain triangles, 7035 collision candidates and 351 placements before runtime basket-kind adaptation. No geometry removed.
- Terrain candidate radius doubled from 768 to 1536 units. Neighborhood radius 1792, covering a player offset of 256 from the anchor. Maximum 24 blocks and 422 KiB in 3387 distinct nonempty anchor neighborhoods. Shared pool 920 KiB, capacity 28 active blocks. GPU packet capacity increased to 12000. Index size 26776 bytes; native buffer rounded up to 28672. Original texture bank unchanged. The new loader accepts 2048-unit cell index; previous Dojo executables need their original disc data. Hub fallback preserved on disc.
- Linked allocation 1725376 bytes from load; headroom 175168 bytes before 0x801e0000 stack reserve. Savings 120928 bytes versus v0.26. Runtime stack, FPS and disc timing unmeasured.
- All 9 milestone tests passed, including exact repack equivalence, native-cache exhaustive anchor neighborhoods, 61 charge steps across 6 resident sets using simulated CD registers, object coverage, persistent gems and baskets, texture cache and disc-sector integrity. Inherited earlier milestone tests archived but not all rerun.
- Preview is host software rendering at the same route positions as v0.26, with staged companion position. Wider scenery visible, but distant cutoffs, lack of skybox, provisional lighting and original blend rules remain. Not emulator output.

## Rebuild
```
python tools/repack27.py
python tools/build_m27.py
python -m unittest discover -s tests -p test_m27.py -v
python tools/preview_m27.py
```
Requires Python, NumPy, Pillow, Clang MIPS-I, LLD and llvm-objcopy. No original ISO needed for this repack because the recovered records are already in the project. Disc boots ETD_WIDE.EXE; ETD_POOL.EXE retained as hub fallback (no in-game launcher or portals). Use CUE with BIN. Previous v0.26 disc is a separate archive and its executable is not compatible with the new Dojo index.

Controls unchanged from v0.26. CD reads remain synchronous; 192/193 gems and 45/45 selected baskets have nearby collision candidates. Enemy AI, skybox, portals, other levels, audio and full hardware testing pending. Estimated engineering progress 61%, not percent of original adventure playable.
