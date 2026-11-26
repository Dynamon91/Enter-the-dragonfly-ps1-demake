# Classic v0.62 — collision-checked cow herding

Original adventure only. Uses five original herding cow placements and EDF flag assignments recovered in v0.61. The original AI solver is not recovered. A bounded offline A* searches the existing source-derived collision triangles on a 128-unit grid with intermediate 32-unit floor samples, slope and 70-unit height-change checks. 122 total waypoints, five endpoints within 600 horizontal units of Farmer Dean. Native controller follows four substeps per segment, queries actual resident floor before moving, and pauses outside 1100-unit player neighborhood, during dialogue, or if floor is unavailable. Fire or charge hit activates an idle cow only after escape flag 7. Repeated hits cannot grant reward or restart route. Each arrival independently sets original flags 8–12 only within the source 850-unit target range and vertical tolerance. Dean's original script records one pending reward when all five flags are set. No dragonfly capture ledger integration yet. The original cow model, original initial yaw and existing rendering path are reused; movement is not skeletal animation. Dynamic obstacle, wall/capsule clearance, full route/player traversal and native frame rate remain unverified. The three prior barn escape floor gaps are not fixed.

## Verification

Host test completed the earlier barn rescue with actual existing fire emitter, then activated all five field cows with the same fire emitter. It repositions the simulated player to follow cows and loads the authentic collision bank through a memory callback, not a full continuous playthrough. 463 additional movement ticks after initial hit tick, all five arrivals and individual flag checks, remote pause, no stationary hit, no duplicate activation, original Dean reward exactly once, reset and locked state passed. Charge detection is implemented but not separately exercised end-to-end. 12288 dialogue branch cases and 23 original voice payload tests rerun successfully. All seven previous asset banks byte-identical. Native MIPS-I executable 610304 bytes; linked RAM 1868416 bytes; 32128 bytes before reserved stack; all 2594 raw CD sectors structurally regenerated and compared. Independent build produced identical EXE and BIN. No emulator or hardware execution.

## Reproduction from local source snapshot

    python tools/build_ccc62.py base previous herd out
    python tools/herd62.py previous barn/barn61.json herd_new
    gcc -O2 -fsanitize=undefined -I out tests/herd62_host.c base/src/sector27.c -o /tmp/herd62
    /tmp/herd62 out/CCCSECT.IDX out/CCCSECT.DAT out/CCCBRN.DAT

Public repository contains four new implementation files, all matched to tested local Git blob hashes. Full host test, preview script, generated waypoints, source-derived assets and previous native source dependencies in local archive. Preview is an actual host reference scene using original models/textures and a collision-derived route plot, not an emulator screenshot; sky rendering is omitted in this reference view, not removed from native build.

EXE SHA256 5eae01ac0a0ab7f04de4c1d704c12bdf8d1e01e848fb1923566a6f4153f2ea14
BIN SHA256 fe4be60b14095117c115787eb4ecc3dfa2a7ce33d8aedb366a8097d9bb6ff076
Source ZIP SHA256 e9a12d97fcd8f23a6002eb48c027dbcf502e4212b89d0d293201337b41b3cfb4
Test ZIP SHA256 78c8f54d18081663884a7a978e35a5cc5b1bd3a6f34514583e0a44d7d76fbc29
Both ZIP integrity tests passed. Next: actual dragonfly rewards, cow animation, repair barn escape collision gaps, UFO event, and actual emulator testing. Expanded Mode remains deferred.
