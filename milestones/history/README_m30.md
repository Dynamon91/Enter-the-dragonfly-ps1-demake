# Spyro: Enter the Dragonfly PSX — milestone 0.30

Continues v0.29. Source metadata 567 and geometry 1061 in Dragonfly Dojo's L_1_DD.CNK. Original 27-joint hierarchy, all 10 animation clips (5,054 keys), original body (520 reduced triangles) and both eyes (76 triangles), body and eye texture bindings 182 and 257. 323 indexed vertices. Original eyelid geometry decoded for analysis, not integrated. Native textures: two 64x64 8-bit CLUTs, 9 KiB additional VRAM. Source idle and loop_ready sampled into 12 and 6 poses, respectively; nearest pose playback, nominal 30 updates/s, 80 and 40 update cycles. Euler XYZ and linear interpolation provisional; root translation suppressed, eyes attached rigidly to head. No facial animation, specular layer, or original enemy AI. Stationary enemy combat unchanged. Host reference preview uses depth buffer, unlike native ordering table. All v0.29 sector and placement bytes preserved. Native compilation passed; emulator/real hardware unverified. Linked allocation 1,834,256 bytes, 66,288 bytes before reserved stack. Six new tests passed, seven inherited v0.29 tests passed on previous host combat harness. ZIP contains original converted data; original ISO only required to regenerate assets. Estimated engineering progress 64% (not playable content).

## Rebuild
```
python tools/enemy30.py /path/to/original.iso # optional regeneration
python tools/build_m30.py
python -m unittest discover -s tests -p test_m30.py -v
python -m unittest discover -s tests -p test_m29.py -v
python tools/preview_m30.py
```
Clang MIPS-I, LLD, llvm-objcopy, Python NumPy and Pillow required. Extract BIN/CUE together and open CUE in DuckStation. Boot ETD_EYES.EXE; fallback ETD_NINJ.EXE and ETD_POOL.EXE are included, no executable-switching menu yet. Next: enemy movement and authentic attack states, NPCs/doors, portal transitions, hardware testing.
