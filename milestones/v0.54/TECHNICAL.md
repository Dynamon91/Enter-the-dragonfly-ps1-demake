# Classic v0.54 — transactional terrain and texture transitions

Classic adventure only. Expanded content remains deferred. This is an additive native module, not a rebuilt v0.37 executable or a new level conversion. The original PS2 source ISO and complete generated v0.37 workspace remain absent locally.

`src/texture54.c` and `.h` combine the v0.53 portal controller, v0.52 terrain loader and ETTI/ETDT v1 texture-bank validation. The caller supplies the immutable scene-specific material-to-group mapping, texture index, separate read callbacks and a 6144-byte scratch buffer. Index entries must be sorted and unique, with exact contiguous three-sector extents. Every material maps to an existing group or an explicitly reviewed flat-color material (-1). The module reads destination arrival terrain, validates the spawn floor, enumerates the distinct texture groups referenced by its render records, and validates each required texture block against its index and CRC. It stages the 4608-byte payloads in the unused tail of the inactive terrain arena. No third terrain arena or permanent texture payload buffer is allocated. Scene-local group IDs are never assumed to identify identical textures across scenes. Maximum 64 resident texture slots and 540 group IDs; transitions exceeding either the slot or remaining staging capacity are rejected rather than silently substituting missing textures.

The commit boundary is conditional on caller guarantees: rendering stopped, GPU fenced, synchronous infallible upload callback using the original tex19 slot layout, and valid nonoverlapping buffers and metadata. Before the first upload, failures preserve active terrain, texture mapping, progress and spawn output; inactive staging bytes may change. Once uploads begin there is no hardware failure rollback. The module does not yet implement the actual GPU uploader, ongoing texture streaming while walking, transparency/UV fidelity review, script/audio transition coordination or integration with the old renderer's Tex19 mapping. Large arrival neighborhoods may need an alternative staging strategy. Two existing 460 KiB terrain arenas, stack usage, scratch, indices and all other assets must fit the actual linked executable; native object compilation is not a complete RAM-budget verification.

## Reproduction

From the repository root with Python 3, NumPy, GCC, Clang and LLD:

    python -m unittest discover -s tests -p 'test_classic*.py' -v
    python -m unittest discover -s tests -p test_scene52.py -v
    python -m unittest discover -s tests -p test_portal53.py -v
    python -m unittest discover -s tests -p test_texture54.py -v
    for f in texture54 portal53 scene52 sector27; do clang --target=mipsel-none-elf -march=mips1 -mabi=32 -mno-abicalls -fno-pic -G0 -O2 -ffreestanding -fno-builtin -c src/$f.c -o /tmp/$f.o; done
    ld.lld -m elf32ltsmip -r /tmp/texture54.o /tmp/portal53.o /tmp/scene52.o /tmp/sector27.o -o /tmp/texture54_linked.o

58 host tests passed (12 new, 46 inherited). New tests exercise different payloads with identical group IDs across scenes, used-only loading, shared groups, explicit flat color, missing mapping, duplicate index, invalid extent, CRC/read failure rollback, lock checks, slot and arena overflow. Tests use synthetic fixture textures and a mock upload callback, not original PS2 assets. MIPS-I combined relocatable object: 14212 text bytes, zero data/BSS, no unresolved symbols. Clang warns that MIPS-I support is experimental; pre-existing sector27 indentation warnings remain. No full PS-X EXE or emulator/hardware execution.

Next: recover original source data, integrate the real GPU upload path and per-scene material tables into the authentic adventure, verify actual neighborhood budgets, texture cache movement and portal triggers. Finish original 90-dragonfly campaign before expansion.

Archived authentic visual reference: [v0.37 NPC conversion](../../docs/screenshots/v0.37.png). No new in-game screenshot in this module-only revision.
