# v0.39 workprint — campaign allocation and Atlas

Additive source milestone on top of v0.38, not a new playable PS1 disc. The v0.37 engine, animation compression, and gameplay call sites are unchanged.

- All 120 project slot IDs are assigned exactly once to the existing 30-location registry. Dojo retains 0–9 (including existing 0–3), Dragon Realms 10–19, remaining released realms 20–89 in registry order; expansion slots 90–119. The 21 expansion locations have one or two each. These expansion assignments are new fan design, not recovered placements.
- Original portal thresholds (Dojo through Jurassic Jungle): 1, 6, 15, 25, 35, 45, 55, 65. Applied in both modes. Source: https://gamefaqs.gamespot.com/ps2/555743-spyro-enter-the-dragonfly/faqs/21472 . Hub staged reward counts used in the simulation: https://www.darkspyro.net/dragonfly/dragonrealms/ . Ability/item gates still need real gameplay integration.
- `wp_atlas39` derives per-realm found/total counts without adding persistent state. `wp_collect39` rejects cross-realm awards, boss-arena awards, duplicate captures, invalid slots, and awards during a pending transition. Caller must establish a legitimate in-world reward. No placements are created by this module.
- `wp_request39` / `wp_finish39` recheck eligibility before committing. Classic Ripto access is deliberately delegated to the future completion/phase controller (the existing boss ledger is single-bit and not a reconstruction of the three phases).
- Existing v0.38 Expanded gates unchanged. A fixed-point simulation collects only from eligible scenes, checks boss gates after each award and returns to the source scene. It reaches every exact threshold and all 120 slots. This assumes that all planned packs are validated and their allocated rewards are obtainable; it is not a proof of actual geometry, quests or gameplay reachability. The hub test stages 3/3/4 rewards using visit flags as proxies for ability progression.

## Reproduction (from repository root)

```sh
gcc -std=c99 -O2 -fsanitize=undefined,address -I src tests/test_campaign39.c -o /tmp/camp39
/tmp/camp39
gcc -std=c99 -O2 -fsanitize=undefined -I src tests/test_workprint38.c -o /tmp/wp38reg
/tmp/wp38reg
clang --target=mipsel-none-elf -march=mips1 -mabi=32 -mno-abicalls -fno-pic -G0 -O2 -ffreestanding -fno-builtin -I src -c tests/campaign39_mips.c -o /tmp/camp39.o
size /tmp/camp39.o
```

Observed: 4 new scenario groups and 13 inherited groups passed. Bosses reachable at 30/60/80/95/110 dragonflies; fixed point 120 dragonflies, 30 locations and five wins. MIPS-I object: 2651 text bytes, zero data/BSS, compiler warns MIPS-I support is experimental. No complete executable link or emulator test. No new models, animation, audio, boss AI or collision assets. The source archive includes the additive modules and tests, not the private generated asset banks.

Next: wire validated scene bank loader and actual reward call sites; implement ice breath and Classic Ripto phase controller; verify placement and ability gates with actual scenes. Do not mark planned packs ready until validated.
