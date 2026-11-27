# Classic v0.71 — cross-level material restoration and minigame geometry

Full Classic estimate 47.20% (47% rounded; previous 46.95%). Core engine 70%, locations 44%, presentation 35%, QA 20%. Streaming and textured graphics each increased from 80 to 85 in engine rubric, no level-stage or minigame runtime credit. Scope includes all 90 original dragonflies, ten main locations and sixteen minigames; expanded mode deferred.

## Rebuilt native prototypes

| World | Prior faces | New faces | Selected material faces unresolved | RAM headroom bytes | Peak texture groups |
|---|---:|---:|---:|---:|---:|
| Cloud 9 | 88168 | 106867 | 0 | 413568 | 38 |
| Monkey Monastery | 36165 | 40604 | 0 | 668768 | 28 |
| Honey Marsh | 87671 | 91163 | 0 | 514816 | 37 |
| Thieves Den | 103674 | 120606 | 0 | 457408 | 60 |
| Jurassic Jungle | 79244 | 86504 | 20 | 411152 | 47 |
| Ripto arena | 12259 | 12355 | 0 | 969680 | 12 |

458099 packed faces, +50918. Of 50965 previous unresolved selected faces, 20 remain. Quantization exclusions and 460 arena background faces remain; many unselected source meshes and local/world transforms remain unfinished. Source is user-provided Definitive Edition 1.2.1 modified PS2 image, not verified retail. No invented textures: material bindings require exact source texture hash, dimensions and size. Context-specific reused hashes mapped by directly embedded material node or uniquely corroborated geometry context; first source pass only, not original multipass shaders. Three dual-material shapes had misread packet-range headers: C9_AA_Shape33 (12+1 packets, groups 29/363), Mid1_Shape102 and Mid1_Shape101 (2+1 packets each, groups 326/52). Union bounds verified, 22 previously omitted faces recovered in those extra packets. Arena platform Shape2 restored by exact shape identity in standalone metadata 589 and source group 90. Jurassic Jungle Mid1_ON_Shape1 uses group 316, a 4096-color highlight map with no decoded indexed mip; its 20 faces remain quarantined. New packed material IDs are local synthetic identifiers, original hash preserved separately. No fake visual replacement.

## Cache and verification

Per-level shared active/pending pool sized from exact adjacent-anchor unions and union with original spawn for reset, rather than two copies of the largest neighborhood. Movement/lookahead bounded to adjacent anchors; arbitrary teleport not supported. 152268 occupied anchor neighborhoods and 601853 adjacent pairs audited, peak 60 groups under 64 terrain slots. 1916 real-bank transitions and 432 failed-read rollback tests passed on host. Honey Marsh headroom improved from 43808 to 514816 bytes, Thieves Den from 36336 to 457408 bytes. All six independent EXE/BIN rebuilds byte-identical, 30 movement cases (3600 ticks), six jump tests, 3637 terrain blocks, 319 texture blocks, 13837 raw sectors validated. No emulator or physical hardware execution. Four older native discs (hub v0.21, Dojo v0.29, CCC v0.65, Luau v0.69) preserved byte-for-byte in test bundle, not rebuilt in this milestone.

## All-minigame geometry recovery

All 16 original minigame containers processed by strict source packet/bounds matching in largest scene metadata record: 8611 selected, 6441 matched, 866 duplicate shapes, 1304 unmatched, 809792 local triangles with UVs. Separate NPC/vehicle models, material bindings, collisions, transforms, game logic, objectives and transitions remain incomplete. No native minigame runtime added. Additional broad main scene candidate geometry exports completed for CCC and arena only; batch interrupted, remaining expansions not claimed. Scope ledger tracks 10 main locations and 16 minigames plus 38 auxiliary CNKs, all 24324 source records in nested previous inventory.

## Artifacts and reproduction

Authoritative complete local source archive contains six revised native inputs, extraction/repair/build/test scripts, all minigame candidate meshes/reports, two completed broader main scene exports, preview, coverage ledger and prior v0.70 source archive. Public GitHub code/notes only, no converted proprietary asset banks. From extracted root:
    for w in C9 MM HM TD JJ BOSS; do
      python tools/build_world71.py base shared prior "$w/assets" "$w/bank" "$w/rebuild" "$w/summary.json"
      python tools/test_world71.py base "$w/rebuild" "$w/assets"
    done

Source ZIP SHA256 731fec53df002569a9f0f06d6388009aabecb41f7977e8ba496e67d6dbb4ec27
Test ZIP SHA256 1ce66ea76d6e87aa8e2ffb7eecc5b751bebec1479dd110c56d26c56ebda3b2dd
Both ZIP integrity tests passed. Host reference preview, not emulator screenshot.

Next all-level work: source placement/transform resolution, original texture layering and highlight map, minigame collision and objectives, NPC/actor models and behaviors, boss fight, unified campaign and collectible ledger, emulator boot and full continuous playthrough. Nothing intentionally removed from scope.
