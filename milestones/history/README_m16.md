# Spyro: Enter the Dragonfly — PSX milestone 0.16

Continuation of v0.15. Native PS1 farm prototype plus the first disc-resident full Dragon Realms asset pack. Not a full game; the original PS2 ISO is not included.

## New in 0.16
- All 75,653 recovered source render triangles from 504 meshes, 6,195 original collision polygon-derived triangle candidates, and 380 unique character placements are serialized into 174 bounded blocks in 166 spatial cells. The placements are 290 gems, 27 baskets, 12 sheep and 51 other characters. Original source IDs and offsets are preserved. Position rounding is at most 0.5 world unit; UV Q10 rounding at most 1/2048. No source triangles are dropped or duplicated. Centroid ownership and full per-block AABBs are separate, so future visibility must use full bounds, not just the owning cell. These are source triangles, not yet split/optimized final GPU triangles. Collision candidates are from the existing incomplete BSP heuristic, not verified complete collision.
- 208 regional material entries: 74,075 triangles have a unique source base texture candidate from the existing filename-hash registry. Four mountain materials (1,578 triangles) are still unresolved. The 141 corresponding texture groups are converted to a disc-resident 64x64 8-bit RGB555 CLUT bank, currently opaque; alpha and multi-layer blending still need decoding. No runtime VRAM allocator is added yet.
- `HUBSECT.DAT`, `HUBSECT.IDX`, `HUBTEX.DAT`, and `HUBTEX.IDX` are included on the BIN/CUE image, and verified via ISO filesystem readback. `src/sector16.c` provides a bounded, CRC-checked, callback-based sector loader (MIPS-I object and host shared library built). Host tests read all 174 blocks and reject corrupt payloads, bad directory entries, insufficient buffers, transport failures, and invalid IDs. The loader is not yet linked into the gameplay runtime; physical CD transport, residency, collision switching, and GPU texture uploads are future work. A failed read can overwrite staging storage, but output metadata is not committed. No active resident block should alias the staging buffer during a read.
- The existing renderer now uses per-face compact UVs and one-byte material IDs rather than duplicating texture-page, CLUT and texture-window state for each face. All 19,892 per-face state/UV words reconstruct identically. Native linked RAM from load is 1,775,424 bytes (44,448 bytes lower than v0.15), leaving 125,120 bytes before the reserved stack; enough for one 64 KiB staging slot and 10,456-byte index, subject to future integration overhead. No changes to the existing farm scene, animation, gameplay, audio or source-derived collision. Native executable 651,264 bytes. New disc has 2,279 sectors. 110 host regression tests passed. No emulator execution, real hardware tests, FPS or audible playback verification.

## Build
Requires Python 3, NumPy, Pillow, Clang MIPS-I, LLD, llvm-objcopy. All source-derived exports are included, except the source disc itself. Texture bank rebuild requires the user's PS2 ISO.
```
python tools/sectors16.py assets_m16
# Optional: regenerate texture bank from the user's original disc:
python tools/texture16.py /path/to/source.iso assets_m16
python tools/build_m16.py build_m16/play
python tools/disc16.py build_m16/play
python tools/preview_m16.py
python -m unittest discover -s tests -v
```
## Controls and testing
Extract the BIN and CUE together and open `ETD_PSX_M16.cue` in DuckStation, or load `ETD_SECT.EXE`. Controls are unchanged from v0.15: D-pad/left stick move; Cross jump/glide; Square charge; Circle fire; L1/R1 camera; Select recenter; Triangle toggles legacy fire targets; Start resets; R2 toggles diagnostic sheep; L2 simulates damage. Only the previously loaded farm prototype is available in the runtime. The new disc files do not extend the playable world yet. Real unmodified consoles require a suitable homebrew loader. `sector_atlas.png` is a source-data atlas, not an emulator screenshot.

Next: connect a native CD-ROM read transport, integrate staging/residency and texture uploads, and test an adjacent sector including original sheep placements; then recover the remaining mountain material bindings, fix blending and expand to the rest of the adventure.
