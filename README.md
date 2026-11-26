# Spyro: Enter the Dragonfly — PS1 demake / expanded vision

**Work in progress — experimental native PlayStation prototype.**

![Shared engine estimate: 71%](https://img.shields.io/badge/shared%20engine%20estimate-71%25-blue)

Unofficial fan development project targeting the original PlayStation (MIPS R3000A, GTE, 2 MiB main RAM, 1 MiB VRAM, 512 KiB SPU RAM). Classic Mode aims to reconstruct the released adventure; Expanded Mode explores the originally ambitious vision with separately labeled new designs.

## Current priority — Classic adventure first (v0.50)

Expanded content is deferred until the original adventure is complete. The original v0.37 hub/Dojo build remains the baseline; v0.38–0.49 workprint labs are separate diagnostics. The new generic terrain recovery tool is ready for real-source validation when the original PS2 ISO or full v0.37 archive is recovered. See [Classic v0.50 technical notes](milestones/v0.50/TECHNICAL.md).

## v0.37 — Lossless animation optimization

![v0.37 decoded character poses and memory comparison](docs/screenshots/v0.37.png)

*Host C-decoded pose data and source-derived reference rasterization, not an emulator screenshot.*

- Lossless grouped bit packing preserves all 245 Spyro matrix frames and 36 NPC samples exactly; 1,200 random frame seeks and blend transitions verified.
- Same eight-frame matrix checkpoint interval; two cached NPC samples per character. No added runtime CD reads or reduced animation sampling.
- Native MIPS-I compilation passed; 1,798,352 bytes linked RAM, 102,192 bytes before reserved stack (99.8 KiB, up from 33.4 KiB).
- Six new and 21 inherited selected tests passed, 27 total. Both ZIP archives validated.
- Existing dialogue, quest logic, enemy poses and textures retained.
- 90 Classic / 120 Expanded ledger slots; [proposed campaign registry](campaign33.json) contains 26 adventure levels, four homeworlds and five boss encounters.

Both modes share the current Dojo prototype. The codec trades additional integer decoding operations for reduced resident memory; real PS1 decoder cost and frame rate are unmeasured. No new levels, boss encounters or abilities in this revision. The percentage is an engineering estimate, not playable campaign completion. Emulator and physical hardware execution remain unverified.

## Source checkpoint

See [technical notes](milestones/v0.37/TECHNICAL.md), [compression report](milestones/v0.37/pack_report.json), [memory report](milestones/v0.37/report37.json), [test results](milestones/v0.37/test_results.txt), [archive checksums](milestones/v0.37/ARCHIVES.md) and [historical milestones](milestones/history).

This is a source archive, not a standalone buildable checkout. Generated proprietary asset banks, intermediate builds, executables and disc images remain separate. Build with locally converted assets and the local PS2 source disc.

## Next work

Kite animation, exact quest triggers, original voice playback, ice breath, portal transitions, released Ripto fight and separately identified expanded content packs.

Spyro and Enter the Dragonfly belong to their respective rights holders. This independent project is not affiliated with them.
