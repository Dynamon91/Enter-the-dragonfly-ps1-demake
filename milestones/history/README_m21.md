# Spyro: Enter the Dragonfly PSX — milestone 0.21

Native MIPS-I experimental streamed gameplay. This revision combines the v0.20 world streaming and collection with basket, fire, sheep and Sparx health mechanics. Original PS2 ISO is not included.

## Changes
- All 27 basket IDs and 12 sheep IDs validated against original sector records and coordinates. Objects are instantiated only when their sectors are resident. Source IDs retain broken/consumed state across eviction and reloading. Charge and fire hit tests use collision-derived floor coverage; no full wall/BSP collision. Baskets release provisional red gems after a delay; original rewards not decoded. Sheep are stationary reconstructed fodder; butterflies seek Sparx or Spyro when health is zero and expire after 180 simulation steps. No original sheep AI or enemy combat yet.
- Native original fire texture and original basket sound bank from earlier milestones restored, with three original samples; no audible playback verified. Fire uses additive approximation and collision-floor gates. Sparx assistance disabled at zero health; health indicators and provisional body tint in the native renderer. L2 is a debug damage control; it is not an original enemy attack.
- Host interaction tests at the original object coordinates show fire breaks Farm_Basket1_1 at frame 4 (5th simulated step); Farm_Basket1_2 charge and reward persist over unloading and reloading; SHEEP4 butterfly restores 2/3 to 3/3 health and can revive zero health. These are locally staged tests, not a continuous playthrough from spawn. 34/39 object centers have supported cache residency; River_Basket_2, SHEEP1–3 and SHEEP7 exceed the existing eight-block selection capacity. All original IDs and placements are retained. Terrain shadow/lighting, original pose conventions, object textures and collision coverage remain incomplete.
- Native linked allocation 1,771,088 bytes, 129,456 bytes before reserved stack region. Executable 466,944 bytes. 149 regression tests pass, including nine new tests. No emulator or physical hardware verification. Host preview depicts staged interaction states with recovered meshes and textures, using a side camera and representative original animation poses, not captured emulator output.

## Rebuild
Requires Python 3, NumPy, Pillow, Clang MIPS-I, LLD, llvm-objcopy. From project root:
```
python tools/build_m21.py
python tools/disc21.py
python -m unittest discover -s tests -v
python tools/preview_m21.py
```

## Test
Extract BIN/CUE together, open CUE in DuckStation. ETD_HUB.EXE needs the matching disc-resident data. D-pad/left stick move, Square charge, Cross jump/glide, Circle fire, L1/R1 camera, Select recenter, L2 diagnostic damage, Start reset. The previous ETD_GEM.EXE and earlier fallbacks are also on the disc. No Sony disc authentication data; physical unmodified PS1 needs a compatible homebrew loader. No emulator boot, audible playback or framerate claim.

Next: dense neighborhood streaming capacity, asynchronous CD reads, enemy scripts, additional breath abilities, original spawn coverage, other levels and cutscenes.
