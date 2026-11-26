# v0.45 — original asset and audio intake guard

Authentic v0.37 scene and asset conversion is the main adventure baseline. v0.38–44 remain diagnostic branches. No new PS1 executable or actual music/asset extraction in v0.45: original PS2 disc and full m37 archive are not present in the current workspace. Refer to ASSET_RESTORATION.md and milestones/v0.37/ARCHIVES.md.

Minimum inventory: 80 logical entries (27 Classic, 53 additional Expanded), including 30 scenes and corresponding music assignments, 5 boss arenas and tracks, 9 model/model-bank groups, and original SFX bank. Entries are not individual files or counts of completed assets. Reuse one verified track when appropriate. All entries initially missing; the catalog records current local availability, not historical extraction success. Released scope requires ETD retail provenance. Expanded music accepts retail ETD, authentic unused ETD recordings, or new original compositions; other Spyro games may be donor models for Expanded only. Original game and donor assets remain local. Source references, source and output SHA-256, and explicit review flags are required. For audio intake use a local decoded 16-bit PCM WAV and an explicit [start,end-exclusive] music loop in sample frames. Reject silence, malformed/truncated PCM and invalid loops; flag full-scale samples and discontinuous loops for listening review. This checks metadata and intermediate audio, not PS1 format validity or authenticity of self-attested flags.

Run Python >=3.11 from repository root:

    python -m unittest discover -s tests -p test_asset_gate45.py -v
    python tools/asset_gate45.py assets45/intake.json /path/to/local/assets --mode classic
    python tools/asset_gate45.py assets45/intake.json /path/to/local/assets --mode expanded

16 synthetic fixture tests passed. Empty current intake correctly blocks Classic (27) and Expanded (80). No copyrighted audio or meshes included. Release gating is currently a standalone preflight; it must be called by the future authentic game builder before release packaging. Runtime tests remain required: texture seams, collision, animation, portal loading, save/resume, XA playback/looping during CD reads, SPU sound-bank capacity, VRAM/RAM budgets, emulator and physical hardware. Stream original music via CD-XA or another measured streaming strategy; store short sounds in SPU ADPCM; do not load full PCM songs in the 512 KiB SPU RAM. Preserve tempo, pitch, channels, cue order and loop points; avoid composing replacements for existing tracks. No claim of zero bugs.
