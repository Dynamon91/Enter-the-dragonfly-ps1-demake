# Classic v0.66 — original Luau Island native traversal

Full-project estimate 33.50%, rounds to 34% (previous 31.30%). Engine estimate 68%, original locations 20%, presentation 35%, QA 20%; Luau Island earns native traversal stage 40%, not quest completion. Four original location prototypes historically, zero continuously verified.

## Source and conversion
Original user-supplied Definitive Edition 1.2.1 PS2 image, modded, not verified retail. L_3_LI.CNK SHA256 8224399a9e479a764938ea29a0018e68a7b6d94da86b26273d3ffac75f7f4be1. Metadata record 394, texture table 333, texture data 612, collision 448, corroborating placement record 628. Selected 589 named meshes, all uniquely matched by source bounds; 91,462 triangles. Excluded separately placed LI_BWALL_CShape (631 triangles; context-specific material binding, not static terrain). Remaining 90,831 static triangles, 82 uniquely resolved materials, 401 nonempty source texture groups. Quantization excluded 19 collapsed render triangles, IDs recorded. Packed 90,812 render triangles, 7,601 heuristic collision candidates, 326 corroborated object placements. 142 direct gems (457 value), 39 baskets (116 provisional EDF value). Other placements inventoried, not implemented. Actual spawn recovered from two records: (-7025.614,951.768,-7182.921), runtime rounded (-7026,-952,-7183), floor -950. Heading 28/64 from source yaw. Source local geometry transforms not comprehensively reviewed. Water, transparency and dynamic wall not resolved; temporary clear color, no original sky yet.

## Native budget and verification
498 terrain blocks, 29,896-byte index, peak 397,312 bytes (388 KiB), 25 blocks. Separate 416 KiB active/pending budgets. 36,361 occupied neighborhood windows, peak 49 distinct texture groups within 64 slots. Native standalone traversal reuses v0.57 shared engine and v0.65 snapshot assets, not CCC-specific quests. EXE 471,040 bytes, linked RAM 1,638,624 bytes, 261,920 bytes (255.8 KiB) headroom. 600 movement ticks across five directions/charge tests, jump landed, all 142 gem and 39 basket identities checked; no pickup observed in those five traces. All 498 sector16_load checks and 82 texture block/host upload checks passed. All 2,539 raw CD sectors compared to regenerated sectors. Independent build from the source snapshot reproduced identical disc. Existing CCC v0.65 preserved separately. No emulator or hardware execution; no full playthrough or continuous campaign integration. 

## Local artifacts
Source archive contains complete generated banks, build script, extraction/packing tools, host tests and progress tracker; run `python tools/build_luau66.py base shared prior assets bank out` from extracted root. The GitHub branch preserves progress, extraction/packing and test source; the complete local archive is authoritative for the build and generated assets. No proprietary banks committed to public GitHub. Preview is host reference rasterization of recovered terrain and opaque source textures, not emulator screenshot.

EXE SHA256 15d7ec5a417ce3fb7a7041910e8aceff9257cdf46deb9e724626ecfeffa93394
BIN SHA256 f6bf1c6de80bf7065f798052a515721ebc03cc6f9e2e978a2423680bcb1055f1
Source ZIP SHA256 6f2435ed00da6ea454867272b475fc6cdaa9ede9fd4a923b91199ba318ac1a7d
Test ZIP SHA256 e1adb858319fad783fecec379c4775c1349d728811894dbd6ec7803071a96099

Both archives passed ZIP integrity tests. Next: water/swimming and original Luau sky, enemies, NPCs, quests, dynamic rock walls, dragonflies, connected portals, and conversion of remaining original locations. Expanded content remains deferred.
