# Classic v0.55 — authentic source recovered

The original user-supplied eight-volume archive was recovered via Library metadata listing (the earlier title search returned no results). All eight files were materialized and concatenated in numeric order. The ISO was extracted from the ZIP with CRC checking. The recovered source is the Definitive Edition 1.2.1 modded PS2 image, not a verified unmodified retail image. The earlier v0.29 full workspace (including source-derived assets) was recovered from the Library as well. No public game image or proprietary asset bank is committed.

## Source identity

| File | Bytes | SHA256 |
|---|---:|---|
| concatenated source ZIP | 809595095 | be0bbb94f1f1783f6a6cea8309e23ef343c2df2cef10c0979886069894495e01 |
| Definitive Edition 1.2.1 ISO | 1423341568 | 1f2c3f69bc5eb0e7707651eef98339e4008646d9289bd8c55be2a2db9c789c05 |
| spyro_etd_psx_m29.zip | 157394998 | 1119f93587c53738f1c686ad2330b03b9e660fda23ca520adc14b80dab09b7bf |

Source archive prefix: `Spyro Enter the Dragonfly Definitive Edition 1.2.1.zip.` followed by 001–008. First seven volumes are 104857600 bytes each; final 75591895 bytes. Use the user's Library listing, not title search alone, to recover split binary files. SHA256 per part:

    001 d600bc0390f6946b8c5b13847e9b4d16d34b8925e91df638dc9db1dd41be1221
    002 b96babc1245dcc640618d1f52c0c907926370d4bf7350bb541ef746f55eb8335
    003 33fd423758878b5466b16480b4dcb6f05d103daa405f74082c106c4b9249def4
    004 115e7772da36936e00efdf27840d38dfef962c061481c9630167abbd45b37fef
    005 4bca73afef1aa3221a31b702e7ebf5b90fe580714a4c0552ce06bc88c5dd5387
    006 0cfe2d43b21defef5693f171ed6d99cc83970b3c3489c2b1069484965b7335e8
    007 bf9205b2203d1e8488066b2bf6973ea9830e6d9ff4e8ad1c400472067b46007c
    008 c804db2e3ea1cf42c0655371164bd1d44deabd351bd41d99ac0e18723de60b1d

## Recovery and actual source validation

`recover48.py extract` extracted 68 files totaling 1421525942 bytes, including 64 CNKs, with hashes. Original cnk.py directory parser validated 24324 records; 6666 records have valid VAG headers (including duplicates; not all are music or unique sounds). The ten Classic location containers are present:

| CHUNKS3 container | Resource records | VAG records |
|---|---:|---:|
| THE_HUB.CNK | 1662 | 795 |
| L_1_DD.CNK | 1243 | 480 |
| L_2_CC.CNK | 1242 | 506 |
| L_3_LI.CNK | 1301 | 535 |
| L_4_C9.CNK | 1176 | 462 |
| L_5_MM.CNK | 1119 | 391 |
| L_6_HM.CNK | 1231 | 491 |
| L_7_TD.CNK | 1080 | 378 |
| L_8_JJ.CNK | 1327 | 530 |
| BOSS.CNK | 709 | 137 |

## First new authentic terrain: Crop Circle Country

Real source test of classic_mesh50.py, not a synthetic fixture. Main metadata record 379 in L_2_CC.CNK, source SHA256 96e6088141808bbb0f46e9af53327ff4eabaf0408e5f06b7b339a749813ab2c9. Selection: four named terrain sectors and their named shadows, case-insensitive regex `^(sl[1-4]_|sh_sl[1-4]_)`. 508 selected / 508 uniquely matched, 0 unmatched, 0 duplicate shapes; 83884 vertex samples, 52072 nondegenerate triangles, 41 material hashes. Original UVs and face/material/part data exported to geometry.npz, SHA256 658dc674cee209178337cbf4782c83a9102d6af0e6c023a5a1b5efbf192216fe. This is not full scene coverage; transforms, original material binding, collision, props, enemies and quest triggers are not yet validated. PXT record 580 begins with expected signature, but old parser rejects group header at offset 272240; investigate without silently skipping. Collision named ccc_collShape found in records 379 and 425. No new complete playable level.

Reproduce using user source (shell, from repo root):

    cat "/path/to/Spyro Enter the Dragonfly Definitive Edition 1.2.1.zip."00[1-8] > /tmp/etd-source.zip
    unzip /tmp/etd-source.zip '*.iso' -d /tmp/etd-source
    python tools/recover48.py extract "/tmp/etd-source/Spyro Enter the Dragonfly Definitive Edition 1.2.1.iso" /tmp/etd-recovered
    python tools/classic_mesh50.py recover /tmp/etd-recovered/SPYRODAT/CHUNKS3/L_2_CC.CNK 379 '^(sl[1-4]_|sh_sl[1-4]_)' /tmp/ccc-geometry

The tested invocation included --allow-partial but all selected shapes matched, so it is unnecessary for this selection.

## Native baseline recovery

The recovered v0.29 workspace was unzipped and `python tools/build_m29.py` succeeded using packaged authentic banks. Seven original tests passed via `PYTHONPATH=tools:tests python -m unittest discover -s tests -p test_m29.py -v`. EXE 544768 bytes; linked RAM 1800416 bytes, 100128 bytes before reserved stack. Rebuilt ETD_PSX_M29.bin SHA256 1dd70564ffbc3d4abfae961e32653356fe8b5c3a8645f623db5ce9cd058c823d. Native PS1 binary and disc layout verified by host tests, not emulator execution. Full generated v0.37 workspace still not recovered; preserve v0.37 source and reconstruct later generated files using available disc and v0.29 checkpoint. No regression to v0.29 as final game target. v0.55 is a recovery/terrain extraction milestone, not a new native adventure version. Expanded Mode frozen.

Next: recover/rebuild v0.30–37 dependent assets and verify native baseline; complete Crop Circle Country geometry/material/collision/spawn conversion; integrate v0.52–54 modules; restore the remaining released locations and original soundtrack.
