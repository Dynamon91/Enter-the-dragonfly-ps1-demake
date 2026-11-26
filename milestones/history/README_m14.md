# Spyro: Enter the Dragonfly — PSX milestone 0.14

Continuation of v0.13, a native PS1 farm-sector prototype, not a full game. The original PS2 ISO is not included.

## New in 0.14
- Recovered 27 basket placements from the hub placement record and decoded `basketShape` (metadata record 932, geometry record 1237). 554 original triangles, reduced to 158 per instance with grid-based mesh simplification. Original local bounds validated against metadata. Two source positions are enabled within the current supported collision grid. Flat-shaded brown material is provisional, not the original basket texture.
- Both baskets can be destroyed by charging while moving or by a live fire particle. Broken baskets expose a single provisional red gem after a short release delay; the original reward definitions have not been recovered. Direct pickup checks the existing collision grid and increases the counter only once. Start resets baskets and rewards. Sparx-assisted pickup of basket rewards, debris animation and basket solid collision are not yet implemented.
- Original break-basket sound `SPY01.vag`, identified explicitly by the hub audio table (record 1079, event 103); payload record 769. 36,544 bytes of original ADPCM, 22.05 kHz, preserved byte-for-byte. Three original sound effects now use the existing SPU driver. No actual audio playback test was performed.
- GPU packet coordinates now encode all six signed 11-bit GTE screen coordinates losslessly in five 16-bit words, reducing packet size from 22 to 20 bytes. All 2,048 signed coordinate values and mixed signs tested; no geometry or texture changes to the earlier farm assets.
- Native MIPS-I build 681,984 bytes, linked RAM allocation 1,749,632 bytes from load address; 150,912 bytes before reserved stack region. BIN/CUE 355 sectors; executable readback and EDC/ECC checks passed. 92 host tests passed (83 previous + 9 new). No emulator/hardware execution, audio playback, FPS or timing verification. Real unmodified consoles require an appropriate homebrew loader.

## Build and test
Requires Python 3, NumPy, Pillow, Clang MIPS-I, LLD and llvm-objcopy.
```
# Optional re-extraction from your supplied original ISO:
python tools/basket14.py /path/to/source.iso assets_m14
python tools/build_m14.py build_m14/play
python tools/disc14.py build_m14/play
python tools/preview_m14.py build_m14/play
python -m unittest discover -s tests -v
```

## Controls
Extract BIN and CUE together and open ETD_PSX_M14.cue in DuckStation, or load ETD_BASK.EXE directly. D-pad/left stick move; Cross jump/glide; Square charge; Circle fire; L1/R1 camera; Select recenter; Triangle toggle legacy fire targets; Start reset. Baskets are near sector coordinates (-3312,799,-777) and (-2906,800,-738). Preview uses a diagnostic camera starting near the first basket; not an emulator capture. Existing farm rendering, lighting, sparse collision, original animations, AI, other breath abilities, streaming, soundtrack and entire adventure remain unfinished.
