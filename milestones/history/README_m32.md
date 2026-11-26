# Spyro: Enter the Dragonfly PSX demake — milestone 0.32

Startup memory optimization based on v0.31, with original asset bytes unchanged. The engine loads a version-specific `BOOT32.DAT` from the CD into the existing geometry arena before any sector is resident. Seven initialization-only payloads (Spyro and fire GP0 command streams, sky and Ninja palettes/pixels, SPU sample bank) are moved out of linked main RAM. The entire bank is checked against a compiled-in CRC32 and exact length before GPU/SPU upload; a failed boot bank gives a red diagnostic screen. After the uploads, the temporary pointer is cleared and the same arena is used normally for sector streaming. The existing SPU failure behavior remains audio-optional.

## Measured build and validation
- Native MIPS-I linked allocation: 1,700,528 bytes vs 1,856,992 in v0.31. Net RAM savings 156,464 bytes (152.8 KiB).
- Available before reserved stack: 200,016 bytes (195.3 KiB), previously 43,552 bytes (42.5 KiB).
- Boot bank: 157,152 bytes, padded to 77 CD sectors, read in three bounded requests (32 + 32 + 13). CRC32 bbae529e. Exact previous payload bytes, no geometry or animation reduction. Native EXE: 436,224 bytes vs 591,872.
- Six new host tests, 18 distinct inherited tests, 31 invocations including duplicated imported test classes. All passed. Tests cover byte equality, length/CRC/failure rejection, destination canaries, mock SPU data transfer and scratch reuse, linked symbol/lifetime checks, and disc EDC/ECC/fallback checks.
- No new playable content. CD startup remains synchronous; extra seek/read latency is unmeasured. No emulator or real hardware run, no measured FPS. Original AI, collision completeness, lighting and facial animation remain provisional.

## Build
With the v0.31 full workspace present, run `python tools/build_m32.py` and `PYTHONPATH=tools:tests python -m unittest test_m29 test_m30 test_m31 test_m32 -v`. Open `build_m32/play/ETD_PSX_M32.cue` with a PS1 emulator. `ETD_BOOT.EXE` requires its matching disc. `ETD_AI.EXE` and `ETD_POOL.EXE` are fallbacks. Standard controls unchanged. The test disc does not include Sony security data; physical unmodified console boot requires an authorized compatible loader. Source-only GitHub checkout still requires local converted assets from the full workspace.

## Next priorities
Dragonfly capture, bubble breath, NPCs and portal transitions, then additional levels. Engineering progress estimate 66%, not a measure of playable adventure content.
