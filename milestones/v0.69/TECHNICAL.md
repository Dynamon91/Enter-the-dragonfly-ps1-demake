# Classic v0.69 — source seabed, switches and gates

Original adventure weighted completion 33.75% (rounded 34%, 66% remaining), collision estimate increased from 75 to 80; Luau location stage remains 40 until major challenge access routes are proven. Source is the user's Definitive Edition 1.2.1 modded PS2 image, not verified unmodified retail. Previous v0.68 preserved.

## Seabed
At the eight previously blocked vase locations, original visual seabed surfaces remain even though the collision extractor missed solid floor polygons. New fallback samples only actual packed render triangles with original material IDs 28 (sandedge, 597fc378), 53 (sandwater, a7735dab), 59 (waterbot, b50ac2d4), only when solid-bed query is absent. Requires submerged vertices, slope limits, barycentric inclusion, and bounded depth. No added geometry or changed banks. Reconstructed collision proxy, not a full PS2 BSP decoder or swept-volume proof. Native swimming/controller host tests: all 14 vases and 35 urns break and collect, 24 submerged gem identities worth 75 versus 18 worth 42 before. No duplicate pickups. Three original free dragonflies still captured, three challenge-associated identities remain deferred.

## Source switch/gate recovery
Original button MRB record 1201 / geometry 699 (239 optimized triangles across four shapes, including both signal states); bamboo door 580 / 255 (1180 triangles across two shapes, bbox excluded); breakable wall 132 / 436 (631 triangles). 2050 triangles total. Five source texture groups 266,307,35,305,221, uniquely resolved with original UVs. 30720-byte LIAGAT.DAT, reserve slots 57–61 (57 terrain slots vs measured maximum 49, prior prop slots 62–63 intact). Original five button, three gate and one wall placements retained. Source scripts gate_front 539, gate_front2 429, gate_pastcave 675, gate_lake 346, gate_end 1036. Group-3 flags implemented: front 0/14, prison 12, pastcave 3/4/15, lake 6/7/13/16, end 10/11. Prison EDF does not explicitly invoke gate_prison.scr, so flag 18 not fabricated. Script timing, camera and animation approximated, not exact. Actual front flame hit uses widened vertical proxy because original button is 243 units above the recovered floor; charge allowed by runtime but not verified at that placement. Four other source buttons require Super Smash: jump then Triangle. All five native attack-input tests passed. Three corresponding gates animate upward over 32 ticks and release oriented land movement blocker; closed/open proxy crossing tested directly, not continuous route traversal or underwater collision. Front/prison gate geometry not implemented. Original underwater-charge wall mesh rendered, not yet destructible; flag 37 remains untriggered. No fake challenge completion or rewards.

## Verification
600 dry movement updates, jump/reset, eight dive/resurface columns, 80-tick horizontal swim, shoreline entry and exit passed with host callbacks. All 498 terrain and 82 texture blocks native reader tests passed, five new texture CRCs verified, 2638 raw Mode2 sectors structurally checked. All five prior banks byte-identical. Independent source-archive build produced identical EXE/BIN. EXE 630784 bytes, linked RAM 1800208 bytes, 100336 bytes (98 KiB) before reserved stack. Native MIPS-I compilation and host tests, no actual emulator or hardware boot/performance; tests reposition player between source locations. Preview is host reference rendering of original source terrain and converted props, not emulator output.

Full downloadable archive is authoritative, includes new extraction tools, generated assets, native build inputs, test harnesses, preview script and reports. GitHub includes the three runtime headers and native build script (all verified byte-for-byte against tested snapshot), project tracker and notes. Proprietary original/converted asset banks excluded from public GitHub.

Rebuild: python tools/build_luau69.py base native68 . final69
Host regression commands in archive README.md.

EXE SHA256 a497c789a98edf5c5f42d48bb14c5dc96b39ab403e043737346bf799c96274b8
BIN SHA256 8a30ef8b9be1dae7e69661c703f1c6d5ea94f4f5f45f7ae6b9505dbf5de54f25
Source ZIP SHA256 94cfeaa58f2a956a9702210472a5c1c36b581b90d90f9657ad31af44f7c9cc19
Test ZIP SHA256 6c2ab1a0add297adb0c2e5ab568a64b4edd23d5f5a0a701eb7b2443b78d1fcd4
Both ZIP integrity checks passed.

Next: source wall destruction/access route, prison and pastcave challenge capture, original enemies/NPCs, remaining levels and actual emulator verification.
