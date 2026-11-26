# Spyro: Enter the Dragonfly — PSX milestone 0.11

Continues the v0.10 native PS1 farm diagnostic; not a finished game. Original ISO not included. All earlier milestone files retained.

## Changes
- Exact Q12 matrix checkpoint/delta compression, with two 516-word caches. All 245 original sampled matrices and 283,465 vertex poses reproduced exactly; transition blends also checked. No additional animation fidelity claim: Euler XYZ, interpolation, facial morphs and root suppression limitations remain as in v0.10. Matrix storage 252,840 bytes -> 188,481 bytes plus 984-byte offsets and 2,072-byte caches (61,303 bytes net saved).
- 22-byte depth-sorted primitive packets (formerly 24); 16-bit packet indices with 65535 sentinel. The full six-triangles-per-source-triangle clipping capacity is retained, including room for the fire effect. No reduction of world or actor asset detail.
- Circle emits 3 particles every 3 simulation ticks while grounded. Bounded 24-particle pool, finite lifetimes, provisional floor and step obstruction checks. Three synthetic diagnostic targets, each two hits. Start resets all. Original PS2 combat/damage logic, actual enemies and breath timing still unresolved. The muzzle origin and range are prototype tuning, not validated against the source game.
- Actual original `spyro_fire` sprite `ECFECEFC.PXT` (directory group 17) converted to 8-bit CLUT and PS1 additive blending. Source alpha uniformly zero, so nonzero RGB texels use STP and black is transparent. Blend mode is a deliberate approximation. Additional VRAM 1,536 bytes; no overlaps with existing textures, palettes or framebuffers. Dummies are not original models and are for hit detection testing only.
- Native MIPS-I compilation passed; 606,208-byte PS-X EXE. Linked memory from load address: 1,654,340 bytes (130,908 saved vs v0.10), stack region headroom 246,204 bytes. 318-sector Mode 2 Form 1 disc, all EDC/ECC and ISO executable readback tests passed. No emulator installed; boot, GPU behavior, controller input and FPS unverified. Physical unmodified consoles need a suitable homebrew loader.
- 65/65 host regression tests passed. Full source-derived terrain, visibility and animation arrays remain byte-identical. The host-rendered fire preview shows the target removed after two hits. No emulator screenshot claimed.

## Reproduce
Requires Python 3, NumPy, Pillow, Clang MIPS-I, LLD and llvm-objcopy. The converted v0.10 assets and source fire texture conversion are included.
```
python tools/build_m11.py build_m11/play
python tools/disc11.py build_m11/play
python tools/preview_m11.py build_m11/play
python -m unittest discover -s tests -v
```
To regenerate the source sprite from your own supplied disc:
```
python tools/fire_texture11.py /path/to/source.iso assets_m11
```

## Controls
Extract BIN and CUE together and open `ETD_PSX_M11.cue`, or load `ETD_FIRE.EXE` directly in DuckStation. D-pad/left stick move; Cross jump/glide; Square charge; Circle fire at diagnostic targets; L1/R1 camera; Select recenter; Start reset position and targets. Host tests cover fire state, not console input timing.

## Next
Recover original collectible and enemy placements, Sparx, remaining breaths; fix terrain material blending and shadow/decal sorting, compare source animation timing, test emulator and physical console.
