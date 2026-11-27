# Classic v0.65 — transport and combat

Full-project scope: original Classic adventure. Weighted tracker 31.30%, rounds to 31% (previous 30.55%). Engine estimate 68%, original locations 16%, presentation 35%, QA 20%. No credit for expansion or asset availability alone.

Source-derived data: six named UFO platform spline arrays, 43 control points, corroborated between CCC CNK metadata records 379 and 1012. EDF directory 1125/payload 719 confirms original call/return flags 15–18, distinct one-way and to-and-fro paths and source speed categories. Original placed platform geometry and textures reused. The recovered source is the user's Definitive Edition 1.2.1 PS2 disc (modded, not verified unmodified retail). No new original meshes in this milestone.

Native transport: aimed lightning calls each platform; player boards via jump/landing. A real cache transition must succeed before moving the rider across anchor boundaries. For reachability under the current jump physics, both original lower dock elevations are adapted downward to the sampled terrain floor minus 80 units (dock 1 original -701, adapted -84; dock 2 original -842, adapted -282). The six source flight splines remain unchanged; docking is an added motion. A 30-tick wait while aboard initiates the return/shuttle. Original spline interpolation, platform bounce/rotation physics, trigger timing and exact dock heights are not reproduced. Deck support uses a circular proxy; falling off uses a nearby lower terrain surface. No full swept-volume/wall clearance guarantee.

Combat: source EDF vulnerability subset for ordinary flame, charge and lightning. 10 ray-gun Riptocs resist charge, seven space cows vulnerable to charge/flame/lightning, 27 blue urns require charge (or other original super abilities not implemented), six chickens drop a healing butterfly. Original gem1 and gem5 rewards for 17 enemies and 27 urns, 152 gem value in total, collected once per placement. Chicken butterflies use existing model and proximity recovery. Simplified stationary facing and ray projectile behavior, source-derived treasure amounts, not exact AI/attack scripts/animations. Health protection and spawn respawn are implemented but no full lives/game-over flow or save support. Source 905 interaction flag and higher breath abilities not fully integrated.

Host tests on the real packed collision bank: both aimed lightning calls, original route endpoints, actual jump boarding, rider transport (79 and 390 movement ticks respectively), walking dismount and return tested. All 50 placement pickup tests use direct defeat activation, with no duplicate rewards; separate real fire, charge, lightning and hostile projectile damage checks pass. Tests reposition player between scenarios, not continuous playthrough. 12,288 dialogue combinations, 23 original voice uploads, original spawn trigger, 8,914 neighborhood audit and 308 transitions, earlier barn/herding and six dragonfly rewards rerun and pass. Prior quest host test uses an actor-visibility stub for new render hook. All eight prior banks byte-identical. No emulator or actual hardware boot/timing validated.

Native EXE 741376 bytes; linked RAM 1453088 bytes; 447456 bytes (436.97 KiB) before reserved stack. 2685 raw CD sectors structurally verified. Independent rebuild byte-identical. Source archive is authoritative complete local snapshot; GitHub includes new runtime, extraction/build tools and technical notes. The local source archive includes the new host test and preview renderer; these are not separately committed in this checkpoint. Original/converted proprietary assets not pushed to public GitHub.

Rebuild from source archive:
    python tools/build_ccc65.py base native64 platform out
    python -c "from pathlib import Path;p=Path('out/play65.c').read_text();Path('out/movement65_test.h').write_text(p[p.index('static int update18('):p.index('#define NFACE20')])"
    gcc -O2 -fsanitize=undefined -I out tests/interaction65_host.c base/src/sector27.c -o /tmp/interaction65
    /tmp/interaction65 out/CCCSECT.IDX out/CCCSECT.DAT

Optional original recovery:
    PYTHONPATH=base/tools python tools/platform65.py /path/to/L_2_CC.CNK actors/bindings.json platform_new

EXE SHA256 02acf383e12541a3bf8b4c1eea99b22954739e94f7105fb5f5b8d9acb30fa045
BIN SHA256 a89e02d87e7a1201c9f2c0b99cc3fbe9188d90877457d363e92d765ff6891634
Source ZIP SHA256 2cdd820a808e13cd09514db0357532752a28f7dffb6a4e522c86a0f92ed38f80
Test ZIP SHA256 de141c1766d1c4a1acf5785cd0802779e22a209a40eda3438e15963a28d5f3cc

Both archive integrity tests passed. Host model preview and original spline elevation plots, not emulator capture. Next: missing CCC challenge/minigame and original character animation, plus parallel extraction of remaining original locations. Expanded content deferred.
