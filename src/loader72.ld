ENTRY(_start)
SECTIONS {
 . = 0x801e0000;
 .text : { *(.text.start) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) *(.sdata*) *(.got*) }
 .bss (NOLOAD) : { . = ALIGN(4); __bss_start = .; *(.bss*) *(.sbss*) *(COMMON) . = ALIGN(4); __bss_end = .; }
 /DISCARD/ : { *(.MIPS.abiflags) *(.reginfo) *(.pdr) *(.comment) *(.note*) *(.gnu.attributes) }
 ASSERT(return72 == 0x801e0010,"return vector moved")
 ASSERT(. < 0x801ea000,"resident loader overlaps session state")
}
