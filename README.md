# Spyro: Enter the Dragonfly — PS1 demake

**Work in progress — experimental native PlayStation prototype.**

![Engineering estimate: 65%](https://img.shields.io/badge/engineering%20estimate-65%25-blue)

This unofficial fan development project targets the original PlayStation (MIPS R3000A, GTE, 2 MiB main RAM, 1 MiB VRAM, 512 KiB SPU RAM). The goal is to reconstruct the adventure using a native fixed-point engine and locally converted assets.

## Current milestone: v0.31 — Animated Ninja Riptoc combat

- Dragon Realms and Dragonfly Dojo terrain and texture streaming.
- Source-positioned gems, baskets and Ninja Riptocs.
- Original sky environment and sampled character animations.
- Reconstructed enemy detection, windup, jump attack, recovery and persistent defeat.
- Native MIPS-I compilation and 18 recorded host regression tests passed.
- Approximately 1.77 MiB linked main RAM; 42.5 KiB before the reserved stack.

The percentage is an engineering estimate, not the percentage of playable original content. Emulator boot, real hardware operation, performance and complete adventure progression remain unverified.

## Repository status

This initial checkpoint records selected project source and milestone documentation. It is **not yet a complete buildable checkout**. The full v0.31 development ZIP and BIN/CUE test disc are retained separately; see [archive manifest](milestones/v0.31/ARCHIVES.md) for their SHA-256 checksums. Original PS2 disc images and extracted proprietary game assets are not committed.

## Next work

Memory optimization, additional NPCs, dragonfly capture, bubble breath, portal transitions and emulator verification.

Spyro and Enter the Dragonfly belong to their respective rights holders. This independent project is not affiliated with them.
