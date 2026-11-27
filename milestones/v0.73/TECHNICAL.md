# Classic v0.73 — source-derived hub travel and capture

Full Classic estimate 49.425% (49% rounded, 51% remaining), previously 47.825%. Engine 74.5%, locations 46%, presentation 35%, QA 20%. Hub moves from native traversal stage 40 to partial quest stage 60 for six capture identities and eight tested travel/arrival routes. No complete level or minigame credit. Scope remains all 90 dragonflies, ten original main locations, sixteen minigame containers, original presentation and Ripto fight; expanded mode deferred.

## Original source
User-supplied Definitive Edition 1.2.1 modded PS2 disc, not verified retail. THE_HUB.CNK SHA256 d4721e60bc8b5f9bfedfd5e8d0378cc3af13f5b7d8176fb387478ed58d36ab69. Source node records 502/1402 corroborate spawn and travel positions. EDF directory 1500 and payload 968 identify flags 10..17; conversations 1273,1406,669,195,789,1368,393,218 specify requirements 1,6,15,25,32,45,55,65. Original Luau script checks 15 but sets 12; native approximation uses count gate rather than executing original conversations. Boss flag 30 and its entry floor unresolved. Eight return positions now floor-validated. Triangle at grounded, floor-path-checked entry within 520 units requests travel; direct overlay handoff via resident request, not original portal models or cutscenes. Destination uses existing level spawn. Select+Start in an adventure level requests return to corresponding hub source return point; Start alone returns to developer selector. Boss selectable only through developer menu. Failure to mount return neighborhood retains verified spawn. No actual in-level exit devices, original gate actors, ability unlocks or transition movies.

Six source hub DFLY placements use green_dragon_fly.mrb despite BLUE_DFLY EDF names. Metadata 647, geometry 786 identical to 1212/1537 and CCC record 353; 590 optimized main triangles and three 34-triangle wing poses; original palette references from directory 442/payload 772. Original flags 201/202/203/207/208/209 (found 212/213/214/218/219/220). R2 fire/bubble, Circle selected breath; approximate hover and bubble physics, original flight waypoints not reproduced. Native capture tests at nearby floor-verified positions and repeated hits; all six pass. Hub live count replaces saved hub count to avoid double-counting. 15 implemented identities total in unified disc (6 hub, 6 CCC, 3 Luau); normal progression cannot yet satisfy later gates, so developer selector intentionally remains unrestricted. No persistent memory-card I/O. 

## Streaming and regression
Replaced old eight-block hub cache with 16-block shared pool. 11,515 occupied anchors audited: peak 542720 bytes, adjacent union 600064, spawn union 665600, 536 KiB neighborhood and 672 KiB shared pool. Maximum 47 texture groups. Resolves formerly blocked Dojo/Cloud 9 return positions and first hub dragonfly floor, without changing original banks. Hub native headroom 457024 bytes. All ten prior level asset-file hashes unchanged (57 unchanged nonboot file entries). 10 native overlays and resident loader compiled; resident end 0x801e6430. All six hub bubble-capture and duplicate checks, eight entrance/threshold and eight return tests, failed-read return rollback, hub snapshot restore pass. All 100 ordered world-switch combinations, 30 injected failure cases and 10 snapshot regressions pass. Native tests use memory-backed CD and reposition player between scenarios. No continuous traversal proof, emulator/physical hardware boot, card/BIOS/controller timing or actual rendering verification. Independent logical ISO rebuild byte-identical; 27764 raw payload sectors checked against logical ISO.

## Artifacts
BIN SHA256 ffafb112b19241fd66c3bc86db87a31f1d0a2a50038f66b0431e2629cdf23263
Logical ISO SHA256 6289a91dae857815c83008f153abc15b859d1344ecfe75fcf6bd9a0c01415c25
Test ZIP SHA256 0fb54914945e4363c3ce553caf71bd983263750d7155e38127a13a47fbd1f8ca
Source ZIP SHA256 2df0185a14e64dd7174a5c1dc7894bed0c29e19d91fb3f1a50561c300790e6ea
Both ZIP CRC checks passed. Authoritative local source snapshot includes complete generated inputs, tests, tools, prior v0.72 source archive with all minigame/scene inventories, v0.71 test input, reports and preview. No original PS2 ISO required for native rebuild. Public GitHub contains selected original runtime code and technical notes; full build inputs are in downloadable archive. Host preview is rendered from actual packed hub terrain and recovered dragonfly model, not an emulator screenshot. 

Rebuild from extracted archive:
    python tools/build72.py inputs rebuilt previous_v071_test.zip
    cc -O3 tools/raw72.c -o raw73
    ./raw73 rebuilt/logical.iso rebuilt/ETD_CLASSIC73.bin

Next: restore original hub travel actors, initial dialogue reward, ability unlocks, upgrade Dojo, all remaining dragonfly identities and minigames, original boss, persistent save and actual emulator verification.
