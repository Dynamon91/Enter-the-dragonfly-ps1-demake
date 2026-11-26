# Spyro: Enter the Dragonfly — PSX milestone 0.15

Continuation of v0.14. Native PS1 farm-sector prototype; not a full game. Original PS2 ISO is not included.

## New in 0.15
- Original sheep resource `sheep.mrb` (metadata 1318, geometry 1531) and standard butterfly (metadata 280, geometry 270) decoded, with bounding boxes validated against source records. Visible sheep source triangles: 1,100, reduced to 353; butterfly 304, reduced to 49. Four base texture filenames resolved through the original folded MD4 directory. Reduced meshes use per-face colors sampled from original texture UV centroids; exact UV orientation, eyelids, facial rest transforms, PS2 shader blending and skeletal animation remain provisional.
- All 12 source sheep placements preserved in `assets_m15/fodder_report.json`. None is within the current farm grid. The optional diagnostic sheep at (-1152,800,-2820) is NOT an original placement. R2 enables/disables this stationary test encounter; L2 simulates one damage event per button press. Charge or fire defeats the sheep, releasing a butterfly; within collision-supported range it approaches Sparx (or Spyro when Sparx is absent), restores one health level up to 3, and can only be consumed once. It expires after 180 ticks. No original sheep AI, enemy damage, death/restart sequence, or original fodder sound has been implemented.
- Sparx health states: gold, blue, green, absent. At zero health, automatic gem assistance and companion rendering are disabled; direct pickups remain enabled. Health HUD is diagnostic, not the original UI. Health resets on Start. Butterfly wing flap is reconstructed from source geometry, not original animation.
- Existing terrain, character animation, gem/basket assets and sound bank retained byte-for-byte. Native MIPS-I executable 694,272 bytes, linked allocation 1,819,872 bytes from load address, 80,672 bytes before reserved stack. Disc 361 sectors. 101 host regression tests passed (92 previous + 9 new), including EDC/ECC and ISO executable readback. No emulator boot, physical console test, actual FPS or audible playback verification.

## Build
Requires Python 3, NumPy, Pillow, Clang MIPS-I, LLD, llvm-objcopy.
```
# Optional source re-extraction:
python tools/fodder15.py /path/to/source.iso assets_m15
python tools/build_m15.py build_m15/play
python tools/disc15.py build_m15/play
python tools/preview_m15.py build_m15/play
python tools/fodder_asset_preview15.py
python -m unittest discover -s tests -v
```

## Controls
Extract BIN and CUE together and open `ETD_PSX_M15.cue` in DuckStation, or load `ETD_FODR.EXE` directly. D-pad/left stick move; Cross jump/glide; Square charge; Circle fire; L1/R1 camera; Select recenter; Triangle toggles legacy fire targets; Start resets; R2 toggles the sheep encounter; L2 simulates damage. At initial spawn press R2 and L2, then hold Circle to test the butterfly and health recovery. Real unmodified consoles require an appropriate homebrew loader. The previews are software-rendered diagnostics, not emulator screenshots.

Next priority: sector streaming and real sheep positions; more RAM headroom, original enemy AI, source animation and material improvements, and hardware validation. Existing lighting/shadow artifacts remain.
