.set noreorder
.set noat
.section .text.start,"ax",@progbits
.globl _start
_start:
    j boot72
    nop
    nop
    nop
.globl return72
return72:
    j menu_entry72
    nop
boot72:
    lui $sp,0x801f
    ori $sp,$sp,0xff00
    lui $t0,%hi(__bss_start)
    addiu $t0,$t0,%lo(__bss_start)
    lui $t1,%hi(__bss_end)
    addiu $t1,$t1,%lo(__bss_end)
1:  beq $t0,$t1,2f
    nop
    sw $zero,0($t0)
    b 1b
    addiu $t0,$t0,4
2:  jal init72
    nop
menu_entry72:
    lui $sp,0x801f
    ori $sp,$sp,0xff00
    jal menu72
    nop
3:  b 3b
    nop
.globl launch72
launch72:
    # Flush CPU instruction cache via BIOS A0 function 44h. No return to old overlay.
    addiu $t1,$zero,0x44
    addiu $t0,$zero,0xa0
    jalr $t0
    nop
    lui $t0,0x8001
    jr $t0
    nop
