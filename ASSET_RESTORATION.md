# Asset policy — source-first restoration

The v0.37 authentic-asset adventure is the primary game baseline. The v0.38–0.44 asset-free campaign/arena builds are diagnostic experiments only; they must not replace it. Integrate their tested mechanics into the authentic baseline after recovering the full workspace.

## Required recovery
Prefer the full local archive `spyro_etd_psx_m37.zip`, SHA-256 aa9d30787b88f26f37ed36398cbc995b8e79e9f541ef5c23edac6cf108b4de04. The test-disc-only archive is insufficient to regenerate the complete source assets. If the full archive is unavailable, use the user's original PS2 disc dump and the retained extraction tools. Earlier extraction identified US executable SLUS_203.15 and SPYRODAT/CHUNKS, CHUNKS2, CHUNKS3. Verify these against the actual recovered disc. See milestones/v0.37/ARCHIVES.md and TECHNICAL.md.

## Asset precedence
1. Existing released character meshes, rigs, animations, textures, level geometry, collision, object placement, dialogue/audio: recover and convert original PS2 resources, preserving UVs, silhouette, topology where practical, scale and layout.
2. Existing assets for Crush, Gulp, Ripto and Gnasty Gnorc: reuse source models/animations where actually available, audit missing clips separately. Boss encounters not present in the released game need newly authored behavior, not automatic replacement models.
3. Cancelled levels: use verified surviving geometry, textures and references first. Where assets are genuinely absent, create distinctly labeled fan reconstruction and reuse compatible original environment props.
4. v0.44 asset library: retain as separate diagnostic/fallback content; do not silently substitute for released assets.

## Integration order
Reproduce v0.37 build, validate host tests and emulator boot; continue extracting actual released level packs and transitions; port campaign routing and combat modules onto the native 3D engine; test original collision and animation fidelity; add expanded encounters and cancelled content as separate mode. Keep original disc and converted proprietary asset banks local, public repository retains tools, manifests, source, and non-proprietary diagnostics. No original-asset claims without extraction evidence.
