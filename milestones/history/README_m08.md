# Spyro: Enter the Dragonfly — PSX milestone 0.8

Native interactive diagnostic based on the supplied Definitive Edition 1.2.1 PS2 disc, not a complete game. Previous milestones remain included; the original ISO is not included.

## New in 0.8
- Exact base-texture lookup recovered from the original executable: lowercase ASCII filename, MD4, then XOR of four little-endian 32-bit digest words. The executable routine at 0x18a490 folds the digest. MD4 round constants and rotations are present in the routines around 0x1944c0 and 0x1946b0. Five RFC 1320 vectors pass. All 693 indexed material references (476 distinct filenames) match original directory keys and payload lengths; 688 also match decoded image dimensions. The other five reference multi-CLUT resources without decoded image dimensions.
- All 23 active farm base materials and three Spyro base textures resolve by original metadata, replacing 14 old farm candidate slots, retaining three, and adding six slots. Spyro body group 303 retained, wing corrected to group 21, eye corrected to group 296. PS2 blend layers, lighting and alpha semantics remain approximate; 8-bit CLUT conversions apply diagnostic opacity/cutout policies, not exact PS2 blending.
- Recovered 39 previously excluded hub meshes with shadow-associated names, adding 5,242 source triangles to the 70,411 already indexed. 244 source triangles restored to the test sector (254 after UV subdivision). Nearby floor geometry subdivided further to improve depth ordering: 4,973 terrain triangles total, 3,135 vertices. Compact 24-byte native packets preserve memory headroom. In the four fixed host preview views, clear-color pixels in the lower halves decrease from 82,289 to zero; this is a local diagnostic, not a whole-level guarantee.
- Expanded collision height grid from 227 to 879 samples by corroborating extracted collision polygons with restored visible floor. All 227 prior samples preserved. Added samples are heuristic; full BSP collision, wall handling and seamless streaming remain unfinished.
- Native MIPS-I compilation passed; 378,880-byte PS-X EXE, linked memory from load address 1,495,812 bytes, static allocation ends at 0x8017d304. 43 host regression tests pass. MODE2/2352 disc sector EDC/ECC and ISO executable read-back verified. No retail security sectors, no emulator or console boot verified. Runtime performance and actual frame rate are not measured.
- Preview: host rasterization using shared C clipping code and approximated projection/rasterization. This is not an emulator screenshot. The original Spyro rest pose remains provisional. Distant coverage, character animation, visual artifacts and exact blend/lighting remain to be corrected.

## Reproduce
Python 3 + numpy + Pillow; clang MIPS-I, ld.lld, llvm-objcopy. The earlier v0.6 generated assets are retained as input.
```
python tools/build_m08.py /path/to/source.iso build_m08/play
python tools/preview_m08.py build_m08/play
python tools/disc08.py build_m08/play
python -m unittest discover -s tests -v
```
See `build_m08/play/report.json`, `texture_registry.json`, `build_m08/shadow/hub_report.json`, and `reports/m08_tests.txt`. The nested `collision` and `candidate_metadata_matches` fields in the report describe the inherited baseline; the new `collision_total_samples` and `verified_world_bindings` fields describe the current build.

## Test on an emulator
Extract BIN and CUE together and open `ETD_PSX_M08.cue`, or load `ETD_MAT.EXE` directly in DuckStation. D-pad/left stick move; Cross jump/glide; Square charge; L1/R1 camera; Select recenter; Start reset. Stock PS1 requires a suitable homebrew boot method. No emulator execution is claimed.
