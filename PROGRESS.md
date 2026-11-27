# Classic demake completion — v0.70

**47% estimated complete / 53% remaining.** Scope: the released original adventure, all 90 dragonflies, Dragon Realms, eight released adventure levels and Ripto's arena. Expanded Mode is excluded. This is a subjective engineering estimate with an explicit weighted rubric, not a measured fraction of code, assets, or elapsed time. Source availability is tracked independently and earns no level-conversion credit by itself. Host tests are not emulator/hardware verification.

| Category | Weight | Estimated completion | Weighted points |
|---|---:|---:|---:|
| Core PS1 engine | 25% | 69% | 17.25 |
| Original locations and quests | 55% | 44% | 24.20 |
| Audio, menus and presentation | 10% | 35% | 3.50 |
| Testing and release readiness | 10% | 20% | 2.00 |
| Total | 100% | | 46.95 (rounds to 47%) |

## Evidence and scoring

Core: equal-weight estimates for native compiler/disc packaging (100), terrain streaming (80), textured graphics (80), movement and input (90), collision (80), camera (70), actor animation (60), combat and breath abilities (60), scene transitions (50), progression/save support (20). Average 69%. Scene transition modules exist but are not yet integrated into a connected adventure; no persistent memory-card save implemented.

Location milestones: 0 = source only; 20 = converted static bank; 40 = native traversal prototype; 60 = subset of quest mechanics implemented; 80 = full original gameplay integrated; 100 = fidelity and continuous playthrough verified. The older hub and Dojo prototypes are credited at their highest evidenced stage, not claimed as part of the latest standalone CCC disc.

| Location | Stage credit | Evidence |
|---|---:|---|
| Dragon Realms | 40% | Earlier native hub traversal |
| Dragonfly Dojo | 60% | Earlier native terrain, quest/capture/dialogue prototype |
| Crop Circle Country | 60% | v0.65 native traversal, six dragonfly identities, two transport rides and enemy/urn interactions exercised through host tests |
| Luau Island | 40% | Native traversal, recovered sky and swimming; 35 urns, 14 vases, 24 underwater gem identities, three free dragonflies, five switches and three gate state changes host-tested; major quest access routes incomplete |
| Cloud 9 | 40% | v0.70 standalone source-derived traversal; partial terrain and movement/jump host tests |
| Monkey Monastery | 40% | v0.70 standalone source-derived traversal; partial terrain and movement/jump host tests |
| Honey Marsh | 40% | v0.70 standalone source-derived traversal; partial terrain and movement/jump host tests |
| Thieves Den | 40% | v0.70 standalone source-derived traversal; partial terrain and movement/jump host tests |
| Jurassic Jungle | 40% | v0.70 standalone source-derived traversal; partial terrain and movement/jump host tests |
| Ripto arena | 40% | v0.70 source-derived arena traversal, original spawn and host movement; no boss fight |

Equal-weight location average 44%. Original source location containers 10/10, native source-derived location prototypes 10/10 historically, fully verified continuous original locations 0/10. Global integrated collectible ledger and full original minigames remain outstanding. CCC's six tested identities do not mean six verified in a complete playthrough or all CCC challenges completed.

Presentation: equal estimates for original music (10), sound effects (50), dialogue (50), menus and UI (30), average 35%. QA: host regression and reproducible-build coverage (80), actual emulator boot/play (0), real hardware testing (0), full campaign playthrough (0), average 20%.

Use the same rubric for future milestones. A version increment or new synthetic test does not automatically raise completion. Reassess the categories when evidence changes; estimates may decrease if a regression is discovered.

## v0.70 all-level scope audit
All 10 original location containers, 16 minigame containers and 38 auxiliary CNKs inventoried (24,324 records, 6,666 valid VAG headers including duplicates). Six new prototypes earn stage 40, not complete-level credit; unresolved material faces and unselected meshes are explicitly inventoried. Minigames, quests, boss AI, animations, transitions, global 90-dragonfly ledger and actual emulator/hardware playthrough remain incomplete. No independent extra credit for the inventory.
