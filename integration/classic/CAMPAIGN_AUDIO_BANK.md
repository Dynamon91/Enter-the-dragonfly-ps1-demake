# Classic campaign audio bank

Full original-source audit of the user-provided PS2 Definitive Edition 1.2.1 disc (not independently authenticated against clean retail). Source patch delivered as etd_classic_campaign_audio_source.zip in the project conversation.

- All 28 main soundtrack cues bound to source mission identifiers, including nine worlds and 16 minigames; 35 cinematic/demo audio records recovered, six newly identified opening-cinematic streams with unverified language assignments.
- 6,666 VAG references; 3,410 distinct payload/rate combinations. Conservative English/shared selection retains 944 assets, 54,327,296 data bytes; 29 assets exceed 192 KiB and require streaming. Native quest/SFX event bindings are not yet implemented.
- 64 original CNK containers and 24,324 records inventoried; 25,534,442 ADPCM blocks verified. All-language banks total 669,146,352 bytes before game assets, so language selection is necessary for CD capacity.
- Native MUSIC.IDX parser, bank builder, voice selection tool, raw sector generator and verification scripts supplied. 16,416 host validation checks; 15,965 bit corruptions rejected, 419 structurally valid frame-count alterations require SHA verification.
- Recovered v0.29 Dojo playback harness compiled and linked against the full music bank; 1,875,632 bytes linked RAM, 24,912 bytes before reserved stack. All 141,475 sector payloads match cooked image, 263 raw EDC/ECC samples independently matched, all 28 track hashes and boot EXE verified. 332,749,200-byte test BIN SHA-256 901471f6e952d009106df86fa5594f9e688865654f3f0119862f2d8b4b9a8d31.
- Select+R2/L2 changes cue in the harness. Actual emulator and physical SPU playback remain unverified; no gameplay portal integration, original loop-point verification, cinematic playback or new playable campaign levels claimed.
- Full test disc delivered separately in four concatenatable ZIP parts. No original assets committed to GitHub. v0.74 unified source is still inaccessible and has not been overwritten. Full-project completion estimate remains 50%; all outstanding rewards, quests, enemies, minigames, animations, Ripto phases and flight paths remain required.
