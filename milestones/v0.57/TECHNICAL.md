# Classic v0.57 — Crop Circle Country native traversal

Classic only. Original source recovered in v0.55: user's Definitive Edition 1.2.1 PS2 image (modded, not verified retail). v0.56 recovered 508 selected named meshes and 52072 triangles, 41 material hashes all uniquely resolved, 392 nonempty PXT groups and one empty directory entry, 7889 candidate collision triangles, 342 corroborated placements. Four render and 61 collision triangles collapse under integer quantization; excluded IDs and face mapping retained by pack_ccc56.py. Packed 52068 render and 7828 collision triangles, 485 blocks, 29116-byte index, 2693120-byte terrain bank. Peak 163840 bytes / 19 blocks at 512-unit anchors and radius 1792. No claim of full scene coverage or exact BSP recovery.

v0.57 adapts the recovered authentic v0.29 native GTE traversal engine to this bank. Original Spyro spawn __CNODESpyro (10645.125,603.1400756835938,19103.013671875) maps to runtime Y-down (10645,-603,19103); floor query matches exactly. Original shared Spyro rig and animations, direct gem meshes and Sparx are reused. Original scene-specific 146 direct gem IDs total 569 value. 35 original basket placement IDs classified by EDF; provisional reward mapping by EDF yields 78 value (some node names differ, not verified retail rewards). Existing reconstructed movement/jump/charge/fire/gem and basket logic reused. The 41 original CCC texture blocks are bound to existing GPU upload/cache path. Dojo-specific Ninja Riptoc and sky routines removed; temporary flat sky clear color. Original CCC sky, enemies, NPCs, cow herding, UFO, scarecrow, minigames, dragonflies, portals, original music and other prop/script integration not yet implemented. Some shared models and audio inherited from v0.29; exact CCC sound assignments not established. All new code remains separate from preserved v0.37 source.

## Reproduction

Use the recovered original ISO and full v0.29 workspace from v0.55. From this repository root (Python, NumPy, Pillow, GCC, Clang/LLD/llvm-objcopy):

    python tools/classic_mesh50.py recover /path/to/recovered/SPYRODAT/CHUNKS3/L_2_CC.CNK 379 '^(sl[1-4]_|sh_sl[1-4]_)' /path/to/new/geometry
    python tools/ccc56.py /path/to/recovered/SPYRODAT/CHUNKS3/L_2_CC.CNK /path/to/new/geometry/geometry.npz /path/to/ccc_assets
    python tools/pack_ccc56.py /path/to/new/geometry/geometry.npz /path/to/ccc_assets /path/to/new/ccc_bank
    python tools/build_ccc57.py /path/to/spyro_etd_psx_m29 /path/to/ccc_assets /path/to/new/ccc_bank /path/to/new/ccc57_native
    python tools/test_ccc57.py /path/to/spyro_etd_psx_m29 /path/to/new/ccc57_native /path/to/ccc_assets

Build requires the previous generated m29 headers and banks; not a standalone public checkout. Index increased to 30720 bytes allocated. Old fixed terrain cache configured for 485 blocks and 41 materials, not the later generic v0.52–54 loader. No additional terrain arena. Native executable 471040 bytes, linked RAM from load 1728976, 171568 bytes headroom to reserved stack region. All 1706 Mode2/2352 sectors structurally validated. All 485 terrain CRCs and all original packed record IDs unique and accounted for. Clang experimental MIPS-I warning. Native executable has not been booted in emulator or on hardware.

## Host regression results on original CCC data

The test extracts the generated movement functions verbatim and compiles them with existing cache/collection/interact code and real sector27.c under UBSan. CD reads use memory callback, not real disc latency. Five independent runs of 120 ticks from original spawn, plus jump and 80 ticks settling. All maintained ground height while moving; back run stops at collision boundary. Direct gem score recorded in two runs; no claim of full path coverage. No reported UBSan runtime errors. All 146 direct gem and 35 basket identities mapped uniquely, not all collected or broken in playthrough.

| Input | End X | End Y | End Z | Gem value | Peak neighborhood bytes |
|---|---:|---:|---:|---:|---:|
| Forward | 10645 | -603 | 21383 | 0 | 65536 |
| Right | 12925 | -603 | 19103 | 5 | 65536 |
| Back | 10645 | -603 | 17830 | 0 | 67584 |
| Left | 8365 | -603 | 19103 | 2 | 86016 |
| Charge forward | 10645 | -603 | 23663 | 0 | 65536 |

Jump rose above spawn and landed at -603. No renderer/GPU, actual controller or audio hardware behavior validated by the host tests. Original BSP flags, hazards, clearance, world transforms, draw distance, texture alpha/layers, affine artifacts and actual frame rate remain unverified. Original game completion and v0.37 rebuild remain outstanding. Test disc is standalone CCC, not a complete connected adventure, and needs compatible emulator or authorized homebrew loader.

EXE SHA256 e02af3d79d61dd8bf0c3b8068c0521fc824508b3ee25a65a095aea37403c5a35
BIN SHA256 5e04f174ac6ee8a0dff5b98db3191b12678bc652e82dd9ada9f00904a57419a6
CUE SHA256 18fdc01ee5457630f2e040c0911bd6aa1c151b1e7882f54506bf40f6d8ea4809

Private local archives: spyro_etd_classic_v057_ps1_test.zip (SHA256 6ecaef28496545cac73356fb8cc4c15e1554f26c396df8941ddbe92847861387); spyro_etd_classic_v057_source.zip (SHA256 6153cd89276841fe88c34959c60ea8273f75d4b0cf006a92b1ada91449a581f9). Both passed ZIP CRC tests. Public repo contains source/reports only; local preview is included in source archive (actual geometry plus measured host traces, not emulator capture). Next: real emulator run, CCC original sky/quests/actors and remaining terrain, rebuild v0.37 dependencies and connect Classic scenes.
