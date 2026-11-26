ENTRY(_start)
SECTIONS {
  . = 0x80010000;
  .text : { *(.text.start) *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  /DISCARD/ : { *(.MIPS.abiflags) *(.reginfo) *(.pdr) *(.comment) *(.note*) *(.gnu.attributes) }
}
