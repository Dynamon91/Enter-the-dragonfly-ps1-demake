ENTRY(_start)
SECTIONS {
 . = 0x80010000;
 .text : { *(.text.start) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) *(.sdata*) *(.got*) }
 .bss (NOLOAD) : { *(.bss*) *(.sbss*) *(COMMON) }
 /DISCARD/ : { *(.MIPS.abiflags) *(.reginfo) *(.pdr) *(.comment) *(.note*) *(.gnu.attributes) }
 ASSERT(. < 0x801e0000,"RAM overflow")
}
