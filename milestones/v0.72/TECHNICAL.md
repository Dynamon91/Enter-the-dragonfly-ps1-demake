# Classic v0.72 — unified ten-location native test disc

Weighted overall Classic estimate 47.825% (48% rounded, 52% remaining), up from 47.20%. Core engine 72.5%, locations 44%, presentation 35%, QA 20%. Engine scene transitions score 50 -> 60 and progression/save score 20 -> 35. No original level-stage, minigame or presentation credit for a developer selector.

## Integration
All ten existing original-location prototypes now packaged on a single Mode2 Form1 native PS1 test disc. Original source is user's supplied Definitive Edition 1.2.1 modified PS2 image, not verified retail. Dragon Realms v0.21, Dragonfly Dojo v0.29, Crop Circle Country v0.65, Luau Island v0.69, Cloud 9, Monkey Monastery, Honey Marsh, Thieves Den, Jurassic Jungle and Ripto arena v0.71 retained. Earlier v0.37 Dojo milestone remains on main, not integrated into this disc. No source banks removed; auxiliary older EXEs preserved but not selector entries. All 16 minigame geometry exports and original content inventory retained in nested v0.71 source archive; none converted to playable minigames in this turn.

Resident loader links at 0x801e0000, fixed return vector 0x801e0010, end 0x801e62c0. Ten child executables load at 0x80010000 and link below 0x801e0000. Each virtual ISO retains local PVD/root layout; original polled CD reader receives bounded sector offset adapter. Loader checks known boot name, child PVD, header, size, fixed entry address and CRC before handing off; low RAM loaded through uncached alias, BIOS instruction cache flush before launch. Native transfer and CD timing not tested in emulator. The high-RAM session at 0x801ea000 reserves ten 4096-byte snapshot slots (41140 bytes including headers); 48716 bytes between session end and stack top. Level overlay RAM headroom before resident region at least 99184 bytes (Luau). Start in level replaces old reset with return-to-selector; reentry uses source spawn. Retain actual per-world gem IDs and consumed container states, Dojo defeated-enemy flags, CCC quest flags/barn/herd/UFO/lifts/combat/dragonfly state, Luau props/gates/dragonfly state. Projectiles cleared and uncommitted conversations canceled on resume. Invalid status blocks overwriting the previous snapshot. Checksum detects accidental corruption; not a durable or transactional memory-card save. Menu counts only currently implemented rewards, not a fully populated 90-identity campaign ledger. No authentic portals, progression locks, original menu or persistent memory card.

## Verification
Ten native overlays compiled and linked. Native snapshot tests pass for all ten worlds (756–2420 bytes actual state; first eight final runs with UBSan, last two uninstrumented). Actual native structs and collectible methods compiled with host hardware routines discarded; test state injected, not full gameplay. Ten virtual volumes, 77 directory extents, 100 ordered switch pairs/200 loads, 30 injected read/header/payload failures passed with the extracted native open routine using memory CD, host destination and stubbed jump. 27749 raw sectors payload/address/sync verified; 755 EDC/ECC samples independently byte-compared to previous Python encoder. Prior asset contents compared byte-for-byte during packaging. Prior movement and quest tests are inherited, not rerun as a continuous native playthrough. No physical PS1 or emulator boot verification; no frame-rate, audio, actual controller/BIOS or cache-flush testing. No retail boot security/license data authored.

## Artifacts
Local test ZIP SHA256 4de2ab9f5b3fe7bbe83b4de63ab40a0840c6009d33e05dfaab8625c4c88ee7ae
Local source ZIP SHA256 737bf393d1c471144ffa215c60fdfa938163a93b08b9e614009a139789e0dfdd
BIN SHA256 0cd63d0c6501ec316232a78aa024515950f7148bc24da378b5c85bee4e14b757
Logical ISO SHA256 d220fdb53d63f1128a2bd5cb532008310f28d4c2d3343a07282c559afee85dc3
Both archive CRC checks passed. Source archive is authoritative, includes native loader and snapshot glue, build/test tools, exact ten prior overlays' C and headers, previous v0.71 source and test bundles, all converted inputs, manifests and preview. Original PS2 ISO not required for this build. GitHub branch contains selected runtime and progress/technical notes; no proprietary converted banks published there. Menu preview from actual UI drawing code using host rectangle renderer, not an emulator screenshot.

Rebuild:
    python tools/build72.py inputs rebuilt previous_v071_test.zip
    cc -O3 tools/raw72.c -o raw72
    ./raw72 rebuilt/logical.iso rebuilt/ETD_CLASSIC72.bin

Next across all original locations: source portals and unlocks, upgrade historical Dojo integration, full global collectible ledger and memory-card save, minigame mechanics, missing actors/animations/scenery/quests and boss fight, emulator verification. Expanded mode deferred; original scope unchanged.
