# Classic v0.63 — native dragonfly capture, quest accounting and memory optimization

## Original source
The recovered user-supplied Definitive Edition 1.2.1 PS2 image is modded, not a verified unmodified retail dump. L_2_CC.CNK source SHA256 96e6088141808bbb0f46e9af53327ff4eabaf0408e5f06b7b339a749813ab2c9. Dragonfly geometry record 353 is byte-identical to records 404, 590, 906 and 1149. Green/yellow/red variants use metadata records 487/273/710, identified by source body palette and EDF geometry names. The extractor matches actual mesh bounds, material references and source UVs, clusters positions and samples source texture palettes into RGB555 face colors. Shared main mesh: 590 triangles, three 34-triangle wing-pose meshes. The active pose submits 624 triangles before clipping. Original facial/wing geometry retained with approximate bind transforms; eyelids omitted; no original shader, full texture mapping, skeletal animation, or exact flight waypoint solver. The preview uses original geometry and packed terrain in a host reference rasterizer, not an emulator.

## Original dragonfly progression
Source flags are authoritative and the HUD counts distinct committed identities, not the number of times a dialogue Give opcode runs.

| Source identity | Caught/reward flag | Found flag | State |
|---|---:|---:|---|
| Green starting dragonfly | 200 | 211 | Bubble capture tested |
| Yellow dragonfly | 201 | 212 | Bubble capture tested |
| Upper barn green dragonfly | 203 | 214 | Bubble capture tested |
| Dean's herding reward | 204 | — | Original conversation award |
| UFO red dragonfly | 205 | 216 | Hidden until flag 23; capture tested with simulated unlock only |
| Bill's rescue reward | 206 | — | Original conversation award |

Original flags are recovered from EDF directory 1125 / payload 719 and original farmer scripts. Original placed dragonfly coordinates converted to Y-down; floor-relative hovering and approximate animated wing cycling are reconstructed. R2 toggles fire/bubble, Circle emits selected breath. A 12-particle bubble pool uses existing floor/path checks and a reconstructed translucent ring, no extra VRAM. Unique captures mark Found/Caught only after collision. The two Give branches credit their original committed reward flags directly, consistent with the scripts; no fabricated loose dragonfly for those rewards. The three free dragonflies and two quest awards passed the host test. UFO encounter and lightning/cannons not yet implemented; unlocking flag 23 in the test verifies only subsequent red dragonfly capture. No continuous full-level playthrough, original capture cutscene, unique name popup, global 90-dragonfly ledger, memory card saves or exact original breath-selection UI. Classic only.

## RAM and barn corrections
Exhaustive selection sweep of all 8,914 occupied 512-unit anchor cells: maximum 163840 bytes (160 KiB) per neighborhood and 19 blocks. Retain 192 KiB per active/pending bank, shared 384 KiB pool instead of 920 KiB. 536 KiB reclaimed from terrain allocation; 525232 net bytes gained after added code/data. This reduced budget is specific to CCC and must not be applied to other levels without their own measured bounds. Host test checked 308 actual cache transitions, including peak windows and failure rollback/retry. Original terrain and collision banks unchanged.
The earlier floor gap on cow 2's escape segment 3 is avoided with one extra waypoint (3840,-400,3770), between the existing source control points. Original endpoints and flags remain intact. 515 actual barn cow positions were checked against the real collision bank during escape. The prior three missing floor samples on the straight segment are avoided, not repaired in the original collision mesh. Runtime still uses scripted path interpolation; no swept-volume or dynamic obstacle proof. Previous 463 herding movement ticks and all five arrivals remain valid.

## Verification
- All three free dragonflies caught by the implemented projectile, from floor-checked nearby player positions. Negative fire-mode, repeat hit, locked UFO, reset tests passed. Test harness repositions the simulated player between challenges; it is not a continuous playthrough.
- Barn fire hit, 515 escape floor checks, five original endpoints, herding fire hits and 463 floor-checked herding ticks; both original farmer rewards credited once.
- 12288 dialogue combinations, 23 mocked SPU uploads, original spawn dialogue trigger rerun and passed.
- 7 prior asset banks byte-identical. Native executable 632832 bytes, linked RAM 1343184 bytes, 557360 bytes (544.3 KiB) headroom before stack reservation. All 2605 Mode2 raw sectors validated. Independent rebuild produced byte-identical EXE and BIN. MIPS-I compile only, no emulator or hardware execution.
- EXE SHA256 0329e0bfb8b0ccdfa9c6cee799af83f2d9fc9b5cf6ce302522d80d853978dd1d
- BIN SHA256 a5c6d688127cc2c0644d7119c22ce57d9bd026c88e08e3a1141c91bff525dcc7
- Source ZIP SHA256 416cb83368d4bac2c709d8ab3fe019417dbb6d055a45fae15218cecd9895563d
- Test ZIP SHA256 2bc306e75fae6e4882975fe58145c848866b33b44d2572f55863aef1ac49c8b5

Both ZIP CRC tests passed. The downloadable source archive contains all prior generated inputs, converted assets, original-data manifests, host test harnesses, reference preview and reports, and is self-contained for native rebuild without ISO. Public GitHub contains code and technical notes, not proprietary banks.

## Reproduction
    python tools/build_ccc63.py base native62 dragonfly out
    gcc -O2 -fsanitize=undefined -I out tests/capture63_host.c base/src/sector27.c -o /tmp/capture63
    /tmp/capture63 out/CCCSECT.IDX out/CCCSECT.DAT out/CCCBRN.DAT
    gcc -O2 -fsanitize=undefined -I out tests/cache63_host.c base/src/sector27.c -o /tmp/cache63
    /tmp/cache63 out/CCCSECT.IDX out/CCCSECT.DAT

Original extraction using local CNK and previous bindings:
    PYTHONPATH=base/tools:tools python tools/dragonfly63.py /path/to/L_2_CC.CNK actors/bindings.json dragonfly_new

Next: actual four-cannon UFO chain (source cannon scripts 121/730/665/1029, flags 3–6; UFO death raises 23), lightning breath and source ability progression, enemy combat and full original character animations, remaining released levels, persistent global progression, emulator execution. Expanded content remains deferred.
