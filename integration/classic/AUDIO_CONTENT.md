# Mandatory Classic audio and content coverage

Standalone audio cue controller delivered in the conversation patch. Host tests: 14,321 assertions; MIPS-I compile: 916 text bytes, zero data/BSS; state and command each 4 bytes. Three Python tests verify asset table and validation. No game integration or playback verification yet.

29 reference cues (28 music tracks plus intro audio): nine world themes, sixteen minigame/speedway themes, title, intro, Ripto, and credits. Each original cue is required, with no synthetic fallback. Original voices, effects, ambience, jingles, opening and ending cinematics also required. Source identity and exact loop points must be checked against retail.

The proposed asset pipeline takes local extracted files and encodes stereo 32 kHz SPU-ADPCM (VAGi), with ordinary data sectors and provisional 32 KiB RAM staging/32 KiB SPU ring. Encoder and retail audio unavailable in this session; conversion and CD/SPU playback are untested. Validate actual disc budget, seek arbitration, buffer underruns and native CPU cost before acceptance.

100 content acceptance checks and 90 reward reference entries provided separately; all are audit targets, not proof of completion. Classic Mode must retain every released location, NPC, quest, minigame, speedway, boss phase, collectible, animation, menu and cinematic. Original assets, native IDs, playback driver, emulator verification remain blockers. Expanded Mode is separate. No main-branch change or increase in overall completion estimate.

References: https://downloads.khinsider.com/game-soundtracks/album/spyro-enter-the-dragonfly (track metadata), https://github.com/WonderfulToolchain/psxavenc/blob/main/README.md (format documentation).
