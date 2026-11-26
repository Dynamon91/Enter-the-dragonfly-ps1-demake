.set noreorder
.set noat
.section .text.start,"ax",@progbits
.globl _start
_start:
    lui $sp,0x801f
    ori $sp,$sp,0xff00
    mfc0 $t0,$12
    nop
    lui $t1,0x4000
    or $t0,$t0,$t1
    mtc0 $t0,$12
    nop
    nop
    jal main
    nop
1:  b 1b
    nop
.globl gte_setup
# a0 points to eight packed control words, followed by H, OFX, OFY.
gte_setup:
    lw $t0,0($a0)
    nop
    .word 0x48c80000 # ctc2 $t0,$0
    lw $t0,4($a0)
    nop
    .word 0x48c80800 # ctc2 $t0,$1
    lw $t0,8($a0)
    nop
    .word 0x48c81000 # ctc2 $t0,$2
    lw $t0,12($a0)
    nop
    .word 0x48c81800 # ctc2 $t0,$3
    lw $t0,16($a0)
    nop
    .word 0x48c82000 # ctc2 $t0,$4
    lw $t0,20($a0)
    nop
    .word 0x48c82800 # ctc2 $t0,$5
    lw $t0,24($a0)
    nop
    .word 0x48c83000 # ctc2 $t0,$6
    lw $t0,28($a0)
    nop
    .word 0x48c83800 # ctc2 $t0,$7
    lw $t0,32($a0)
    nop
    .word 0x48c8d000 # ctc2 $t0,$26
    lw $t0,36($a0)
    nop
    .word 0x48c8c000 # ctc2 $t0,$24
    lw $t0,40($a0)
    nop
    .word 0x48c8c800 # ctc2 $t0,$25
    .word 0x48c0d800 # ctc2 $zero,$27
    .word 0x48c0e000 # ctc2 $zero,$28
    jr $ra
    nop
.globl gte_project
# a0 points to (packed x/y, z), a1 points to (screen xy, depth).
gte_project:
    lw $t0,0($a0)
    lw $t1,4($a0)
    mtc2 $t0,$0
    mtc2 $t1,$1
    nop
    nop
    .word 0x4a180001 # RTPS, sf=1
    nop
    nop
    mfc2 $t2,$14
    mfc2 $t3,$19
    sw $t2,0($a1)
    sw $t3,4($a1)
    jr $ra
    nop
