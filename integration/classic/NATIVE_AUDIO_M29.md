# Native audio integration — recovered M29 fork

The user's eight-part Definitive Edition 1.2.1 PS2 source archive and recovered M29 source were successfully materialized. The newer v0.74 source remains inaccessible; this is a separate integration experiment, not a replacement or downgrade of the main game.

- 28 full title/world/minigame/boss/credits tracks extracted to native-format stereo ADPCM banks; 57 stereo records total, 56 unique hashes (including cinematic/demo variants); 6,666 valid VAG-header records, 3,411 distinct record hashes extracted. Exact retail comparison and all voice/event mappings remain unverified.
- Dojo track 11,701,116 sample frames at inferred 44.1 kHz; original ADPCM predictor/sample payload preserved, flags adapted for independent 64 KiB stereo chunks. 17,339,520 blocks across 28 tracks verified against source. Original loop points not authenticated.
- M29 game code linked with DMA4 SPU transfers, four 64 KiB music slots, 64 KiB main RAM staging, 51,200-byte voice bank. Existing SFX retained, damage triggers syouch, L2 previews dus10503.wav (diagnostic, not verified quest binding). Music ducking during preview.
- MIPS-I linked RAM 1,873,776 bytes, 26,768 bytes before reserved stack region. 48,894 simulated driver assertions passed under UBSan. All 12,065 raw sectors passed checksum reconstruction; boot EXE, Dojo geometry/texture data and music/voice extents verified. Test disc SHA-256 b6ac160df3eda34ef105f175a4ed61d0fe7f807e4e856d9ed380fcbe6b4f01f8.
- Source patch and test BIN/CUE delivered separately. No original audio assets or disc image committed to GitHub.

Actual emulator/physical execution unavailable in this environment. Synchronous CD reads can stall gameplay; independent chunks may click or gap. Only Dojo has this native music integration. Latest unified campaign integration, full voice/SFX event bindings, authentic loop points and cinematics still outstanding. Overall completion estimate unchanged; no main-branch changes.
