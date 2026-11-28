.set noreorder
.text
.macro bios name, table, number
.globl \name
.ent \name
\name:
 li $t1, \number
 li $t0, \table
 jr $t0
 nop
.end \name
.endm
bios bios77_open, 0xb0, 0x32
bios bios77_seek, 0xb0, 0x33
bios bios77_read, 0xb0, 0x34
bios bios77_write, 0xb0, 0x35
bios bios77_close, 0xb0, 0x36
bios bios77_first, 0xb0, 0x42
bios bios77_init, 0xb0, 0x4a
bios bios77_start, 0xb0, 0x4b
bios bios77_stop, 0xb0, 0x4c
bios bios77_bu, 0xa0, 0x70
bios bios77_auto, 0xa0, 0xad
