# Classic scene audio and conversation audit (M29 integration fork)

Source and incremental disc update delivered in the project conversation.

- 62 CNK containers with 279 source sound table records, 7,985 sound/stream rows; 3,673 unique filename/rate matches, 85 ambiguous, 4,227 unresolved. Counts include languages and duplicates.
- 101 conversation records across 10 containers, 310 Say calls, 268 of those referring to IDs in augmented global voice map. Source flags and branch references indexed, not executed.
- Prior 400 dialogue matches retained. 23 added candidate English matches supported by scene sound tables and numeric filename variants, matching rates. Alternate-take identity and listening verification pending. 205 unresolved lines remain.
- Five original Dojo effects (source record 611): hurt 17, normal fire 33, jump 16, basket break 103, death 39. Preload 94,400 bytes in existing 96 KiB effects allocation; 3,904 bytes free. Source effect layout in scene_sfx.h. Inherited gem sounds remain. Death gong is not game-over implementation. 5,919 host SFX checks (5,889 ADPCM blocks), 66,385 dialogue checks.
- MIPS-I build 1,883,184 bytes linked RAM, 17,360 bytes before reserved stack. All 168,015 sector payloads, 263 EDC/ECC samples, 28 music hashes checked. Update installer tested twice, all 16 ISO files equal fresh build, SHA256 6eb4b6b020156b416b22fca2a02c9a6786f8c00c3ad2e93709ca7a8ab4e075f2.
- Native execution and SPU audio not verified. NPC quest triggers, all-world gameplay, remaining objectives and cinematics remain incomplete. Latest v0.74 unavailable; no downgrade or main branch changes. Full completion estimate stays 50%. No audio assets or executable committed.
