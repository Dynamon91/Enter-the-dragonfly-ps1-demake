# Spyro: Enter the Dragonfly — PSX milestone 0.10

Native interactive diagnostic based on the supplied Definitive Edition 1.2.1 PS2 disc. This is not a complete game. Original ISO not included. Earlier milestones retained.

## New in 0.10
- The `spyro_character` resource contains 167 target IDs and attribute codes; the table is identical in hub metadata records 502 and 1641. All 129 skeletal rotation channels and 3 root translation channels bind to the 43 named joints. The inverse bind matrices in `skinCluster1`/`skinCluster2` agree; reconstructing parent links from local translations gives maximum error 0.00000769 source units.
- All 80 skinned geometry packets (body and wings) decode four indices and float weights per valid vertex. 2,481 skinned source samples; indices are one-based offsets in units of four, verified active range, zero unused. Maximum weight sum error 1.2e-7. The existing 1,157-vertex LOD is retained; up to four influences per vertex, maximum discarded weight 0.096%, integer weights sum to 256.
- Nine original clip data sets sampled into 245 bone-matrix frames at 30 Hz: idle, walk, run, charge, jump start/cycle/land, glide cycle, fire breath. Native fixed-point skinning and a four-tick transition blend are compiled into the interactive farm diagnostic. All 245 host poses (283,465 vertices) agree with independent NumPy reference. C state-machine tests exercise all nine states. Circle triggers the fire animation only; no projectile or damage logic. Walking/running animation selection uses analog deflection; original movement speed tuning remains pending.
- Original channel IDs, bind matrices and weights are validated. Euler XYZ rotation order and linear interpolation are provisional; tangent semantics and PS2 playback comparison pending. Facial morphs, eyelids, eye channels and squash/stretch not yet implemented. Airborne root translation suppressed so existing jump physics owns displacement. No hardware or emulator boot claimed. Real frame rate unmeasured. Native code is more demanding than v0.9; matrix palettes occupy 252,840 bytes, linked allocation from load address 1,785,248 bytes, 115,296 bytes remaining before reserved stack region. v0.9 world and visibility assets are byte-identical.
- 56/56 host regression tests passed. 344-sector MODE2/2352 disc EDC/ECC and ISO executable read-back passed. No retail license sectors; unmodified PS1 requires a homebrew boot method.

## Reproduce
Python 3, NumPy, Pillow, Clang MIPS-I, LLD and llvm-objcopy. Earlier v0.9 generated assets retained as input.
```
python tools/build_m10.py /path/to/source.iso build_m10/play
python tools/disc10.py build_m10/play
python tools/preview_m10.py build_m10/play
python tools/preview_scene10.py build_m10/play
python -m unittest discover -s tests -v
```
Host previews are not emulator screenshots: `animation_preview.png`, `idle_preview.gif`, `farm_animated_preview.png`. The first two use actual C skinning output and source textures; the latter combines a sampled idle pose with the host rasterizer. See `rig_report.json` for quantitative validation and limitations.

## Controls
Extract BIN and CUE together and open `ETD_PSX_M10.cue`, or load `ETD_ANIM.EXE` directly in DuckStation. D-pad/left stick move; Cross jump/glide; Square charge; Circle fire animation test; L1/R1 camera; Select recenter; Start reset. Digital movement chooses run animation. The controller and GPU runtime still require emulator or hardware testing.
