# Native voice bank and dialogue integration — recovered M29

Source patch and incremental BIN/CUE update delivered in the project conversation.

- Full selected English/shared bank (944 resources, 54,327,296 bytes) mounted in recovered native Dojo engine. Stable 3410-ID index paged from disc. 776 resources fit a 96 KiB resident slot; 168 require streaming/larger buffer.
- Original syouch and spybreathredofir assets preloaded at startup, tied to damage and fire-button events. Original Rusty line 430 available on L2 as a diagnostic; not a quest binding. Voice DMA and music staging shared only when idle, selected voice request deferred until music queue buffered.
- English TITLE.CNK record 83 hash matches M36: 1,082 rows, 1,072 unique text IDs. 444 unvoiced, 287 ready matches, 113 unique matches requiring streaming, 212 missing English-name matches, 16 ambiguous. No guessed fallback or claim of completed native quest triggers.
- 5,168,729 host voice-index/payload assertions, 66,113 dialogue lookup checks; MIPS-I link 1,878,544 bytes, 22,000 bytes before reserved stack. Fresh disc 168,012 sectors; 263 independent ECC/EDC checks; all 28 music hashes verified. Incremental update applied twice, all 16 ISO files byte-identical to fresh build, 99 rebased sector checks; output 168,307 sectors, SHA256 1976eb44ceba48dc7e64f3c764325bf05a3205abe31f4280cf13f3409fefcc2c.
- Prior disc preserved by updater. No original audio assets or binaries committed to GitHub.

Remaining: actual emulator/console execution, long voice streaming, exact missing/ambiguous voice resolution, native quest hooks and portals, all original gameplay and cinematics. Latest v0.74 unified build unavailable; no main branch changes or increase to the 50% engineering estimate. Synchronous CD reads may stall frames; no measured runtime performance.
