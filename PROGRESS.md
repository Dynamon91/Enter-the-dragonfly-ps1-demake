# Classic demake completion — v0.65

**31% estimated complete / 69% remaining.** Scope: the released original adventure, all 90 dragonflies, Dragon Realms, eight released adventure levels and Ripto's arena. Expanded Mode is excluded. This is a subjective engineering estimate with an explicit weighted rubric, not a measured fraction of code, assets, or elapsed time. Source availability is tracked independently and earns no level-conversion credit by itself. Host tests are not emulator/hardware verification.

| Category | Weight | Estimated completion | Weighted points |
|---|---:|---:|---:|
| Core PS1 engine | 25% | 68% | 17.00 |
| Original locations and quests | 55% | 16% | 8.80 |
| Audio, menus and presentation | 10% | 35% | 3.50 |
| Testing and release readiness | 10% | 20% | 2.00 |
| Total | 100% | | 31.30 (rounds to 31%) |

## Evidence and scoring

Core: equal-weight estimates for native compiler/disc packaging (100), terrain streaming (80), textured graphics (80), movement and input (85), collision (75), camera (70), actor animation (60), combat and breath abilities (60), scene transitions (50), progression/save support (20). Average 68%. Scene transition modules exist but are not yet integrated into a connected adventure; no persistent memory-card save implemented.

Location milestones: 0 = source only; 20 = converted static bank; 40 = native traversal prototype; 60 = subset of quest mechanics implemented; 80 = full original gameplay integrated; 100 = fidelity and continuous playthrough verified. The older hub and Dojo prototypes are credited at their highest evidenced stage, not claimed as part of the latest standalone CCC disc.

| Location | Stage credit | Evidence |
|---|---:|---|
| Dragon Realms | 40% | Earlier native hub traversal |
| Dragonfly Dojo | 60% | Earlier native terrain, quest/capture/dialogue prototype |
| Crop Circle Country | 60% | v0.65 native traversal, six dragonfly identities, two transport rides and enemy/urn interactions exercised through host tests |
| Luau Island | 0% | Source available |
| Cloud 9 | 0% | Source available |
| Monkey Monastery | 0% | Source available |
| Honey Marsh | 0% | Source available |
| Thieves Den | 0% | Source available |
| Jurassic Jungle | 0% | Source available |
| Ripto arena | 0% | Source available; synthetic workprints do not count |

Equal-weight location average 16%. Original source location containers 10/10, native source-derived location prototypes 3/10 historically, fully verified continuous original locations 0/10. Global integrated collectible ledger and full original minigames remain outstanding. CCC's six tested identities do not mean six verified in a complete playthrough or all CCC challenges completed.

Presentation: equal estimates for original music (10), sound effects (50), dialogue (50), menus and UI (30), average 35%. QA: host regression and reproducible-build coverage (80), actual emulator boot/play (0), real hardware testing (0), full campaign playthrough (0), average 20%.

Use the same rubric for future milestones. A version increment or new synthetic test does not automatically raise completion. Reassess the categories when evidence changes; estimates may decrease if a regression is discovered.
