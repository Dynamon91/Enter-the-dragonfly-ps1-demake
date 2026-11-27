# Classic demake completion — v0.72

**48% estimated complete / 52% remaining.** Scope: the released original adventure, all 90 dragonflies, Dragon Realms, eight released adventure levels and Ripto's arena. Expanded Mode is excluded. This is a subjective engineering estimate with an explicit weighted rubric, not a measured fraction of code, assets, or elapsed time. Source availability is tracked independently and earns no level-conversion credit by itself. Host tests are not emulator/hardware verification.

| Category | Weight | Estimated completion | Weighted points |
|---|---:|---:|---:|
| Core PS1 engine | 25% | 72.5% | 18.125 |
| Original locations and quests | 55% | 44% | 24.20 |
| Audio, menus and presentation | 10% | 35% | 3.50 |
| Testing and release readiness | 10% | 20% | 2.00 |
| Total | 100% | | 47.825 (rounds to 48%) |

## Evidence and scoring

Core: equal-weight estimates for native compiler/disc packaging (100), terrain streaming (85), textured graphics (85), movement and input (90), collision (80), camera (70), actor animation (60), combat and breath abilities (60), scene transitions (60), progression/save support (35). Average 72.5%. Ten native overlays share a resident test selector and RAM session ledger; original portals, memory-card saves and native emulator verification are outstanding.

Location milestones: 0 = source only; 20 = converted static bank; 40 = native traversal prototype; 60 = subset of quest mechanics implemented; 80 = full original gameplay integrated; 100 = fidelity and continuous playthrough verified. The older hub and Dojo prototypes are credited at their highest evidenced stage, not claimed as part of the latest standalone CCC disc.

| Location | Stage credit | Evidence |
|---|---:|---|
| Dragon Realms | 40% | Earlier native hub traversal |
| Dragonfly Dojo | 60% | Earlier native terrain, quest/capture/dialogue prototype |
| Crop Circle Country | 60% | v0.65 native traversal, six dragonfly identities, two transport rides and enemy/urn interactions exercised through host tests |
| Luau Island | 40% | Native traversal, recovered sky and swimming; 35 urns, 14 vases, 24 underwater gem identities, three free dragonflies, five switches and three gate state changes host-tested; major quest access routes incomplete |
| Cloud 9 | 40% | v0.71 standalone source-derived traversal; material restoration, measured pool, movement/jump/cache host tests |
| Monkey Monastery | 40% | v0.71 standalone source-derived traversal; material restoration, measured pool, movement/jump/cache host tests |
| Honey Marsh | 40% | v0.71 standalone source-derived traversal; material restoration, measured pool, movement/jump/cache host tests |
| Thieves Den | 40% | v0.71 standalone source-derived traversal; material restoration, measured pool, movement/jump/cache host tests |
| Jurassic Jungle | 40% | v0.71 standalone source-derived traversal; material restoration, measured pool, movement/jump/cache host tests |
| Ripto arena | 40% | v0.71 source-derived arena traversal, original spawn and host movement; no boss fight |

Equal-weight location average 44%. Original source location containers 10/10, native source-derived location prototypes 10/10 historically, fully verified continuous original locations 0/10. A per-world session ledger for implemented collectibles is integrated; the full original 90-dragonfly ledger and all minigames remain outstanding. CCC's six tested identities do not mean six verified in a complete playthrough or all CCC challenges completed.

Presentation: equal estimates for original music (10), sound effects (50), dialogue (50), menus and UI (30), average 35%. QA: host regression and reproducible-build coverage (80), actual emulator boot/play (0), real hardware testing (0), full campaign playthrough (0), average 20%.

Use the same rubric for future milestones. A version increment or new synthetic test does not automatically raise completion. Reassess the categories when evidence changes; estimates may decrease if a regression is discovered.

## v0.71 all-level scope audit
All 10 original location containers, 16 minigame containers and 38 auxiliary CNKs inventoried (24,324 records, 6,666 valid VAG headers including duplicates). Six new prototypes earn stage 40, not complete-level credit; unresolved material faces and unselected meshes are explicitly inventoried. Minigames, quests, boss AI, animations, transitions, global 90-dragonfly ledger and actual emulator/hardware playthrough remain incomplete. No independent extra credit for the inventory.

## v0.71 material and minigame asset pass
Six revised discs contain 458,099 packed faces (+50,918), with 20 selected material faces unresolved (Jurassic Jungle highlight map), 460 arena background faces still quarantined, and quantization exclusions retained. All 16 minigame largest scene records exported: 8,611 selected shapes, 6,441 matched, 866 duplicates, 1,304 unmatched, 809,792 triangles. Source candidates only, no minigame gameplay credit. Broader main-scene expansion completed for CCC and arena only. Four prior discs preserved. All 10 main locations and 16 minigames remain in scope.

## v0.72 unified native test disc
All ten v0.71 disc prototypes are preserved as source-compatible virtual volumes on one disc. The native selector loads a level into the shared overlay area; Start returns to the menu and retains the supported collectible/quest state in RAM. Ten snapshot tests and 100 ordered switch-pair host tests pass; original portal gating, save persistence, missing level content and hardware/emulator execution are not implemented or verified. This earns engine integration credit only, not additional location stage credit.
