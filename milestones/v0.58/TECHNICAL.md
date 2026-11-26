# Classic v0.58 — original Crop Circle Country sky

Classic only. Original source is the recovered user-supplied Definitive Edition 1.2.1 PS2 image. The previous v0.57 traversal engine and terrain banks remain intact. The native v0.58 build adds the original sky, not replacement art.

Source: L_2_CC.CNK metadata record 510 and geometry record 484. All 23 selected named sky shapes matched exact source bounds. All 1,441 nondegenerate triangles survive the 1/64 position scaling and Q10 UV conversion. Seven material hashes uniquely resolve to original PXT groups 329, 381, 357, 218, 96, 58 and 44. Sky textures converted to indexed 64x64 with RGB555 palettes (32,256 bytes total). The sky is camera-relative, rendered before terrain using the existing clipping and GTE projection path. Source alpha materials use approximate half-blend, not exact PS2 blend equations; sky animation not implemented. Dark clear color remains below uncovered horizon; terrain should cover it, but full-scene coverage has not been verified.

The seven 32-word-wide texture rectangles at x832–959, y256–383, and seven CLUTs at x768–1023, y4–10 are disjoint from existing actor/fire uploads, framebuffers and terrain slots. Host capture of actual sky packet construction tested all 64 camera yaws, 138–178 submitted triangles per angle, verified texture-window/CLUT/tpage fields and clipped coordinates. 14 new VRAM allocations checked against 152 total allocations. No claim of GPU emulation, real FPS or hardware execution. Host rasterizer displays approximate transparency and affine texture sampling; combined preview is not an emulator screenshot. Visible horizon banding and other alpha inaccuracies require review.

Native MIPS-I executable 552960 bytes; linked main RAM from load 1810224 bytes; headroom 90320 bytes before reserved stack. All 1746 raw Mode2 sectors structurally validated. The four prior CCC terrain/texture banks are unchanged. Gameplay source matches v0.57 after reversing four sky-only substitutions; all prior 600-tick movement, jump, collectible ID and disc regression checks were rerun on v0.57 and passed. No newly implemented enemies, NPCs, quests, dragonflies, music or minigames. No emulator installed; standalone test disc requires emulator or compatible loader.

Reproduction using recovered original CNK, previous generated v0.57 native directory and v0.29 workspace:

    PYTHONPATH=/path/to/v029/tools:tools python tools/sky_ccc58.py /path/to/L_2_CC.CNK /path/to/new/sky58
    python tools/build_ccc58.py /path/to/v029 /path/to/ccc57_native /path/to/new/sky58 /path/to/new/ccc58_native

Requires Python, NumPy, Pillow, Clang/LLD/llvm-objcopy. Host capture C harness is on GitHub; Python verification and preview scripts, reports, generated local sky assets and preview PNGs are in the downloadable v0.58 source archive. No proprietary asset banks published to public repository.

EXE SHA256 6796edd55723fd86e1cf5b822ad467aeb2fd12ad147ef6592736735db4027993
BIN SHA256 ffb1aef74cbfdac73ec475df9a019f52913741170db91a9b281fd7035df4dfb5
Local test archive SHA256 e40155609af9caf694aeaa57cf01d03079eb14a6cf8a973e3d9b46f998baf859
Local source archive SHA256 3e42dfa699c6dffccf12e6c780a9e794a7aee24b085ddd751e09cdfa1de119ed

Both ZIP CRC tests passed. Next: authentic CCC character and prop recovery, original dragonfly/quest triggers, sky blending improvements, actual emulator testing, and remaining Classic locations.
