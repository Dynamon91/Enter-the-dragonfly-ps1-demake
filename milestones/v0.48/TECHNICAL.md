# v0.48 — source-first recovery sweep

No new game executable. The v0.37 authentic adventure remains the baseline; later labs remain separate. Current workspace scan: 36 archive/image candidates (17 ZIP candidates, 7 other ISO images, 12 unreadable/non-disc binary candidates), zero matching m37 archive hashes, zero m37-compatible discs, zero PS2 ETD candidate discs. Project/Library title search found no corresponding source archive. Public checkpoint deliberately excluded locally converted asset banks and original disc. Git network unavailable in container; repository connector remains functional.

## Recovery commands

    python tools/recover48.py scan /path/to/local/archive/folder
    python tools/recover48.py extract /path/to/ETD_PSX_M37.bin /path/to/new/recovered
    python tools/recover48.py extract /path/to/original_ps2.iso /path/to/new/ps2_resources
    python -m unittest discover -s tests -p test_recover48.py -v

Python 3.11+. Scan recognizes exact archived ZIP SHA-256 regardless of base filename, inventories minimum generated source input names and disc members, and inspects standalone ISO9660 images (2048 logical sectors or single-track 2352 Mode 1/Mode 2 Form 1). Compressed 7z/RAR require local unpacking. ZIP-contained discs must be unpacked locally before extraction. Recognition is a candidate signature, not verified disc identity; the scanner does not recover data that is not present. Unsupported multi-extent/interleaved directory records are rejected. Extraction copies only recognized source resource paths or v0.37 disc-bank files into a new directory, generates SHA-256 manifests, and leaves inputs untouched. Raw sector EDC/ECC and PS2 resource container semantics are not validated by this tool; subsequent existing parsers and asset gate are required. Interrupted extraction may leave partial files in the new output directory; discard that directory and retry.

If the exact full m37 archive is found, prefer it. If only the m37 test disc survives, recover the 16 named banks/executables; these do not include all generated C headers, editable animation data, or intermediate v0.36 workspace. If only original PS2 ISO survives, extract SPYRODAT and executable then rerun original container parsing/conversion. Source inputs checked in ZIP are minimum indicators, not a complete build dependency audit.

8 synthetic fixture tests passed: full 16-file bank recovery, raw Mode 2 image, nested SPYRODAT tree, extent bounds, unrelated disc rejection, no overwrite, ZIP inventory, unsafe directory rejection. 31 inherited asset/audio tests and host XA transport test also passed. No original resource was recovered during this sweep and no hardware run performed.

Authentic reference preview: [v0.37 character conversion](../../docs/screenshots/v0.37.png), archived host-rendered original geometry and textures, not a new screenshot.
