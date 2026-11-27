# Classic v0.74 — cross-world dragonfly capture

Weighted completion 49.675% (rounded 50%, 50% remaining), previous 49.425%. Engine 75.5%, original locations 46%, presentation 35%, QA 20%. Progression/save rubric score 40 -> 50 for shared per-level capture ledger, no memory-card or level-stage credit. Scope remains all original main levels, 90 dragonflies and sixteen minigames.

Original source: user-supplied Definitive Edition 1.2.1 modded PS2 image, not verified retail. All six new location dragonfly geometry records independently match SHA256 7955d419213990abbc6e2aa544d9a9878d57d7a41248eaa999cc6c7d3a6b5563. Per-world original color metadata resolved by filename hash and texture table. 590 optimized body triangles plus 34 per wing pose, approximate source bind translation, palette centroid color, eyelids omitted. 23 original placements corroborated across duplicate metadata and EDF source caught/found flags. Original waypoint names recorded, flight and bubble trajectories reconstructed. No continuous access or original behavior guarantee.

| Location | Source capture flags | Newly capture-tested |
|---|---|---|
| Dojo | 1:203/205/206 | 3 |
| Cloud 9 | 4:200/201/204/205/206 | 5 |
| Monkey Monastery | 5:200/202/205/206 | 3; 202 floor missing |
| Honey Marsh | 6:200/205/206/207 | 4 |
| Thieves Den | 7:203/204/205/206 | 4 |
| Jurassic Jungle | 8:201/206/207 | 1; 201 locked by flag 26, 207 floor missing |

R2 switches fire/bubble, Circle fires. Original explicit gate remains locked until puzzle implemented. No fake unlock flags. Other source-specific access routes, doors and hazards incomplete. 20 actual new native bubble capture routines exercised using host floor and memory CD callbacks, wrong-breath rejection, repeated capture prevention, capture session count and snapshot restoration verified. Test repositions player; no continuous playthrough. 35 total reward identities exercised across current and earlier tests, 38 represented including two blocked and one gated. Prior 15 not retested as gameplay this turn. Nine collectible-bearing worlds now participate in session reward count; boss arena preserved.

Reward inventory read-only scan of 26 source main/minigame CNKs: 267 source references across 86/90 candidate 200..209 slots (groups 0..8). Missing direct evidence 5:203, 6:201, 7:201, 8:203. Flag structure is audit hypothesis; references are not proof of actual distinct collectible names or award behavior. All minigames still unfinished.

All 10 overlays compiled, minimum headroom 74784 bytes in Dojo. 57 original asset-file entries unchanged. All ten state snapshot tests, 100 ordered switch pairs, 30 injected load failures passed. Independent native logical ISO rebuild byte-identical; 27838 raw sector payloads matched. No emulator, BIOS, hardware or continuous full adventure execution.

BIN SHA256 1c1349a4ceccf05199436502fd94d5a39de9d5514319338f371ec45bf59814d3
ISO SHA256 2ad9a882d41e73da69b353f642b9ed1e488075b24ac8814ca0c7be373b51c1e2
Test ZIP SHA256 0b5b3a57bd5d2af6f68f49c59cab986fc95ce24e1fd186663c4a69e226b04265
Source ZIP SHA256 f296ae629d114c6c721ebda92a1de5429864929fe3a2205e69b3b5a50f8616f6

Both archive CRCs passed. Complete authoritative downloadable source includes tested native runtime, generated headers, extraction and reward audit tools, host tests, exact input banks, preview and nested v0.73 source and v0.71 test snapshots. Public repo tracker and selected source; proprietary banks excluded. Rebuild:
    python tools/build72.py inputs rebuilt previous_v071_test.zip
    cc -O3 tools/raw72.c -o raw74
    ./raw74 rebuilt/logical.iso rebuilt/ETD_CLASSIC74.bin

Host preview maps actual packed source terrain and original placement coordinates. Next all-world quest and minigame rewards, missing collision/gates, original NPCs/enemies, animations, boss combat, permanent save and emulator execution.