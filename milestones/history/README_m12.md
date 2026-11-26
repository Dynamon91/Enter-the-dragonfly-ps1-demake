# Spyro: Enter the Dragonfly — PSX milestone 0.12

Continues v0.11, a native PS1 farm diagnostic. No full playable game or verified emulator boot yet. Original ISO is not included. Previous milestones retained.

## Changes
- Recovered 290 directly placed gem nodes from original hub CNK record 1402 (151 red/1, 111 green/2, 15 purple/5, 13 gold/25; aggregate 773). Exported 90 other Character nodes, including original Spyro/Sparx spawn entries, enemies and portals. These are placement data, not original AI or complete world inventory; treasure inside containers is not counted.
- Three original gems with collision-confirmed positions enabled in the farm sector (2 green and 1 red, total value 5). Single-collection flag, pickup radius and vertical checks, midpoint ground check, HUD score and reset. Pickup behavior is prototype logic, not original source code. Other 287 placements remain outside the enabled test area or unsupported by the present collision grid. No memory-card saving yet.
- Original red, green, purple and gold geometry decoded, with source bounds validated (46, 58, 80, 54 triangles). Only red and green appear in the current test sector. Flat facet colors approximate PS2 materials, not the original specular shader.
- Sparx source metadata and geometry records 274 and 365: 13 source meshes decoded, 149 reduced body/eye triangles plus 28 triangles for each of three pairs of original wing shapes. Prototype fixed-point follow and wing-pose cycling; original skinning, animation curves, textures, health states and automatic collection behavior not implemented. Two eye shells omitted from prototype to prevent occlusion.
- Original gemhit1.vag and csprxpu.vag extracted by folded MD4 resource ID. ADPCM payloads byte-identical, VAG headers reconstructed. 22.05 kHz, 7,920 and 8,032 bytes. SPU playback not yet integrated.
- Legacy fire diagnostic targets are hidden by default. Triangle toggles them, Start disables them and resets game state. Existing fire particles and previous assets preserved.
- Native MIPS-I compilation passed. 620,544-byte PS-X EXE; linked allocation 1,727,544 bytes from load address, 173,000 bytes before reserved stack. 325-sector disc; EDC/ECC and executable readback checked. All 73 host regression tests passed. No emulator installed; real boot, GPU behavior, controller timing and FPS remain unverified. Physical unmodified consoles need a suitable homebrew loader.
- Host-rendered screenshots are approximate GPU/texture/depth visualizations; terrain lighting, shadow artifacts and camera need further work. Original assets are not AI-generated.

## Reproduce
Requires Python 3, NumPy, Pillow, Clang MIPS-I, LLD and llvm-objcopy. Source-derived converted assets are included.
```
python tools/build_m12.py build_m12/play
python tools/disc12.py build_m12/play
python tools/preview_m12.py build_m12/play
python tools/asset_preview12.py build_m12/play/asset_preview.png
python -m unittest discover -s tests -v
```
Regenerate placement/mesh/audio exports from your supplied disc:
```
python tools/collect12.py /path/to/source.iso assets_m12
```

## Controls
Extract BIN and CUE together and open ETD_PSX_M12.cue, or load ETD_GEMS.EXE directly in DuckStation. D-pad/left stick move; Cross jump/glide; Square charge; Circle fire; L1/R1 camera; Select recenter; Triangle toggle fire diagnostic targets; Start reset position, gem collection and diagnostics. Walk near gems to collect them. Only three gems enabled.

## Next
Expand collision-supported sectors, implement original enemy and breakable object behavior, SPU playback, bubble/ice/electric breath, portal and streaming system. Correct material layering and shadows, compare original Sparx pose and animation, verify emulator and physical console.
