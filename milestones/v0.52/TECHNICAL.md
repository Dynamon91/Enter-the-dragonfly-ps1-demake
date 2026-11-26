# Classic v0.52 — transactional scene-bank loading

Classic only. Expanded content frozen. The original v0.37 asset-based hub/Dojo source remains unchanged. No new original scene or playable disc was produced: the original PS2 ISO and full generated v0.37 workspace remain absent.

`src/scene52.c` and `.h` implement a scene-specific ETDI v1 directory parser and synchronous transactional neighborhood loader using the unchanged `sector16_load` in `src/sector27.c`. The scene ID (0–8 released locations, 9 Ripto arena), material count, sector count and immutable index are supplied by the caller. Face and object counts are derived from validated directory entries. Requires contiguous sector extents, bounded world coordinates, matching record lengths, no reserved index flags, and nonempty render/collision data. Maximum index 28,672 bytes (477 entries); 28 selected blocks and 460 KiB of sector-rounded data per neighborhood, 1792-unit selection radius at 512-unit anchors, matching the v0.27–37 Dojo limits. Caller supplies two separate, nonoverlapping 460 KiB buffers, two immutable scene index lifetimes where needed, and a read callback tied to the requested bank. Index memory, callback context and cache metadata must not overlap either arena. The cache must be initialized before use. Read callback must read exactly the requested sectors or fail. All selected block sizes are checked before reads. The active page and metadata are published only after all selected blocks pass the original reader; failed read, CRC, bad extent, empty neighborhood or budget overflow leaves the active page intact.

This is an additive loader for future scene changes, not a drop-in replacement for the asynchronous v0.37 cache or a full portal transaction: it does not load texture/quest banks, validate spawn collision, preserve game state, check unlocks or perform level-specific script binding. It synchronously reloads a neighborhood; CD latency has not been measured. No full-bank duplicate face-ID certification or source authenticity verification is performed by the runtime module. Existing v0.37 memory limits are policy ceilings, not proof of final linked RAM fit. Integration must account for a second index and all other resident assets and reuse the existing cache arena rather than allocating a second one.

## Reproduction

    python -m unittest discover -s tests -p 'test_classic*.py' -v
    python -m unittest discover -s tests -p test_scene52.py -v
    clang --target=mipsel-none-elf -march=mips1 -mabi=32 -mno-abicalls -fno-pic -G0 -O2 -ffreestanding -fno-builtin -c src/scene52.c -o /tmp/scene52.o
    clang --target=mipsel-none-elf -march=mips1 -mabi=32 -mno-abicalls -fno-pic -G0 -O2 -ffreestanding -fno-builtin -c src/sector27.c -o /tmp/sector52.o
    ld.lld -m elf32ltsmip -r /tmp/scene52.o /tmp/sector52.o -o /tmp/scene52_linked.o

34 host tests passed (10 new, 24 inherited). New scenarios exercise two differently sized synthetic banks through the real sector reader, rollback after a second read failure, payload corruption, invalid extents/bounds, empty neighborhood, overflow rejection before reads, no output on invalid index, Expanded ID rejection and arena overlap. Compiler emits pre-existing misleading-indentation warnings in sector27.c and experimental MIPS-I warning. Combined relocatable MIPS-I object: 5752 text bytes, zero data/BSS, no undefined symbols; no PS-X EXE or emulator run. Fixture geometry is synthetic, not a replacement for released assets.

Next: recover source assets, validate actual level banks, integrate per-scene texture and collision spawn verification, wire portal and progression state into the authentic v0.37 runtime. Continue the original 90-dragonfly campaign before adding any extra content.

Archived authentic preview: [v0.37 NPC conversion](../../docs/screenshots/v0.37.png). No new in-game screenshot in this loader-only revision.
