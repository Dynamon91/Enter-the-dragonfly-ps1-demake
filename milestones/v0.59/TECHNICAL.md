# Classic v0.59 — original CCC main meshes and placements

Classic adventure only. Recovered user-supplied Definitive Edition 1.2.1 PS2 source is modded, not verified retail. Previous v0.58 native terrain, texture, sky, movement and existing collectible data remain byte-identical apart from texture slot reservation and the new actor renderer and boot mount.

## Recovered assets

| Model | Metadata | Source triangles | Native triangles | Instances |
|---|---:|---:|---:|---:|
| Cow | 393 | 720 | 344 | 5 |
| Farmer | 823 | 780 | 179 | 3 |
| Chicken | 429 | 260 | 167 | 6 |
| Ray-gun Riptoc main body | 701 | 1312 | 384 | 10 |
| Space cow main body | 160 | 808 | 255 | 7 |
| Blue urn | 344 | 240 | 168 | 27 |
| UFO platform | 1201 | 340 | 225 | 2 |
| Total | | 4460 | 1722 | 60 |

Eight selected main/static mesh shapes, seven source texture bindings uniquely verified by hash, size and dimensions, 898 native vertex entries. Recovered original body geometry and source UVs with verified mesh bounds. Position clustering and duplicate/degenerate triangle removal are deliberately lossy; per-corner UVs quantized to 8-bit texels with common repeat shift. Some facial parts, accessories, gun, space cow legs, skeletal animation and original material blend modes remain missing. Textures opaque RGB555, 64x64 indexed base mip; no exact retail fidelity claim. Instances preserve original placement IDs and rounded position, yaw quantized to 64 headings; small X/Z rotations ignored. UFO platform association based on texture metadata and placement class, provisional. No AI, actor collision, talking, new prop interaction or quest rewards implemented. 11 original conversation scripts inventoried by record, SHA256, dialogue IDs and branch numbers, not executed.

## Native build

Actor textures moved to 43008-byte CCCACT.DAT, 21 sectors, 7 CRC-checked ETDT blocks, loaded into reserved old terrain VRAM slots 41–47 using the existing upload path. Terrain has exactly 41 groups and its cache cap is reduced to 41; old sky regions unchanged. New model vertices and faces resident, original textures loaded at boot using existing scratch. Failure leaves actor_ready59 false and prevents traversal startup; partially uploaded actor slots not used. No GPU failure recovery or native timing measurement. Geometry culling uses original placed location and bounded radius; existing packet cap still applies. This is a standalone CCC traversal prototype; no new complete quest or connected original adventure.

EXE: 581632 bytes. Linked RAM from load 1840144 bytes. Headroom before reserved stack region 60400 bytes (58.98 KiB), about 31 KiB regained relative to initially embedded actor textures. All 1781 raw sectors validated by structural regeneration. Native compilation experimental MIPS-I warning. No emulator or hardware execution.

Host UBSan test: all 60 source positions sampled, 29580 submitted actor triangles in aggregate before camera clipping, peak 1228 at these sample positions, all seven texture CRC failures and seven read failures rejected, out-of-range cull and retry verified. This is not an exhaustive frame-budget proof. The four previous terrain/texture banks, sky, rig, movement and collection routines verified unchanged. v0.57 original movement/jump/collection checks rerun and passed. Source snapshot rebuilt exact EXE and BIN independently from packaged dependencies.

## Reproduction

Original extraction:
    PYTHONPATH=/path/to/v029/tools:tools python tools/actors59.py /path/to/L_2_CC.CNK /path/to/ccc56/bindings.json /path/to/new/actors59

Native build:
    python tools/build_ccc59.py /path/to/v029 /path/to/ccc58_native /path/to/actors59 /path/to/new/ccc59_native
    gcc -O2 -fsanitize=undefined -I/path/to/ccc59_native tests/actors59_host.c -o /tmp/actors59
    /tmp/actors59 /path/to/ccc59_native/CCCACT.DAT

Self-contained local source archive contains converted banks, generated v0.58 inputs, new actor data, native build dependencies and reports. From extracted root:
    python tools/build_ccc59.py base previous actors out

The preview uses actual recovered model/terrain/texture data in a host reference rasterizer. Static main meshes show incomplete faces and accessories; original sky blending remains approximate. Not an emulator screenshot. Full preview script and PNG in local archive.

EXE SHA256 3229599d2f3959f69cc32eeb669f3c3094f601a6a96d66df1f47d3ac225d3b12
BIN SHA256 cb638291f9a68bff920a9ba80c400fd03a193ae4b19524f8f770642d828c3868
Source archive SHA256 6cf5ddba10285ad16e1a04b52b0a00fb35d7368fa68f554934afb558fefb95c3
PS1 test archive SHA256 33810bbd79a122c2f69f91ce9724b641f1de716bfbb0ed87a16bd1ae99ac8936

Both ZIP archives passed CRC verification. Public source repository excludes original and converted proprietary banks. Next: resolve remaining actor submeshes, original animation, cow herding and farmer dialogue scripts, enemy behavior, and emulator verification. Expanded content remains frozen.
