# Classic v0.53 — transactional portal and spawn checks

Original adventure only; Expanded Mode remains deferred. Additive module, not a rebuilt v0.37 executable. No original assets were recovered in this revision.

The portal controller accepts an initialized v0.52 cache, valid Classic progress ledger, immutable destination scene directory, source-reviewed spawn coordinates and heading, a caller-supplied completion percentage, and exact sector read callback. Boot only into hub, hub to released worlds or Ripto, worlds back to hub. Numeric dragonfly gates retained from earlier campaign work: 1/6/15/25/35/45/55/65. Ripto entry checks >=70% supplied completion. This is a provisional routing policy: actual portal interaction, ability gates, original scripts and completion accounting remain to be integrated. No boss reward is granted on entry. Existing collected IDs are unchanged. Reject invalid ledger counts, extra slots and non-Classic boss flags.

The transition stages cache metadata in a local copy, writes only the inactive terrain arena, and checks a collision surface beneath the proposed X/Z using integer barycentric interpolation, original floor slope policy and a 110-unit tolerance around the expected Y (runtime Y-down). It snaps Y to the nearest qualifying surface. No cache/progress/spawn publication on failure. This is a floor candidate check only, not a capsule/clearance or hazard test. Texture, quest, audio and persistent saves are not part of this transaction yet. The caller must ensure metadata, indices, outputs, progress and callback context are correctly initialized, immutable where required and nonoverlapping with the terrain buffers; no concurrency supported. No additional terrain arena is allocated.

## Reproduction

From repository root with Python 3, NumPy, GCC and Clang/LLD:

    python -m unittest discover -s tests -p 'test_classic*.py' -v
    python -m unittest discover -s tests -p test_scene52.py -v
    python -m unittest discover -s tests -p test_portal53.py -v
    for f in portal53 scene52 sector27; do clang --target=mipsel-none-elf -march=mips1 -mabi=32 -mno-abicalls -fno-pic -G0 -O2 -ffreestanding -fno-builtin -c src/$f.c -o /tmp/$f.o; done
    ld.lld -m elf32ltsmip -r /tmp/portal53.o /tmp/scene52.o /tmp/sector27.o -o /tmp/portal53_linked.o

46 host tests passed (12 new, 34 inherited). The portal fixture includes checks at every threshold, hub/world routing, Ripto entry without victory, invalid ledger, spawn heading and height limits, missing floor, corrupted sectors and read failure on the second block. UBSan-enabled portal tests reported no runtime errors. Synthetic fixtures only, not original levels. Relocatable MIPS-I linked object: 10708 text bytes, zero data/BSS, no unresolved external symbols; compiler warns MIPS-I support experimental. No full executable or emulator run. Existing sector27 warnings remain. Previous v0.37 asset-based game source untouched.

Remaining blockers: original PS2 disc or full v0.37 workspace; real scene bank conversion; texture/quest/audio integration; actual player collision, portal triggers and ability gates; complete Classic playthrough. Archived visual reference: [v0.37 NPC conversion](../../docs/screenshots/v0.37.png), not a new screenshot.
