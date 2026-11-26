# Spyro: Enter the Dragonfly — PSX milestone 0.7

Native interactive diagnostic, not the complete game. Based on the user's Definitive Edition 1.2.1 disc. Prior versions are retained. Full original ISO is not included.

## New in 0.7
- Five-plane fixed-point frustum clipping (near/left/right/top/bottom) for the actor and source terrain, including UV interpolation. Large GPU primitives are clipped instead of simply dropped; existing hardware bounds checks remain. Projection cache for trivially visible triangles. 4,000 randomized host cases exercised.
- Expanded source sector by using AABB intersection rather than only triangle centroid: 1,326 original source triangles added, resulting in 3,543 PS1 terrain triangles after splitting. Geometry from v0.6 is preserved. `midwood` uses an explicitly provisional existing `litwood` texture for 504 of the added original triangles. No exact texture binding claimed.
- `yellow_T` candidate had constant zero source alpha, which was converted to entirely invisible in 0.6. Diagnostic opaque conversion now preserves its original RGB; varying-alpha foliage retains alpha testing. This is a diagnostic policy, not recovered original blend semantics. Ground gaps still substantial.
- First MODE2/2352 BIN/CUE test disc: ISO9660 directory, SYSTEM.CNF, native executable, Mode 2 Form 1 EDC/ECC. Read-back via pre-existing ISO parser verified identical executable. No retail license/security sectors. Not boot-tested.
- Native build and 35 regression tests pass. Static ELF load allocation ends at 0x80178ab4, below 0x801e0000 linker limit. Frame rate, runtime performance, emulator boot and physical hardware remain unverified. Collision remains the sparse v0.6 grid, original animations and exact textures still unresolved.

## Reproduce from this package
Python 3 + numpy + Pillow; clang MIPS-I, ld.lld, llvm-objcopy.
```
python tools/build_m07.py /path/to/source.iso build_m07/play
python tools/preview_m07.py build_m07/play
python tools/disc07.py build_m07/play
python -m unittest discover -s tests -v
```

## Test
Open `build_m07/play/ETD_PSX_M07.cue` in DuckStation, or load `ETD_CLIP.EXE` directly. D-pad/left stick move, Cross jump/glide, Square charge, L1/R1 camera, Select recenter, Start reset. Stock hardware needs an appropriate homebrew boot method. This is a test image, not a retail-authenticated disc. Preview is host software-rendered using the same C clipping algorithm, not an emulator screenshot. Keep both BIN and CUE in same folder.
