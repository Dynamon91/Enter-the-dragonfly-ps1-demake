.set noreorder
.section .text.start,"ax",@progbits
.globl _start
_start:
 lui $sp,0x801f
 ori $sp,$sp,0xff00
 jal main40
 nop
1: b 1b
 nop
