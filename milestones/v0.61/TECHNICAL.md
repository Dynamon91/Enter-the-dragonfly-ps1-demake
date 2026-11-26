# Classic v0.61 — original barn rescue

Classic-only milestone. Original source: user-supplied Definitive Edition 1.2.1 (modded PS2 image), recovered L_2_CC.CNK SHA256 96e6088141808bbb0f46e9af53327ff4eabaf0408e5f06b7b339a749813ab2c9.

## Source recovery
EDF directory record 1125 (104 entries) maps hashed filenames to offsets in record 719. Verified original fuse flag 48, door trigger script 159 sets rescue flag 0, left door sets flag 1 after opening, barn cow 3 sets flag 7 at escape completion. All five original herding definitions use flags 8–12 and target Farmer Dean within 850 units. Recovered the five original escape spline control-point arrays in records 379 and 1012, corroborated byte-for-byte; six control points each and five matching barn cow placements. Door meshes metadata/geometry 392/499 and 649/445, fuse 662/835. 335 source triangles, 278 optimized triangles. Original material bindings recovered (two doors share group 283, fuse group 69), three CRC-checked blocks in CCCBRN.DAT. Existing assets unchanged.

## Native implementation
Uses actual existing flame particles and terrain floor/path query at original fuse tip (3133,-414,3756). Ignition sets flag 48; reconstructed 20-tick fuse delay then flag 0; 16-tick door rotation then flag 1; five cows follow piecewise-linear paths at nominal source-derived speed; after all escape, flag 7 is set (conservative adaptation of original cow 3 flag). Herding field cows hidden until then. Uses existing cow model, no new skeletal animation. Source spline interpolation replaced by linear segments; Y shift of 68 units aligns source control points to placed cow roots. Door pivot, timing, fuse hit band and thin closed doorway collision proxy are approximations. No original fuse sound, complete TNT prop, explosion effect or original camera sequence; shared effect used on ignition. Bill's source conversation VM records one pending reward, not a captured dragonfly. Actual five-cow herding AI is not implemented. No extra content.

## Validation
Native EXE 604160 bytes; linked main RAM 1862800 bytes; 37744 bytes headroom before reserved stack. 2591 raw disc sectors verified structurally. Prior six banks byte-identical. Rebuild from self-contained archive produced byte-identical EXE/BIN. Host UBSan test uses actual existing flame emitter and real collision bank from exterior position (3500,-400,3756); ignition after six ticks, five spline endpoints reached in 142 total ticks, gate checks, Bill's reward once, reset clears state, three read and three CRC failures rejected. 267/270 sampled escape positions have qualifying floor within 110 units; three missing floor samples remain, scripted escape path does not use runtime collision. Not full playthrough or collision accuracy. Prior 12288 dialogue branch combinations, 23 mocked voice uploads and original spawn dialogue trigger checks passed. No emulator/hardware execution, actual frame rate unverified.

## Rebuild
From downloadable v0.61 source archive:
    python tools/build_ccc61.py base previous barn out
    gcc -O2 -fsanitize=undefined -I out tests/barn61_host.c base/src/sector27.c -o /tmp/barn61
    /tmp/barn61 out/CCCSECT.IDX out/CCCSECT.DAT out/CCCBRN.DAT
Source extraction:
    PYTHONPATH=base/tools python tools/barn61.py /path/to/L_2_CC.CNK actors/bindings.json previous barn_new
Full test harness, converted assets and reference renderer in local archive. Public repository contains code and technical notes, not proprietary banks. Host preview shows original barn terrain and recovered props before/after opening, not emulator capture.

EXE SHA256 39680439a1ee6cba601002fba9fdcdd411cc64670d9c4438a718b6901f7bea3b
BIN SHA256 8821622acb24b8adf629db8f85a604a6e4d60b5c7fe7b58d0e32c94d8d558f15
Source ZIP SHA256 6a2201e94fc6291c7c5a1a8d9900f1ca6d86308858756d5c894d84543e7a2c6a
Test ZIP SHA256 cbeaeaccf835fc314b2b7a0f993850fb10f0ee8518336838da4ca9dfd1d27bf3
Both ZIP integrity tests passed. Next: floor gaps, original cow animations, collision-aware herding navigation, actual dragonfly reward capture and emulator validation.
