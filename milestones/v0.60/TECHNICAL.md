# Classic v0.60 — original farmer conversations and voice bank

Original adventure only. Preserved all five v0.59 CCC terrain, texture and actor banks byte-for-byte. The recovered source is the user's Definitive Edition 1.2.1 PS2 image (not verified retail). New work focuses on actual source conversation scripts and voice data instead of facial/accessory meshes.

## Script recovery and native integration

Six original conversation records: Dill grab/wait 668/916, Bill 27/372, Dean 1088/585. The English text table is TITLE.CNK record 83. All 28 referenced text entries (three names and 25 spoken lines) recovered. Compiler translates source branch conditions, flag groups 2 and 9, Say/Player/Sparx, flag writes and Give Dragonflies into a small bounded VM. Camera movement, PlaySound script cues, animation and exact original grabbing behavior are deferred. Flag changes commit at conversation end. Give records a pending reward event and sets the original quest flag; it does not create a dragonfly capture or award one in the gameplay ledger. Barn rescue flag 0, UFO flag 6 and five herding flags 8–12 require gameplay integration. No fake completion triggers. Trigger radius and independent bitmap font chosen for PS1 prototype; no original UI or exact camera fidelity claim. Actual source spawn tested with real collision bank: automatic Dill introduction, held-button suppression, repeat talk. Triangle or Cross advances, Triangle talks again, Start resets. Movement and combat update are suspended during active dialogue.

## Original audio

23 unique English VAG clips, 22050 Hz mono, 1617920-byte sector-aligned CCCVOX.DAT. IDs 4105 and 4113 have no matching English VAG in the scanned CNKs, remain subtitles only. Source sample data preserved through the first end flag, terminal dummy normalized to silence. No lossy re-encoding. Original voice names/records and hashes in local manifest. FFmpeg independently decoded 23/23 (126.311 seconds total), all non-silent. Native voice 8 uses SPU window 0x20000–0x70000 and existing 6144-byte CD scratch; longest sample 205136 bytes, disjoint from previous effects bank and voices 4–7. CRC and block checks before key-on; CD reads and manual SPU writes are synchronous and may stall dialogue start. A failed read suppresses voice but the inherited CD driver has sticky transport fault, so subsequent terrain reads may also fail until reboot. No actual hardware output, latency, retrigger pop or voice mixing timing tested.

## Verification

- 12288 enumerated combinations of 11 source quest flags across all three actors and both grab/wait scripts; initial branch and pending reward behavior checked, plus sequential quest paths. Host tests use simulated flags, not actual completion of those challenges.
- 23 byte-exact mocked SPU uploads and 23 corrupted payload rejections, plus two missing-ID and two transport failure tests.
- Actual original spawn conversation trigger and subtitle bounds passed.
- Previous 60 actor placement, 7 texture CRC and 7 read failure cases rerun and passed.
- Native EXE 591872 bytes, linked RAM 1851312 bytes, 49232 bytes before reserved stack. 2576 raw Mode2 sectors regenerated and checked. No emulator/hardware execution. Independent rebuild from local source archive produced byte-identical EXE/BIN.
- Preview: actual native subtitle draw code rendered over archived v0.59 host reference scene; not an emulator screenshot. Character main meshes remain incomplete/static. Original barn doors, fuse, cow herding, UFO, enemies and quest capture rewards remain outstanding.

## Reproduction

From local source archive, without needing original disc again:
    python tools/build_ccc60.py base native59 dialogue out
    gcc -O2 -fsanitize=undefined -I out tests/talk60_host.c -o /tmp/talk60 && /tmp/talk60
    gcc -O2 -fsanitize=undefined -I out tests/voice60_host.c -o /tmp/voice60 && /tmp/voice60 out/CCCVOX.DAT
    gcc -O2 -fsanitize=undefined -I out tests/trigger60_host.c base/src/sector27.c -o /tmp/trigger60 && /tmp/trigger60 out/CCCSECT.IDX out/CCCSECT.DAT

Original extraction (user's local ISO, previous generated build):
    PYTHONPATH=base/tools python tools/dialogue60.py /path/to/source.iso dialogue_new
    PYTHONPATH=base/tools python tools/voice60.py /path/to/source.iso dialogue_new/dialogue60.json voice_new
    cp voice_new/CCCVOX.DAT voice_new/voicedata60.h dialogue_new/
    python tools/build_ccc60.py base native59 dialogue_new out_new

EXE SHA256 43c383490512ab424ea297b62d602f7e35fab06ff12e94b13b6b84b004a5150b
BIN SHA256 a07b3f8ac98666a796583aa3e8eed48c11e6042084340fad0d4c91025f47b524
Source archive SHA256 1de5f525223722004350c8ff90fe9709b16928a49cca9ed77b7435363de55b4d
PS1 test archive SHA256 636e6fcb2acf288d1e0d689a2eb42fecb01f3689b14702cd10a65a6ee522d1f2

Both ZIP CRC tests passed. Local archive includes generated converted assets, native build inputs, tests, reports and host-rendered preview. Public repository contains code and technical notes only. Next: actual barn fuse/door event and source cow-herding targets, connect original quest flags and rewards, recover actor faces and animations, verify actual emulator playback.
