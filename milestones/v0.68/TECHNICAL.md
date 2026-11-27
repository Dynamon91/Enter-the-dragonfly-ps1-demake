# Classic v0.68 — Luau containers, submerged gems and free dragonflies

Weighted completion remains 33.625% (34% rounded). Luau Island remains traversal stage 40% until its major quests are integrated. Source is the user's Definitive Edition 1.2.1 PS2 image, not verified retail. Original L_3_LI.CNK SHA256 8224399a9e479a764938ea29a0018e68a7b6d94da86b26273d3ffac75f7f4be1.

Underwater vase metadata/geometry records 1182/238, urn 351/463. Original 390/240 faces, optimized 374/240, 318 vertex entries. Source texture groups 142/340 uniquely resolved; two 64x64 indexed textures in new 12288-byte LIAOBJ.DAT. Reserve old terrain slots 62–63; maximum previously measured terrain demand 49 groups. Original 14 vase and 35 urn placements from corroborated records. Source EDF directory 1172, payload 751. Vase EDF specifies All destruction mask and gem2; prototype implements underwater charge/dive only. Urn EDF requires Charge/Super_Smash/Super_Flame and releases gem5; ordinary charge implemented, super abilities not implemented. Rewards release and collect once, same direct-gem identity ledger for submerged original gems. No shrapnel, original sound mapping or exact hit volume.

Three original free dragonflies capture-tested: group 3 flags 200/201/206. Challenge-associated 203/204/205 deliberately deferred, not an original EDF gate. All six source found/caught IDs and waypoint names inventoried. Shared geometry record 364 identical to 423/621/942/1193; green/yellow/red metadata 523/285/744. 590 main triangles, 3 wing poses with 34 triangles each; original texture centroid palette colors, approximated bind translations and hover motion, source flight paths not decoded, eyelids omitted. R2 fire/bubble, Circle breath. Native ledger records identity-indexed caught/found state, not full campaign world flags. 

Actual host movement plus interaction on real banks: 35/35 urns, 6/14 underwater vases (8 placements blocked by missing solid floor), 18 submerged gem identities worth 42, three bubble captures, no repeated capture/reward. Prior 600 land movement updates, jump/reset, eight dive/ascend columns, 80 horizontal swim ticks and shoreline entry/exit rerun and pass. Tests reposition player to nearby original coordinates; not continuous playthrough. Water-path samples check column and vertical range, not swept obstacle geometry. No emulator or hardware boot. All four v0.67 banks byte-identical. All 2594 raw CD sectors regenerated and compared. Independent local archive rebuild byte-identical. Native EXE 571392 bytes; linked RAM 1738912; 161632 bytes (157.84 KiB) before reserved stack. Host preview uses original recovered mesh and palette data, not emulator screenshot; no original animation or precise lighting/fog.

Rebuild from downloadable source archive:
    python tools/build_luau68.py base native67 . native68
    python tools/prepare_test68.py native68
    gcc -O2 -fsanitize=undefined -shared -fPIC -I native68 tests/objects68_host.c base/src/sector27.c -o native68/host68.so
    python tools/test_objects68.py . native68
    python tools/test_swim68.py base native68
    python tools/preview68.py . preview.png

Local archive includes complete generated prior native inputs, extractor scripts, converted model assets, test harnesses, reports and host preview. Public repository contains byte-matched new runtime and build scripts, tracker and notes; full extraction/test snapshot is in local archive. No proprietary converted banks pushed to public repository.

EXE SHA256 d032a5847281fdb27e5d348024a99d43f27e83c97d7c0ea24d5481e757052e99
BIN SHA256 a0a70513baaf36467ccd5a5c2f751d867a65e09956934e93451161bb11d1bef2
Source ZIP SHA256 38267fde82977f864536597a0075964eb4452808e7b7cfc723ed1f75dea2672c
Test ZIP SHA256 09a63e132023d7c2870c4430eb589818790a2eb7c0c51b99521229e3aac8f0b2

Both ZIP CRC tests passed. Next: recover missing seabed polygons and dynamic wall, source gates/buttons, prison/past-cave/landslide challenges, enemies and NPCs, original animation, remaining levels and native emulator verification.
