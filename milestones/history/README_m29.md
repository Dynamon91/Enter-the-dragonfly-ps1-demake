# Spyro: Enter the Dragonfly PSX — milestone 0.29

Continues v0.28 with original Dragonfly Dojo Ninja Riptoc geometry, source-positioned encounters and additional basket variants. Native MIPS-I compilation passed; emulator and console execution unverified.

- 25 original Ninja Riptoc positions (15 small, 10 large), all with nearby validated floor candidates. Source main mesh metadata record 567, geometry record 1061, 1,070 triangles reduced to 520. Material 38E2DE97.PXT resolved to Dojo texture group 182; colors baked from original texture at nearest source face centroid. Eyeballs and eyelids not yet bound; rest mesh and materials visibly incomplete. Both variants reuse the body, with a provisional 1.25x large scale.
- Stationary reconstructed combat: enemy faces player, contact damage with 45-update cooldown, small enemies defeated by charge or fire, large enemies by fire. Defeated IDs persist across cache eviction and clear on reset. No original AI, patrol, animation, enemy reward, or player death/respawn logic yet. L2 simulated damage removed.
- All 90 original basket placements (45 basket1, 3 basket2, 40 basket5, 2 basket10) are enabled. All have nearby floor candidates. Rewards 1/2/5/10 inferred from EDF filenames, not verified scripts; total provisional basket value 271. Original basket model shared across variants. Original 10-value gem collectible score checked, with provisional blue-tinted shared geometry instead of incorrect default red rendering. No verified original 10-value mesh yet.
- All 127,733 render triangles, 7,035 collision candidates, source positions, 446 sectors and sky data unchanged. Exactly 45 object-kind fields updated; CRCs refreshed. Original 193 gem IDs preserved. Tests include one representative of each basket variant; no full level playthrough.
- Linked RAM 1,800,416 bytes (1.72 MiB); 100,128 bytes before reserved stack. Seven new tests passed, plus 7 v0.28 and 9 v0.27 tests on inherited host harnesses (23 total). Disc sectors and boot executable readback verified. No FPS claim. Sector reads remain synchronous. Preview is staged host rendering at source locations, not emulator output.
- Disc boots ETD_NINJ.EXE, includes ETD_SKY.EXE and ETD_POOL.EXE as fallbacks. Extract BIN/CUE together and open CUE in DuckStation. Older fallback ignores new basket IDs. No automatic in-game executable switching.

## Rebuild
```
# optional regenerate from supplied original ISO
python tools/enemy29.py /path/to/original.iso
python tools/build_m29.py
python -m unittest discover -s tests -p test_m29.py -v
python tools/preview_m29.py
```
Requires Python, NumPy, Pillow, Clang MIPS-I, LLD and llvm-objcopy. Build uses packaged converted data; original ISO not needed unless re-extracting. Next: original eye binding, animated enemy behavior, doors/NPCs/portals, other levels, hardware boot and performance. Previous engineering estimate 62%; new estimate 63%, not percentage of adventure playable.
