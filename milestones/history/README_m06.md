# Spyro: Enter the Dragonfly — PSX development milestone 0.6

This is a native PS1 diagnostic, not a finished game. Derived from the user-supplied Definitive Edition 1.2.1 disc. Previous milestone files are retained. No original full ISO is included.

## What changed
- Indexed all 540 texture groups against the original texture directory; extracted named material references. 17 source texture candidates match dimension/payload metadata, but the filename/hash relationship is unresolved, so no material binding is claimed exact.
- Recovered 3,776 heuristic polygon candidates (6,195 fan triangles) from the source collisionShape record 1304. The BSP hierarchy and flags are not decoded; polygon completeness and semantics are not guaranteed.
- Source farm region: 1,572 unique vertices, 2,211 triangles after UV splitting. PS1 8-bit CLUT textures (17 groups, 78,336 bytes). Texture window, near clipping and UV interpolation implemented.
- 229 source collision candidate triangles overlap test sector; 1,034 candidate floor samples; 246 agree with old visual floor within 120 units; 19 blocked near walls; 227 admitted. Median agreement before wall exclusion ~3 source units. Sparse grid intentionally limits movement. Lower spawn chosen after host render exposed elevated structure spawn. Camera occlusion, missing terrain and provisional textures remain visible; no original animation, BSP traversal or streaming yet.
- Fixed-point movement logic updated for interpolated floor, midpoint checking, and no traversal into unvalidated cells.

## Reproduce
Python 3 + numpy + Pillow; clang with MIPS target, ld.lld and llvm-objcopy. From the project root:

```
python tools/build_m06.py /path/to/source.iso build_m06/play
python tools/preview_m06.py build_m06/play
python -m unittest discover -s tests -v
```

To regenerate the collision cache, remove `build_m06/collision/collision.npz` before building. The existing hub asset cache is retained. See tools/hub_collision.py and tools/build_m06.py for parsing and validation details. The previous project instructions are in README_m05.md.

## Test on PS1 emulator
Load `build_m06/play/ETD_FARM.EXE` directly in DuckStation; D-pad/left stick move, Cross jump/glide, Square charge, L1/R1 rotate camera, Select recenter, Start reset. Emulator and physical hardware execution are unverified. Native build and host tests passed. No BIN/CUE generated. Do not treat host preview as an emulator screenshot or accurate PS2 material match.

Reports: `build_m06/play/report.json`, `texture_registry.json`, `build_m06/collision/collision_report.json`, `build_m06/test_results.txt`.
