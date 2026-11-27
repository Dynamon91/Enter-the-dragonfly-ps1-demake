# Classic playback adapter and disc index

Source and tests delivered as etd_classic_audio_driver_patch.zip in the project conversation. Standalone adapter connects the earlier cue controller and streaming queue; no native executable changed.

- 37,180 host assertions passed (also under UBSan), 1,805 mock reads, 1,569 mock uploads, 396 mock playback chunks.
- MIPS-I compilation passed: 2,152 text bytes, no data/BSS, queue and memcpy/memset dependencies.
- Five Python disc-index tests passed using a synthetic ISO: all 29 cue extents, hash corruption, missing loop annotation, wrong cue policy, incompatible ISO format.
- Drain old reads/uploads before reusing staging or SPU slots; latest accepted start wins; partial final chunk frame count passed to backend.
- Driver requires 4 KiB staging and eight stereo slots (32 KiB SPU); not measured in the linked game.
- Disc-index builder expects cooked ISO9660 with M00.SPU through M28.SPU in root, single extent, hash matching encoded bank. Loop metadata must be chunk-aligned; no invented defaults.

Real CD/SPU backend, voice completion, precise gapless playback, original music/voice/effect assets, cinematic playback, engine integration and emulator tests remain outstanding. Pause occurs at chunk boundary, repeated I/O failure needs watchdog, caller must synchronize cue state on EOF/errors. All original content remains required. Overall progress unchanged; no main-branch changes.
