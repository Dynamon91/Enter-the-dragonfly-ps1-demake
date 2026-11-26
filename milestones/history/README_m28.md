# Spyro: Enter the Dragonfly PSX — milestone 0.28

Original Dojo sky environment added to v0.27 gameplay. Native compilation verified; emulator/hardware execution not verified.

- Original Dojo source CNK records 1049 and 1080 yielded 14 meshes (environment globe, 11 clouds, sun rays and sun), 59 vertex packets and 1,080 triangles with exact source bounding-box matches. Four source textures resolved by material hash, directory extent, dimensions and size. See assets_m28/sky_report.json.
- Camera-relative background pass: source coordinates divided by 64, Y inverted to match the engine. Original UVs quantized at 1/1024. Four 64x64 8-bit textures and CLUTs consume 18 KiB VRAM. Explicitly separate from terrain cache, actors, HUD and framebuffer regions. Draw globe, additive sun, then half-blended clouds before world geometry. Vertical ramp UV clamp is a PS1 adaptation to avoid wrap seams, not verified original behavior; cloud/sun blending and cloud motion are not original PS2 equivalents.
- Linked RAM 1,782,736 bytes from load; 117,808 bytes before the reserved stack region. Host projection generated 102–415 background triangle packets depending on heading (mean 220.78) across 64 camera angles. Eight rasterized views had at least 99.07% globe coverage; integer seams/fallback clear and affine warping remain possible. Actual FPS unmeasured.
- Seven new tests and nine rerun v0.27 tests passed. Tests cover sky data, palette modes, nonoverlapping VRAM, GPU packet validity, rasterized sky coverage, unchanged gameplay inputs and complete new disc asset readback. Inherited tests run on v0.27 host harness and disc; not full-system emulation. No new gameplay mechanics; terrain draw radius and data unchanged.
- The disc boots ETD_SKY.EXE and retains ETD_WIDE.EXE and ETD_POOL.EXE as fallbacks. There is no in-game launcher or portal transition. Extract and open the CUE with the BIN in DuckStation; actual boot not verified. A direct executable needs disc-resident data.

## Rebuild
```
# Optional: regenerate sky data from user-supplied original ISO
python tools/sky28.py /path/to/original.iso
python tools/build_m28.py
python -m unittest discover -s tests -p test_m28.py -v
python -m unittest discover -s tests -p test_m27.py -v
python tools/preview_sky28.py
python tools/preview_m28.py
```
Python, NumPy, Pillow, Clang MIPS-I, LLD and llvm-objcopy required. Rebuild does not require original ISO if converted sky data is present. Previews are host renders using actual source assets and native background command stream with software projection, not emulator screenshots. CD reads remain synchronous. Original lighting, distant geometry, enemies, portals, NPCs, other levels, music and physical console testing remain incomplete. Prior 61% engineering estimate; this is a visual milestone, not a new playable level. Overall progress estimate 62% (not percentage of full adventure playable).
