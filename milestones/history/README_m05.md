# Spyro: Enter the Dragonfly PSX — milestone 0.5
Continues v0.4; **controller-driven technical diagnostic, not a playable conversion of the full game.** Source: user's Definitive Edition 1.2.1 PS2 ISO. No original disc image included.

## New source recovery
`tools/hub_mesh.py` matches the 465 named HUB_ meshes from combined MRB record 502 with 9 GEOM records, by geometry offset, packet count, strip lengths and original per-mesh bounds. All 465 match uniquely; 103,066 vertex samples and 70,411 non-degenerate triangles (original world coordinates and UVs). The dataset is not necessarily all hub objects, terrain, or the original collision BSP. `build_m05/hub/hub.npz`, `hub_report.json` store recovered geometry and metadata. Material hash-to-texture mapping remains unresolved.

## Native movement diagnostic
`build_m05/play/ETD_PLAY.EXE` contains a small sector near source coordinates (40000,0,4000), 945 deduplicated world vertices and 1,439 world triangles, plus the v0.4 optimized textured Spyro (2,060 triangles). Environment colors are illustrative debug colors derived from material names; not source textures. The grid stores 1,950 valid of 4,225 floor samples. This floor is a provisional heightfield inferred from near-horizontal render triangles. It is not original collision, and it may block walking, omit ground, or allow passage through walls. The cropped scene has open edges. No animation clip decoder, breath gameplay, enemies, collectibles, sound, or CD streaming in this build. Model uses prior provisional rest pose.

- D-pad or left analog stick (if controller is in analog mode): move relative to camera
- Cross: jump; hold to slow descent (prototype glide)
- Square + direction: charge-speed movement
- L1/R1: orbit chase camera
- Select: align camera with player heading
- Start: reset spawn

SIO0 direct polling with bounded timeouts (digital ID 41h, analog IDs 73h/53h). Controller on actual PS1 is not tested. Fixed-point movement and camera, GTE projection, world near-plane polygon clipping, painter sorting, GPU double buffering at 320x240. 30 FPS is a target only; no cycle-accurate timings. Native image 161,792 bytes; ELF loaded sections plus BSS end at 0x8005804c, below 2 MiB RAM; previous texture VRAM budget unchanged. Framebuffer 307,200 B + character texture/CLUT 75,264 B. Tests: 19/19 passed, including native executable header, mesh bounds, indices, floor data and actual C movement logic on host. No emulator or hardware run; no BIN/CUE. `farm_preview.png` is a host approximation, not an emulator screenshot. `hub_map.png` is a top-view of recovered named geometry, not original map art.

## Rebuild
Requires Python 3, NumPy, Pillow, Clang with MIPS-I target, ld.lld, llvm-objcopy. Supply local source ISO. v0.4 model assets/header retained in this package.
```
python tools/hub_mesh.py /path/to/source.iso build_m05/hub
python tools/build_play.py /path/to/source.iso build_m05/play
python tools/preview_play.py build_m05/play
python -m unittest discover -s tests -v
```
Open ETD_PLAY.EXE via DuckStation Start File with original hardware settings. Report any hang or invalid screen with logs/screenshot. Hardware controller reference: https://psx-spx.consoledev.net/controllersandmemorycards/ . Earlier milestones retained. Original game assets are for personal development; do not publicly redistribute them.

Next: original terrain material/texture associations, actual collision BSP, original animation clips and sector streaming; emulator test before treating the diagnostic as playable.
