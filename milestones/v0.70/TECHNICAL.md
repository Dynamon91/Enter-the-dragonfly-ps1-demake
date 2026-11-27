# Classic v0.70 — all-location conversion checkpoint

Scope: released Classic adventure; all 90 dragonflies, hub, eight released adventure levels, Ripto arena and original minigames. Expanded Mode remains deferred. Weighted engineering estimate 46.95%, rounded 47%, using established rubric: engine 69% x 25%, main locations 44% x 55%, presentation 35% x 10%, QA 20% x 10%. Six new native traversal prototypes earn stage 40 each, not full gameplay credit. No extra credit for source availability. No continuous level playthrough or emulator/hardware execution.

## Actual new builds

| Level | Packed render triangles | Collision candidates | Original placements | Native sectors | RAM headroom bytes |
|---|---:|---:|---:|---:|---:|
| Cloud 9 | 88168 | 13660 | 558 | 2516 | 284624 |
| Monkey Monastery | 36165 | 4656 | 353 | 1356 | 496768 |
| Honey Marsh | 87671 | 11645 | 477 | 2274 | 43808 |
| Thieves Den | 103674 | 15419 | 329 | 2744 | 36336 |
| Jurassic Jungle | 79244 | 6760 | 297 | 2461 | 280128 |
| Ripto arena | 12259 | 206 | 9 | 1479 | 863168 |

Totals 407181 packed render triangles, 52346 collision candidates, 2023 placements, 3612 sector blocks, 289 converted texture blocks, 1298 direct gem identities and 149 basket identities. Actual native host movement routines exercised 5 x 120 ticks per location, 30/30 moved, six jump/landing scenarios, all six original spawn positions (arena original spawn drops under gravity to source collision candidate 207 units below). All new raw sectors regenerated and compared (12830). All six independent builds byte-identical. 152030 occupied anchor neighborhoods audited, none exceeds 64 terrain texture groups; peak groups 30/26/37/51/45/11. Honey Marsh and Thieves Den main RAM margins tight, need optimization before new resident assets.

## Explicit coverage gaps

Source is user's Definitive Edition 1.2.1 PS2 image, modded, not verified retail. Six selected source geometry sets comprise 458709 faces before filtering. 50965 unresolved material faces quarantined; source record and face arrays retained. Additional collapsed quantization faces and arena background shape 44 (460 triangles) excluded from static pack. Missing material bindings and incomplete source transforms cause visible holes or visual errors; no fabricated replacements. Collision extraction is heuristic, not fully decoded original BSP. Source placements not all implemented or proven reachable. No new source actor models, dragonfly quests, sky, minigames or boss combat in these six traversal builds. Gem/basket identities verified, not full collection tests. Arena is traversal only, with no lava hazard, moving platforms or Ripto AI. Older hub v0.21 and Dojo v0.29 discs preserved, later Dojo code on main is not in archived v0.29 disc. CCC v0.65 and Luau v0.69 preserved separately. Ten independent test discs, not connected campaign, no global collectible save.

## Complete source inventory

Read-only ISO audit: 103 file directory entries, all 64 CNK containers (10 main locations, 16 minigames, 38 auxiliary), 24324 directory records and 6666 valid VAG headers including duplicates. All records hash/offset/size/reference inventory; mesh and placement metadata and flag script candidates retained in detailed local manifests. This is directory accounting, not semantic completeness. All 16 minigame containers remain unimplemented in the native campaign. No inventory item earns implementation credit by being listed.

## Rebuild and archive

The authoritative downloadable source archive contains all six new banks, extracted geometry and UVs, inventories, coverage ledgers, tools, native build inputs, tests and preview, with earlier CCC and Luau source snapshots nested. User's v0.29 archive remains separately required for earlier hub/Dojo rebuild. Public repository includes progress and technical notes; local archive is complete source for this milestone, proprietary converted banks not public.

From extracted source root:
    for w in C9 MM HM TD JJ BOSS; do
      python tools/build_world70.py base shared prior "$w/assets" "$w/bank" "$w/rebuild" "$w/summary.json"
      python tools/test_world70.py base "$w/rebuild" "$w/assets"
    done

Test archive SHA256 8853f58c5ecd46cfadcc29af68b478749839da5f2bbbee1fdc4e41ff0815f3d1
Source archive SHA256 c43206e6641a1a5bbb15a03ed0e4a78b1c046dc19a3d5de04b13f741336d3ca1
Both ZIP integrity checks passed. Preview is host reference rasterization of actual recovered geometry near original spawns, not emulator output.

Next all-level passes: resolve material contexts and scene transforms, per-level sky/actor models and collision, all original minigames and quest scripts, boss fight and persistent 90-dragonfly campaign. No level omitted from scope.
