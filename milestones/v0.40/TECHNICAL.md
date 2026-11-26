# v0.40 — elemental combat diagnostic

Additive workprint, preserving v0.37 game source and v0.38–39 campaign modules. This is a standalone native PS1 diagnostic, not a rebuilt adventure. No original assets are included in this diagnostic. The generated v0.37 private scene, texture and animation banks are still required for full game integration.

- Classic Ripto phase limit: 70% first round, 85% second, 100% third; Expanded uses all three. Fire against ice shield, ice against fire shield, electricity against giant Ripto during exposure. Reference: https://www.darkspyro.net/dragonfly/ripto/?page=1 . Completion percentage is supplied by caller; no gem/quest completion calculator yet. Shield counts, timers and enemy ice duration are provisional. Only full victory is eligible for campaign boss bit; runtime call site still needs wiring.
- Ice freezes an ordinary test enemy; charge shatters it. No world collision, player damage, kite, models, sound or original boss attacks implemented in this diagnostic. 30 nominal ticks/s in NTSC, every other vblank; actual runtime speed not measured.
- Diagnostic screen starts in automatic mode. SELECT toggles manual; TRIANGLE cycles fire/ice/electric; CIRCLE applies a simulated hit; SQUARE charges the ordinary enemy; CROSS resets the encounter. The three top bars show phase, second row shield, third HP, fourth exposure timer (green = vulnerable), lower left ordinary enemy, lower right victory, bottom indicators mode and selected breath. These controls and GPU output have not been emulator-tested.

## Build and verification

`python tools/build40.py` (clang, ld.lld, llvm-objcopy). Output `out40/ETD40.EXE`, `ETD40.bin`, `ETD40.cue`. Boot executable directly in a compatible emulator or open CUE with matching BIN. Disc has no Sony security data; physical hardware requires an authorized homebrew loader. No claim of stock-console boot.

`gcc -std=c99 -O2 -fsanitize=undefined -I src tests/test_combat40.c -o /tmp/c40 && /tmp/c40` — seven boss threshold scenarios and ice lifecycle passed. Repeated prior workprint38 and campaign39 tests (13 + 4 groups passed). Linked MIPS-I executable, 10,240 bytes including header/padding; entry 0x80010000, stack 0x801fff00. 300 Mode2 Form1 sectors validated structurally using the existing encoder. No emulator available; no GPU, controller or physical hardware execution verified. Clang MIPS-I support warning remains.

## Recover exact binary from repository

From repository root, run `python -c "import base64,zlib,pathlib; p=pathlib.Path('milestones/v0.40/ETD40.EXE.zlib.b64'); pathlib.Path('ETD40.EXE').write_bytes(zlib.decompress(base64.b64decode(p.read_text())))"`. To recreate the disc from this EXE, use `tools/disc16.py` functions `iso(exe,{})` and `raw(i,sector)` as in build40.py. The CUE is standard single Mode2/2352 track, index 01 00:00:00.

SHA256 EXE: 3c5e2aa53c6df1da7ace89d03e618317666b9668bdf59627fb125dbcba1036a1

SHA256 BIN: 7156eccfaacc1c2086b3cc6d84058c301c9ac86005742baf5920ff59dbc2a4f6

SHA256 CUE: 32158b4768bf7ce92071be5b8ed5c02126dbfbef63237097ad866c303858e7ca

Next: recover full v0.37 workspace, integrate elemental collision and completion controller with real scenes, reconstruct boss geometry/AI/animations, and verify actual emulator boot. Expanded boss thresholds and locations remain planned.
