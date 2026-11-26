# Classic v0.50 — released adventure first

The user has prioritized completing the original adventure before extra content. Expanded Mode and new bosses, worlds, dragonflies, custom music and the synthetic arena campaign are frozen. Keep their workprint branches intact, but they are not release candidates. The original v0.37 native hub/Dojo prototype is the game baseline. v0.25 recovered 661 distinct Dojo terrain meshes, 127733 nondegenerate triangles, 52 uniquely matched materials and 351 placements. This does not imply complete level coverage. Earlier work used the user-supplied Definitive Edition 1.2.1 PS2 ISO; verify any differences against a retail dump before describing the result as a faithful retail reconstruction.

## Generalized source geometry converter

The v0.25 terrain extractor had a hardcoded Dojo container and metadata record. tools/classic_mesh50.py inventories extracted CNKs and allows an explicit container, metadata record and name selection. It checks directory bounds, shape metadata, declared packet count, exact packet offset, strip lengths, UV extent and finite values, and source bounding boxes within 0.01 source units. Equivalent payload matches are deduplicated. Ambiguous or missing matches are reported and block export by default. A deliberate --allow-partial exports selected validated meshes only, with remaining gaps recorded. Output geometry.npz carries original local coordinates, triangle indices, UVs, source material hashes and part IDs. Source SHA256 and match records are written to report.json. It does not infer world transforms, material assignments, textures, collision, placement, scripts, or missing geometry; signature heuristics require real-world review. Degenerate triangles are omitted. Source format coverage is not verified outside fixtures; original Dojo converter is preserved.

From repository root, Python 3 and NumPy:

    python tools/recover48.py extract /path/to/source.iso /path/to/new/recovered
    python tools/classic_mesh50.py inventory /path/to/new/recovered > classic_inventory.json
    python tools/classic_mesh50.py recover /path/to/new/recovered/SPYRODAT/CHUNKS3/L_1_DD.CNK 359 '^(dd_|shadow_dd|shadow1[|]shadow_dd|shadow_st|shadow_sub|sh_mid2|sub_05|shadowend)' /path/to/new/dojo_output
    python -m unittest discover -s tests -p test_classic_mesh50.py -v

The Dojo command uses the prior known metadata record and name selection; it is not a new run on authentic data. For all other worlds use inventory and confirm the correct metadata record and terrain name selection before recovery. Ten synthetic fixture tests passed. No original ISO or v0.37 archive was found locally, no new authentic level or PS1 executable produced, no emulator execution.

## Classic completion gates

1. Recover exact prior source archive or original source ISO; reproduce v0.37 and verify hub/Dojo actual emulator execution.
2. Convert remaining released scenes: Crop Circle Country, Luau Island, Cloud 9, Monkey Monastery, Honey Marsh, Thieves Den, Jurassic Jungle, Ripto arena. The released source assets have priority; review individual terrain matches, transforms, material mapping, texture transparency, collision, spawn placements and scripts.
3. Integrate original portal gates, 90 dragonflies, quests, minigames, boss phases, movement, save/resume, original music/voice and sound effects. Use the separate audio modules only after native playback validation.
4. Full Classic completion and regression playthrough in emulator, then compatible PS1 hardware; actual frame rate and RAM/VRAM/SPU budgets must be measured.

Original asset reference preview: [v0.37 NPC poses](../../docs/screenshots/v0.37.png) and [v0.31 Ninja Riptoc animations](../../docs/screenshots/v0.31.png). Both are archived host previews, not new screenshots.
