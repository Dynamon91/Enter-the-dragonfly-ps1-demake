# v0.38 workprint — campaign routing foundation

Additive module based on v0.37 (e9a09d0eab840f00b25162a9d7e2fa66bbbb6b8d). Not a new playable disc. Keep v0.37 intact.

- `src/workprint38.h` uses existing `Progress33` and project IDs from `campaign33.json` (30 levels including four hubs; five boss IDs).
- Classic mode isolates 90 shared dragonfly slots and released levels/Ripto; Expanded mode permits all 120 slots. The existing ledger is unchanged. Classic portal thresholds remain unverified and are intentionally not invented here.
- Readiness is independent of design existence: a loader must set a bit only for a validated loadable pack. Request/finish separates destination validation from ledger mutation. A failed load leaves route and visited flags unchanged. A real loader must stage or restore scene assets itself; this module does not perform CD I/O or render portals.
- Entering a boss arena does not award a victory; combat must call `wp_defeat38` after the genuine defeat. A return request preserves the source level. Duplicate wins are rejected.

## Proposed Expanded campaign gates

| Encounter | Dragonflies | Prior boss wins |
|---|---:|---|
| Crush | 30 | none |
| Gulp | 60 | Crush |
| Ripto | 80 | Crush, Gulp |
| Gnasty Gnorc | 95 | Crush, Gulp, Ripto |
| Ripto and Gnasty | 110 | all four |

Emerald/Enchanted Forest opens at 12, Baked Alaska at 36 plus Crush, Cutthroat's Cove at 64 plus Crush and Gulp. New expansion sectors use corresponding gate groups, with Gnorc-region adventures at 90 and Twin Tyrants Keep at 100. Thresholds, boss ordering and new encounters are fan-designed, not recovered original scripts. Joel Goodsell's 2018 interview supports the historical Gnasty/Ripto direction and Emerald Forest design: https://thewumpagem.wordpress.com/2018/10/01/the-enter-the-dragonfly-investigation-part-ii-interview-with-joel-goodsell/ . Other cancelled level names are reported in https://www.badgamehalloffame.com/spyro-enter-the-dragonfly/ . The existing campaign registry's provenance labels are preserved.

## Verification

From repository root:

```sh
gcc -std=c99 -O2 -Wall -Wextra -fsanitize=undefined,address -I src tests/test_workprint38.c -o /tmp/testwp38
/tmp/testwp38
clang --target=mipsel-none-elf -march=mips1 -mabi=32 -mno-abicalls -fno-pic -G0 -O2 -ffreestanding -fno-builtin -I src -c tests/workprint38_mips.c -o /tmp/wp38_mips.o
size /tmp/wp38_mips.o
```

Observed: 13 scenario groups passed; MIPS-I little-endian relocatable object, 1610 bytes text, 0 data, 0 BSS. Clang warns MIPS-I support is experimental. Route state is six bytes; readiness struct is eight bytes on the tested ABI. No whole-game linking, emulator boot or physical PS1 performance testing. The host tests simulate readiness and captures; actual collectible placement must still be checked for progression deadlocks. No new scenes, textures, animations or boss AI were created.

## Integration next

Wire real portal request and validated CD bank transitions to the current Dojo/hub runtime; ensure the existing scene remains usable on failure. Complete ice breath and kite animation in parallel with released level/boss extraction. Establish a per-level dragonfly allocation and validate all gates against actual obtainable captures. Do not set readiness for planned packs. The v0.37 generated source assets and disc image are needed for a full build; the public source checkpoint excludes them.
