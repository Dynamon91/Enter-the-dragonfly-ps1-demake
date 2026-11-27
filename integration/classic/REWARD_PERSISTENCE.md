# Classic reward persistence milestone

Standalone patch tested on host and compiled to MIPS-I. Not yet merged into the v0.74 game.

- 90 reference slots across nine collection areas; 12-byte bitmap.
- Explicit native-ID mapping generator; partial binding allowed, duplicate/unknown keys and IDs rejected.
- Two 32-byte auxiliary records with mapping revision tag, sequence number and CRC-32. Recovery selects newest valid record with wrap-safe serial arithmetic.
- Host C99 tests: 116,228 assertions, 90 synthetic award round trips, 23,040 single-bit record corruptions rejected.
- Seven Python mapping tests passed.
- MIPS-I object: 2,204 text bytes, 0 data/BSS, no undefined symbols. Not a linked game or emulator test.
- 0/90 actual native IDs bound in this patch. The previous reported 35 tested awards are not independently reverified.

Integration must preserve existing engine save IDs and treat the original save as authoritative. Bind after confirmed award, not on spawn. Validate complete map before replacing any HUD counters. Use an explicitly reserved auxiliary save area if needed; independently write/read the inactive record, validate it before adoption, and rebuild auxiliary state from authoritative flags on mismatch or ambiguity. The patch does not implement physical memory-card I/O or recover original reward triggers. Never derive Ripto's campaign percentage directly from dragonfly count alone.

Source archive delivered separately in the project conversation. No main-branch changes.
