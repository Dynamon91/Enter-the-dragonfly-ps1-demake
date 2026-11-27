# Classic v0.75 — three-form boss and original flight routes

Weighted completion 50.90% (rounded 51%). Engine 76%, main locations 48%, presentation 35%, QA 20%. Boss arena stage increases 40 to 60; core combat 60 to 65. All 90 original reward identities and all 16 minigames remain in scope. No credit for script inventory alone.

Ripto source EDF health 3/20/5; two shields 10. First shield vulnerable to flame, second to ice; final stuck phase lightning. Three original body meshes: 1292, 1292, 2057 native triangles; source palette centroid colors, weapons and rigid parts missing. Body geometry metadata/geometry records 546/267, 563/50, 159/544. Original source modded Definitive Edition 1.2.1, not verified retail. Reconstructed stationary attack loop, projectile and shield proxies, stage handoff and timings. Native host test real floor, fire particles, ice/lightning rays, timed jumps and victory flag checks, final player health 2. Player repositioned near boss. Not original exact AI, arena transitions, portal unlock or ending cutscenes. 14 original animation curve payloads, 16632 keys, 24 remaining; not playing in native build.

All 13 named original flight locator chains across latest six capture worlds decoded; 233 source points corroborated in duplicate metadata. Native flight controller linear interpolation, nearest start locator, looping and speed/range scale reconstructed. Two circuits per route host-tested. Interception tests on real floor and native projectiles pass 22/23 (3 Dojo, 5 Cloud 9, 4 Monkey Monastery, 4 Honey Marsh, 4 Thieves Den, 2 Jurassic Jungle). Both previous floor-blocked identities now tested at later route positions; JJ flag 8:201 remains gate-locked. Tests reposition player and sample route phases; not continuous chase or emulator. 37/90 rewards exercised across milestones (previous 15 carried forward, not all retested); 38 represented. 53 still require implementation/verification.

All 26 main/minigame source containers have resolved EDF directories, 533 filtered actor definitions, 238 dialogue script records, 88 award branches including 27 minigame branches (24 candidate minigame reward pairs). Source conditions and flag writes inventoried; reused scripts require context. No new minigame mechanics, general enemy AI, full quest VM or animation playback in this milestone. No emulator installed; package repository network unavailable.

All 10 native overlays compiled. Minimum RAM margin 73376 bytes. Prior 57 asset files unchanged. 100 ordered switch pairs, 30 injected failures, 10 snapshots, full three-phase boss test, 22 moving capture tests passed. Independent logical ISO rebuild byte-identical; all 27900 raw sector payloads compared. No actual MIPS/GPU/SPU/BIOS/hardware verification.

BIN SHA256 dd0b786d528a0e2470bf6d381a88dabcad45fcd779bd2390a8162d0ef92a2527
ISO SHA256 34c5aa19151e32808c1b4168b7ab3054bea0d7b29b4f437e5e5003317c143e72
Test ZIP SHA256 ffb1ba62cec3e0df781caf01ff519b04912e28db44ccfc4fd03bfcaf653251c9
Source ZIP SHA256 acb82586eb525584caaf7d47fc84ac924516e4f0f28d424eec12ffcc895fbe51

Both ZIP CRC checks passed. Full authoritative source archive contains actual runtime, generated headers, source audit data, extraction and verification tools, original earlier converted inputs and previous v0.74 source snapshot. Public GitHub contains selected source code and technical notes, not proprietary asset banks. Rebuild:
    python tools/build72.py inputs rebuilt previous_v071_test.zip
    cc -O3 tools/raw72.c -o raw75
    ./raw75 rebuilt/logical.iso rebuilt/ETD_CLASSIC75.bin

Next: native minigame mechanics and actual award triggers, complete quest chains, enemy AI and rig playback, remaining reward IDs, original boss movement and effects, persistent save, actual emulator/hardware test.