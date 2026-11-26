# Spyro: Enter the Dragonfly PSX — milestone 0.25

First Dragonfly Dojo conversion milestone. The v0.24 hub gameplay executable and its disc assets are unchanged. The new test disc boots a separate native Dojo sector inspection tool, not a playable Dojo level.

## Original data recovery
- Source: user-supplied Definitive Edition 1.2.1 ISO, `SPYRODAT/CHUNKS3/L_1_DD.CNK`.
- Of 682 selected named terrain shape entries in record 359, 661 distinct meshes were recovered, 20 exact duplicate name/material/decoded geometry entries removed, and one (`DD_TREE_TOPShape`) remains unmatched. All exported mesh bounds match source metadata within 0.01 source units. 191,271 vertex samples and 127,733 nondegenerate triangles; other scene objects outside selected terrain name filters are not counted as complete.
- Texture directory: 351 groups, all offset and size checks passed. 52 of 53 materials resolve uniquely using folded MD4 filename hash, dimensions and size; one ambiguous material affects 56 faces. 52 converted 64x64 indexed texture blocks. Opaque base palette conversion; PS2 layered shading and alpha remain unresolved.
- 7,035 collision triangles from 4,669 candidate polygons in `ddojo_collShape`, recovered by aligned heuristic polygon scan. Original BSP interpretation and walkability not verified.
- 351 character placements corroborated between records 359 and 569, including 193 direct gems worth 389. Other 158 entries remain generic placements, not implemented AI or scripts.
- 163 sector blocks across 131 spatial cells, each at most 64 KiB. Original source IDs retained; position rounding within 0.5 units; UV Q10 rounding within 1/2048 (four faces shifted by integer texture repeats).

## Native test
`ETD_DOJO.EXE`: 20,480 bytes, 178,528 bytes linked main RAM. Left/right select sector; L1/R1 skip ten sectors; Cross toggles collision. Flat material-average terrain colors. The disc includes ETD_POOL.EXE and its hub assets for fallback; it does not yet provide a portal or menu to launch the hub from the Dojo viewer. Direct executable requires the mounted disc assets. Texture bank is on disc but not used for textured rendering in the viewer. 10 new host tests passed, including all 163 blocks through simulated CD registers, disc integrity, asset quantization, texture CRC, fallback identity and transactional bad reads. Previous 175 tests passed in v0.24; not rerun as part of this milestone. No emulator or real-hardware execution measured.

## Reproduce
Requires original ISO supplied separately, Python, NumPy, Pillow, Clang MIPS-I, LLD, llvm-objcopy.
```
python tools/dojo25.py /path/to/source.iso assets_m25
python tools/dojo_collision25.py /path/to/source.iso assets_m25
python tools/dojo_assets25.py /path/to/source.iso
python tools/dojo_sectors25.py assets_m25
python tools/build_m25.py
python -m unittest discover -s tests -p test_m25.py -v
python tools/preview_m25.py
```
Next: parameterize the streamed gameplay engine for Dojo, evaluate neighborhood RAM/VRAM constraints, decode original spawn/portal scripts, restore interactive objects and enemy AI, resolve remaining geometry/materials and validate in emulator. Engineering estimate 59%, not fraction of original game playable.
