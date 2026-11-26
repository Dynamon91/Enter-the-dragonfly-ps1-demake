# v0.47 — native XA audio transport diagnostic

This revision adds a standalone PS1 CD-XA test disc, not a new authentic adventure build. v0.37 remains the original asset-based baseline. Its generated source banks and the original PS2 disc are absent locally. No original game music, voices, maps, or meshes were converted in this revision. The two stereo tones are diagnostic fixtures only.

`src/xa47.h` implements exclusive CD transport ownership, validated file/channel and physical LBA ranges, start/stop, loop-seek, stale position detection, and sticky transport fault. The transport adapter `src/xa47_cd.c` uses polled CD commands (Setmode, Setfilter, Setloc, Demute, ReadS, GetlocP, Pause) and stereo CD input volume. A successful stop mutes and returns to 2048-byte data mode; no simultaneous cd17 access is supported. Controller calls have bounded waits but can block the main loop. An error or timeout fails closed and attempts to mute/pause. A real scene loader must coordinate ownership and handle errors before using the disc. Polling SubQ is approximate; the loop may introduce pauses or truncate audible samples. Seeking, decoder timing, hardware interrupts, filler sectors, and volume are unverified on PS1. No guarantee of seamless loops or concurrent data streaming.

`tools/build47.py` generates two 1.28 s tones, encodes and packs them via v0.46, compiles a MIPS-I EXE, and builds a Mode2/2352 BIN/CUE. Raw XA bank occupies LBAs 300–491, outside ISO file extents but inside its declared volume. 48 guard sectors follow. The diagnostic uses absolute LBAs; the bank is not an ISO file and is not intended for filesystem extraction. This is a structural test disc, not a licensed retail boot disc. Use a compatible emulator or authorized homebrew loader; real stock PS1 boot not verified.

Controls: Cross plays, Circle stops, Triangle switches channel after successful stop. The screen reports approximate drive LBA, loop count, transport state. Fault is sticky until reboot. `tests/preview47.c` renders the same UI with a simulated state; the preview is not emulator capture. No hardware run has occurred.

## Reproduce (repository root)

    python tools/build47.py
    python -m unittest discover -s tests -p 'test_*46.py' -v
    python -m unittest discover -s tests -p 'test_asset_gate45.py' -v
    gcc -std=c99 -O2 -fsanitize=undefined -I src tests/test_xa47.c -o /tmp/xa47 && /tmp/xa47
    gcc -std=c99 -O2 -I src tests/preview47.c -o /tmp/p47 && /tmp/p47 > /tmp/p47.ppm

Observed: 31 inherited Python tests passed, native transport host test passed (mock bus, not MMIO), MIPS-I linking passed with experimental compiler warning. 18,432-byte EXE; 540 raw sectors checked structurally including 48 audio and 48 guard sectors. Both channels extracted independently from the final disc and decoded by FFmpeg PSX STR to stereo 37800 Hz, 1.280 s each. No emulator executable installed; actual CD hardware behavior is unverified. The native diagnostic does not integrate the v0.37 adventure or SPU voice/SFX playback.

SHA256 EXE: 8dba10aa3d584666da50304a13f639c996031eb756061245d29b482039315c4d
SHA256 BIN: 13cad120eee95782768afda253dab27757a5e318ee1b36abf796739caad92f03
SHA256 CUE: b55e343c874c4b3680537fa1d300467bc831a946c0416c64d244b0ca703551ce

Reference: https://github.com/psx-spx/psx-spx.github.io/blob/master/docs/cdromdrive.md

Next: emulator test of diagnostic, original PS2 source/asset bank recovery, SPU ADPCM short sounds and voices, original track mapping, integration of native audio with authentic scene loading. Original released assets and music take precedence over fan reconstructions.
