# Spyro: Enter the Dragonfly — PSX milestone 0.19

Experimental native MIPS-I textured streamed traversal. Disc boots ETD_TEX.EXE; the v0.18 flat traversal, v0.16 textured farm gameplay and v0.17 overhead viewer are retained as separate fallback executables. No source PS2 ISO included.

## Changes
- Dynamic opaque 64x64 indexed terrain textures read directly from HUBTEX.DAT via the native CD path. 64 slots, four 8-bit pages at x=320..831, y=256..511, with separate 256-color CLUT rows at x=768, y=16..79. Total terrain cache occupies 288 KiB of VRAM. Actor textures and the double framebuffer remain unchanged. Index and CRC validation occur before GPU upload, and a failed read leaves previously resident texture contents and tags intact. Select highest-use groups when the active sector set needs more than 64; missing textures render as source average colors. The CD fault latch can require a reboot after a transport error.
- Signed original Q10 UVs are clipped before subdivision, then normalized by whole 64-pixel texture repeats. Oversized UV ranges are split along the longest UV edge until they fit in 8-bit GPU coordinates. All 75,653 source triangles pass host UV subdivision decisions (82,830 unclipped output triangles, maximum recursion depth 6). Native render still caps the frame at 10,000 packets and prioritizes Spyro. This does not prove runtime frame rate or elimination of affine warping.
- The full previous 77-step traversal route requires at most 39 textures simultaneously. 41 total texture reads including 32 initial textures, with zero missing required groups, tested via host callbacks and simulated CD registers against the authored disc. Loading remains synchronous, so startup/transition pauses are expected. No texture preload or real CD timing measurements. All 141 source texture entries and CRCs verified.
- Compiled executable 370,688 bytes. Link allocation from 0x80010000 = 1,672,864 bytes (~1.595 MiB), leaving 227,680 bytes before reserved stack region. Static checks only.
- Existing movement, animation, ground collision and transactional world cache preserved. Sparx, gems, baskets, sheep, damage and sound remain in the separate farm build, not yet merged into streaming gameplay. Original alpha, shadow blending and multilayer PS2 materials remain unresolved; dark ground overlays and distant geometry gaps remain visible. Four unresolved materials still use flat fallback colors. No emulator or physical console execution verified.

## Rebuild
Requires Python 3, NumPy, Pillow, Clang (MIPS-I), LLD, llvm-objcopy. From project root:
```
python tools/build_m19.py
python tools/disc19.py
python -m unittest discover -s tests -v
python tools/preview_m19.py
```

## Test
Extract BIN and CUE together, boot the CUE in DuckStation with a suitable BIOS. ETD_TEX.EXE requires the matching mounted disc. D-pad/left analog moves, Square charges, Cross jumps/glides, L1/R1 rotates camera, Select recenters, Start resets. Circle only plays fire animation. HUD row 1: resident geometry blocks, geometry reads, dropped GPU packets. HUD row 2: texture read attempts, missing required groups, failed texture reads. Hold Left + Square from spawn without camera rotation for the host-tested route. Actual hardware may differ. No commercial disc authentication data; real unmodified hardware requires an appropriate homebrew loader.

Next: time-sliced/prefetch loading, original material alpha and shadow modes, merge collectible and companion gameplay with streamed world coordinates, real emulator and hardware testing. Preview is a host reconstruction using actual geometry and texture bank, not an emulator screenshot.
