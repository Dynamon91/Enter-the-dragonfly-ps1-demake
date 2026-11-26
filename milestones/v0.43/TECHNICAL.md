# v0.43 — integrated expanded campaign diagnostic

Native, asset-free PS1 lab on top of v0.42. It links the v0.39 campaign ledger and route gates, v0.41 combat, and v0.42 renderer in one session. All 30 named locations are synthetic flat test rooms with deterministic collectible positions, not recovered level geometry. The five bosses remain diagnostic proxies; final alliance uses one actor. Expanded-only; Classic and v0.37 source remain untouched. Hub ability gates and original quest triggers are not modeled. No memory-card save, real CD scene streaming, original models or audio. In-room capture is a directional range check, not a simulated bubble projectile. Menu selection replaces physical portal geometry.

Controls: D-pad moves; Square charges; Circle captures in rooms or breathes in boss fights; Triangle changes boss element; L1/R1 selects destinations, Cross enters when unlocked. In a boss fight, Start retries, Select retreats without granting a win, Cross returns after victory. Progress persists across rooms in RAM until reset. The room counter and global dragonfly total are displayed. Green destination names are eligible; red names are locked. The signed GPU coordinate packing is corrected in the generated native source, and controller edge commands are latched across vblanks.

Build from repo root: `python tools/build43.py` (clang, ld.lld, llvm-objcopy). Test: `gcc -std=c99 -O2 -fsanitize=undefined -I src tests/test_session43.c -o /tmp/s43 && /tmp/s43`. Starting from zero, input-driven bot reached 120/120 captures, all 30 room IDs, five victories. Bosses defeated at 30, 60, 80, 96 and 110 captures (Gnasty threshold is 95, test visits after a room finishes). Retreat before victory does not award the boss bit; locked portals and duplicates rejected. Prior workprint38, campaign39, combat40, arena41, view42 host tests pass. Renderer preview: `gcc -std=c99 -O2 -I src tests/preview43.c -o /tmp/p43 && /tmp/p43 /tmp/p43.ppm`. This is host-rendered output, not emulator capture.

MIPS-I link succeeded, PS-X EXE 32768 bytes. 300 Mode2 Form1 sectors structurally checked. No emulator execution or hardware timing verified. Disc lacks Sony security data; use an emulator or compatible authorized homebrew loader. Full v0.37 generated assets absent, so original adventure not rebuilt.

SHA256 EXE: 0a6e296e6fb32bf377cc98a4f0fee2014553507347dac8bc3005d001cb07ba85
SHA256 BIN: 7952bc843ee9f1b451c92bde04fd972d2e211d7402673567ae733a7af1e0fc48
SHA256 CUE: ab2797dea418b21965db81ee4e742cca508fe4006332f4818d2991f66df5ab2a

Next: recover v0.37 asset banks, connect real scene loading, proper portal triggers, camera, collisions, and original art/audio; verify emulator boot and controls.
