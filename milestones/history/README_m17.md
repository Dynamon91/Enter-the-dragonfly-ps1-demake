# Spyro: Enter the Dragonfly — PSX milestone 0.17

This revision isolates CD-ROM transport and transactional sector residency from the v0.16 farm gameplay. The original farm executable remains byte-identical and is included in the new disc and separately in the test ZIP. The disc boots a separate top-down sector viewer, not the playable farm. No source ISO included.

## Changes
- Native polled CD-ROM register transport: Setmode (2x/2048-byte), Setloc (BCD MSF), ReadN, INT1 data FIFO, Pause, bounded polling and fail-closed error latch. Uses uncached KSEG1 MMIO; no BIOS IRQ dependencies. Controller timing, boot-state assumptions and physical reads are not verified; a fault requires reboot.
- Reads the ISO9660 PVD/root directory and locates HUBSECT.IDX and HUBSECT.DAT by name, with extent and endian checks. Supports the authored single-sector root directory, not arbitrary ISO9660 layouts.
- Two 64 KiB resident/staging buffers. A failed read or CRC validation does not replace the active block. All 174 blocks verified through a register-level mock using actual authored Mode2 disc payloads. No claims of emulator execution.
- Standalone viewer fits block AABB on a 320x240 overhead view, with flat source texture-average colors, source object markers, optional collision candidates and a numeric HUD. No texture uploads, player-driven sector traversal, multi-block residency, original collision BSP or gameplay integration yet.
- Native EXE 20,480 bytes, linked memory from load 179,152 bytes (175 KiB) for viewer alone. This is separate from gameplay RAM, not a reduction of the farm runtime. 116 total host regression tests passed, including six new tests. New disc includes 2,289 sectors with EDC/ECC regeneration checks.

## Build
Requires Python, Pillow, Clang with MIPS-I, LLD, llvm-objcopy. From project root:
```
python tools/build_m17.py
python tools/disc17.py
python tools/preview_m17.py
python -m unittest discover -s tests -v
```
Earlier milestone artifacts and tools are retained.

## Test
Extract BIN/CUE together and boot the CUE in DuckStation (PS1 BIOS required); the standalone ETD_CD.EXE needs the matching mounted disc. The viewer starts at sector block 141 near the farm. D-pad Left/Right changes block ID by 1; L1/R1 changes ID by 10; Cross toggles the collision view. HUD fields: block ID, render triangle count, collision candidate count; green status means valid load, red indicates failure. Yellow marks denote source placements. Switching is synchronous, not seamless. Use the separate ETD_FARM.EXE for the original v0.16 gameplay test. The host preview is an overhead visualization of the disc bytes, not a screenshot from a native console.

Hardware reference: https://psx-spx.consoledev.net/cdromdrive/ . No commercial disc authentication data; use a compatible homebrew loader for real hardware. Next: verify CD controller on emulator, optimize and integrate the transport into gameplay, implement texture caching and neighboring sector residency.
