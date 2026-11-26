# Spyro: Enter the Dragonfly PSX — milestone 0.26

Dragonfly Dojo third-person traversal target, based on v0.24 hub engine and v0.25 source extraction. The original hub runtime and v0.25 viewer remain on disc as fallback executables (no in-game launcher or portal yet).

## Changes
- Native MIPS-I `ETD_DJPL.EXE`, original spawn `__CNODESPYRO` rounded to X=10534, Z=-14914; original transformed Y approximately -2075, snapped to recovered collision at -2145. Movement, charge, jump/glide, fire, animated Spyro, Sparx, gem collection and SPU driver inherited from v0.24. Emulator/hardware execution not verified.
- Dojo-specific cache: 1024-unit selection radius, 552 KiB maximum neighborhood, shared 1104 KiB pool, 9500 GPU packets, 768-unit terrain candidate radius. Reduced view radius is an interim memory tradeoff; visible scenery truncation remains.
- All 833 distinct nonempty neighborhoods tested (max 12 blocks, 561152 bytes). A 61-charge-step host route starting at original spawn across two resident sets was verified with simulated CD registers. Not a full level playthrough.
- 193 direct gems worth 389 and 45 exact `basket1.edf` placements wired to persistent source ID state; other variants and original reward scripts pending. Basket mesh reused from hub, provisional 1-gem reward. 192/193 gems and 45/45 baskets have a floor candidate within 110 units; one gem and four other objects fail this check. All 351 placement neighborhoods load. Original geometry/UV records unchanged; only 45 object kind flags and matching CRCs changed.
- 52 texture groups tested using actual native-cache C logic in a host harness; one ambiguous material remains flat-colored. Original PS2 lighting, blend rules and skybox not implemented. All 52 groups fit the existing 64-slot terrain VRAM cache.
- Linked allocation 1,846,304 bytes from load address, headroom 54,240 bytes before 0x801e0000 reserved stack region. Runtime stack high-water and FPS unverified. CD reads synchronous. Host preview uses actual assets and host route; staged companion position, no emulated GPU or actual gameplay recording.

## Build and tests
From project root, with Clang MIPS-I, LLD, llvm-objcopy, Python, NumPy and Pillow:
```
python tools/build_m26.py
python -m unittest discover -s tests -p test_m26.py -v
python tools/preview_m26.py
```
The build generates local target-specific source and data under `build_m26/play`, leaving prior sources intact. All 7 new tests pass. Prior milestones' tests are archived but not all rerun in this revision.

Disc boots the experimental Dojo gameplay target. Controls: D-pad/left stick move, Square charge, Cross jump/glide, Circle fire, L1/R1 camera, Select recenter, Start reset, L2 debug health decrement. Use CUE with BIN in DuckStation. An authorized homebrew boot method is needed for original hardware. No claim of boot or console verification.

Next: fix shortened draw distance through finer sector packing, complete collision, original enemy AI and door/portal scripts, breath abilities, audio and sky/lighting. Engineering estimate 60%; not percent of original game playable.
