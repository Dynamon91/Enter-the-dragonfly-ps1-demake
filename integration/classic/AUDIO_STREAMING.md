# Classic audio streaming milestone

Standalone source patch delivered in the conversation. No changes to main or the current native game executable.

Host C99 SPU-ADPCM encoder and FFmpeg/Python bank builder: stereo 32 kHz, raw 4096-byte chunks (2048 bytes per channel, 3584 frames, 112 ms), approx. 36.57 kB/s. Experimental ETD_RAW_SPU_V1 format, not VAGi. Independent chunk predictor reset, all five filters and shifts 0–12 evaluated. Complete 29-cue synthetic bank converted and independently decoded. Four Python tests passed, synthetic waveform SNR 42.68 dB. No retail music included or tested.

C queue scheduler: eight stereo slots, four-slot prebuffer, generation/serial ticket checks, failed transfer retry, loop and EOF sequencing, underrun recovery. 80,072 host assertions passed, including 10,000 wraparound refill cycles. Queue state 52 bytes, MIPS-I object 1,072 text bytes, no data/BSS, platform memset dependency.

Driver must cancel/drain old CD requests and DMA before reusing slots, validate tickets before transfer, confirm both channel uploads before completing a ticket, consume only after both voices finish each chunk. Ring flags, IRQ/DMA, CD arbitration and actual playback remain unimplemented. Original source IDs, exact loop points, voice/SFX and cinematics remain unverified. Current loop annotations require exact chunk alignment; do not silently round retail loops. Final partial chunk requires exact-frame stopping to avoid padding. Overall completion estimate unchanged. All original content remains required; expanded content is separate.
