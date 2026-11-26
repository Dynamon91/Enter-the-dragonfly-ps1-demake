# Spyro: Enter the Dragonfly PSX — milestone 0.4
Continues v0.3. **Native graphics diagnostic, not a playable game.** Original source: user-provided Definitive Edition 1.2.1 PS2 disc.

## Original mesh recovery
- THE_HUB.CNK metadata record 1130, geometry record 1529. 18/18 meshes, 159/159 packets, 622 strips, 4,721 valid vertex samples (previous 5,088 included padded slots), 3,354 nondegenerate triangles. The VIF table's first byte is valid vertex count; subsequent nonzero bytes encode strip lengths times three. Every packet's lengths sum to its count. All component bounds match the MRB metadata within 0.001 source units. Normals are signed 16-bit triples and UVs are float pairs.
- `build_m04/spyro/spyro_rest.obj` + MTL and PNGs: original mesh topology and texture coordinates; joint local translations extracted, parent chains inferred. Body and wings are bind-pose geometry; head and rigid appendages placed using translation chains. No skin deformation or recovered animation playback. Standing pose and wings are not the final gameplay pose.
- Material choices: original hub PXT groups 303 (body), 411 (wing), 429 (eye), 16 (eyelid, OBJ only), selected visually; exact hashed material-to-PXT links, UV wrap and alpha semantics not confirmed. Eyelid overlays and bounding proxy are retained in OBJ but excluded from viewer. Eye appearance and affine sorting artifacts need further work. Native viewer treats textures as opaque.

## Native builds
| Build | Unique projected positions | Triangles | Executable |
|---|---:|---:|---:|
| ETD_SPYRO.EXE | 1641 | 3210 | 153600 B |
| ETD_LOD.EXE | 1157 | 2060 | 129024 B |

MIPS-I, runtime COP2 RTPS, 1024 depth buckets, GP0 textured triangle commands, double-buffered 320x240 output. Three original textures quantized to 8-bit indexed RGB555 CLUTs, 75,264 VRAM bytes. Two framebuffers require 307,200 bytes. VRAM uploads are tested for bounds and non-overlap. GPU interrupt fence before display swap; two VBlank waits. No controller, audio, terrain, or animation in the viewers. Reduced LOD uses adaptive voxel clustering (finer at the legs and tail to avoid visible detachment); not a final production mesh or performance target. 64 rotation matrices checked by host projection; preview PNGs are painter-sorted affine software renders, not emulator screenshots. 14 host regressions passed. No measured PS1 performance; no emulator/real hardware execution. No BIN/CUE yet.

## Reproduce
Python 3, NumPy, Pillow, Clang MIPS-I backend, ld.lld, llvm-objcopy. From project directory, supply your local original ISO:
```
python tools/build_spyro.py /path/to/source.iso build_m04/view
python tools/build_spyro.py /path/to/source.iso build_m04/lod --lod
python -m unittest discover -s tests -v
```
Earlier milestones retained; see README_m03.md. Use DuckStation Start File to launch either native executable directly. Set native resolution and disable PGXP/overclock. Expected: rotating textured Spyro rest pose. If it fails, share emulator logs and screenshot. The model data derives from the commercial game; keep this package for personal development, do not publish original assets.

Next: decode skin-cluster matrices and animation clips, exact texture references, better topology-preserving LOD and controller/camera in a playable scene. GPU documentation: https://psx.wiki/hardware/gpu/gp0-transfer/ .
