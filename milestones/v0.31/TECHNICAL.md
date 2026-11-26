# Spyro: Enter the Dragonfly PSX demake — milestone 0.31

Native MIPS-I experimental Dragonfly Dojo executable, based on v0.30. Original model/eyes/UVs and four sampled animation clips; jump-forward and die-tumble added. 34 animated poses + rest pose, 323 vertices, 596 triangles. All ten original curve payloads retained. The new fixed-point behavior is a reconstruction, NOT the original PS2 AI. Source IDs and initial placements are unchanged.

## Changes
- `src/enemy31.h`: 25 persistent encounter states, 18-update windup, 34-update jump, 24-update recovery, 60-update death; path-checked movement, 460-unit square leash, shared 45-update damage cooldown, ground-return behavior. Motion uses a procedural height arc and ignores original root motion. Small charge vulnerability applies near ground, fire remains effective; large enemies require fire.
- `tools/enemy31.py`: repeat original extraction with jump and tumble poses, delta-compressed without loss relative to the quantized frames.
- `tools/build_m31.py`: native executable and MODE2/2352 disc; previous ETD_EYES.EXE and hub ETD_POOL.EXE included. Same Dojo geometry and texture banks.
- `tests/test_m31.py`: host C tests against disc geometry, trace of both enemy sizes, death persistence, leash and missing collision, lossless pose decoding, disc sector checks. 5 new + 7 inherited M29 + 6 inherited M30 tests passed. Attack traces: first damage at update 32 in both, 220/280 units displacement respectively. See build_m31/play/test_*_results.txt.

## Build / play
`python tools/enemy31.py <original ISO>` (if regenerating assets), `python tools/build_m31.py`, `python -m unittest discover -s tests -p test_m31.py -v`. Open the CUE in a PS1 emulator. Existing controls: D-pad/analog movement, Square charge, Circle flame, Cross jump/glide, L1/R1 camera, Select recenter, Start reset. A matching disc is required for streaming.

RAM from load address: 1,856,992 bytes (1.771 MiB), 43,552 bytes before reserved stack region. No added VRAM texture allocation. Native compile and host validation only; no emulator or console available. No measured FPS. Enemy behavior, timing, vertical arc, pose interpolation, facial animation, lighting, collision completeness and CD latency remain provisional. No original AI script decoded. New preview is a depth-buffer host render of actual converted poses, not a native screenshot.
