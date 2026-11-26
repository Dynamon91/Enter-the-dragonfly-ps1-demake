# Spyro: Enter the Dragonfly PSX — milestone 0.3
Development checkpoint, NOT a playable game. Builds on v0.2 rather than replacing it. Source: user-provided Definitive Edition 1.2.1 PS2 ISO.

## Results
- All previous archive audit reports retained (64 CNKs, 24,324 entries).
- THE_HUB record 1130 / `af683368`: named gameplay Spyro shape metadata. Record 1529 / `ec6563c8`: 433,184-byte geometry candidate. All 18 named shape offsets and all 159 declared position packets match, yielding 5,088 source vertex samples. These are **point-cloud OBJ files only**, not reconstructed render topology or a rig. Position packet extraction verifies the subsequent normal-stream marker. Do not conflate sample count with unique vertices.
- THE_HUB record 772 / `7afc88b1`: complete PXT traversal, 540 CLUT groups and 1,839 indexed images including mipmaps. 536 first-mipmap images packed to native PS1 4/8-bit indices and RGB555 CLUTs (3,337,968 bytes total, to be streamed rather than resident). Four palette-only 4096-entry groups need further mapping. CSM1 palette swizzle matches visible artwork; alpha flags, texture-to-material IDs and all texture pixel layouts are still subject to validation. This output is raw indexed data, not a complete TIM atlas.
- Luau Island boat asset record 44: exact collision topology (326 vertices, 612 triangles). UFO asset record 419: two validated collision meshes (433 vertices, 814 triangles). These are original collision surfaces, not final render meshes or placed hub terrain.
- `ETD_GTE.EXE`: native MIPS-I 16 KiB diagnostic; runtime COP2 RTPS, 256 depth buckets, 612 flat triangles, two 320x240 RGB555 framebuffers. Automatic rotation; no controller input yet. Host approximation checks all 64 rotation steps, depth 291–542; no actual emulator or console execution. Direct GPU FIFO pacing (GP1 direction 1, bit25); two VBlank waits per frame, intended <=30fps, not measured. CPU packet submission is intentionally simple before DMA optimization. BSS buffers initialized by render code before use. Compile workaround: LLVM assembler does not accept CTC2 in MIPS-I mode; emit documented machine encodings directly.
- 9 regression tests pass. Old native icon remains a separate static diagnostic.

## Reproduction
Python 3 + NumPy + Pillow; Clang MIPS backend, ld.lld, llvm-objcopy. PSn00bSDK and a PS1 emulator are not installed in the current environment. Join parts 001–008, extract original ISO (ignore duplicates). From the project directory:
```
python tools/recover.py /path/to/source.iso build_m03/recovered
python tools/build_dynamic.py /path/to/source.iso build_m03/dynamic
python -m unittest discover -s tests -v
```
Prior milestone tools: `tools/cnk.py audit`, `tools/audio.py`, `tools/build.py`, `tools/verify_native.py`. See source for arguments. The old static diagnostic's limited interpreter does not validate the new GTE runtime.

## Test in DuckStation
Boot `build_m03/dynamic/ETD_GTE.EXE` directly using Start File (PS-X executable). Native resolution, no PGXP, no CPU overclock or expanded RAM. Expected: slowly rotating amber collision model of the original boat against a dark background. If black screen, provide logs and screenshot. This is not a bootable CD image or gameplay demo. The included PNG is a host approximation of native scene geometry; not an emulator screenshot. No real FPS claims.

## Next steps
Decode strip restart flags and cluster transforms, match material references to PXT groups, build true animated gameplay Spyro, implement controller and camera, recover actual level geometry. Keep source-derived assets private; do not publish commercial game files to public repos.

References: https://github.com/egartley/game-re-patterns (partial community formats); https://psx-spx.consoledev.net/ ; https://psx.wiki/tests/gpu-fifo/ ; https://github.com/Lameguy64/PSn00bSDK .
