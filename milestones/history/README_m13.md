# Spyro: Enter the Dragonfly — PSX milestone 0.13

Continuation of v0.12. Native PS1 farm-sector prototype, not a complete game. Original PS2 ISO is not distributed. Earlier milestones retained.

## New in 0.13
- Sparx-assisted gem pickup: direct contact takes precedence (180 world units); Sparx seeks the nearest eligible uncollected gem within 360 units and collects it when within 26 units of its target point on all axes. Four intermediate heightfield checks, vertical limit, and invalid-floor rejection reduce accidental collection through gaps. This is prototype behavior, not the original PS2 AI. The sparse heightfield cannot prove exact line-of-sight or full wall collision. Three original placements remain enabled. Each pickup produces exactly one direct or assist event; Start resets state and stops SFX.
- Original `gemhit1.vag` and `csprxpu.vag` ADPCM payloads preserved byte-for-byte. Startup-only SPU manual-transfer bank: 16,064 bytes at byte address 0x1000, four rotating voices (4–7), pitch 0x0800 (22.05 kHz), no reverb. Direct and assisted events use different samples (provisional event assignment). Bounded polling disables audio when initialization fails rather than indefinitely stalling. SPU register/FIFO mock verifies transfer layout, pitch, key-on and key-off, and timeout behavior; no emulator or hardware playback was performed.
- Native startup explicitly clears linked BSS rather than relying on loader state. No changes to existing source-derived geometry, textures, rig, animation data, terrain or gem placements.
- Native MIPS-I build: 638,976-byte PS-X EXE; linked RAM allocation 1,746,432 bytes from load address, 154,112 bytes before the reserved stack region. BIN/CUE: 334 sectors; EDC/ECC and executable readback verified. 83 host regression tests passed. No emulator executable installed; real boot, audio timing, controller timing, GPU output and FPS remain unverified. Physical unmodified consoles need an appropriate homebrew loader.
- Host-rendered preview shows Sparx approaching and collecting a green gem without moving Spyro. Terrain lighting, material layers, shadow artifacts, original Sparx materials and animation remain incomplete.

## Build and test
Requires Python 3, NumPy, Pillow, Clang MIPS-I, LLD and llvm-objcopy.
```
python tools/build_m13.py build_m13/play
python tools/disc13.py build_m13/play
python tools/preview_m13.py build_m13/play
python -m unittest discover -s tests -v
```

## Controls
Extract BIN and CUE together and open ETD_PSX_M13.cue, or load ETD_SFX.EXE directly in DuckStation. D-pad/left stick move; Cross jump/glide; Square charge; Circle fire; L1/R1 camera; Select recenter; Triangle toggle legacy fire targets; Start reset. Walk toward the three available gems; Sparx can collect them within range and on supported terrain. The original pickup sound should be triggered if SPU initialization succeeds; this needs runtime verification.

## References
PSX-SPX, Sound Processing Unit: https://psx-spx.consoledev.net/soundprocessingunitspu/ (manual write protocol, addressing, voice pitch, registers).

## Next
Original breakable baskets and enemy actors, full collision, materials/depth ordering, sector streaming, other breath abilities, soundtrack/XA, actual emulator and real console verification.
