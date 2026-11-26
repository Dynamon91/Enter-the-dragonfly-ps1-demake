.set noreorder
.set noat
.section .text.start,"ax",@progbits
.globl _start
_start:
    lui $t1,0x1f80
    ori $t1,$t1,0x1810
    sw $zero,4($t1)       # GP1 reset
    lui $t2,0x0300
    ori $t2,$t2,1
    sw $t2,4($t1)         # disable display
    lui $t2,0x0500
    sw $t2,4($t1)         # display origin 0,0
    lui $t2,0x06c6
    ori $t2,$t2,0x0260
    sw $t2,4($t1)         # horizontal range
    lui $t2,0x0704
    ori $t2,$t2,0x2018
    sw $t2,4($t1)         # vertical range 24..264
    lui $t2,0x0800
    ori $t2,$t2,1
    sw $t2,4($t1)         # 320x240 NTSC, 15-bit
    lui $t0,%hi(packets)
    addiu $t0,$t0,%lo(packets)
    lui $t4,%hi(packets_end)
    addiu $t4,$t4,%lo(packets_end)
    lui $t5,0x1000        # GPUSTAT bit 28: ready to receive DMA block
send:
    lw $t2,4($t1)
    nop
    and $t2,$t2,$t5
    beq $t2,$zero,send
    nop
    lw $t3,0($t0)
    addiu $t0,$t0,4
    sw $t3,0($t1)
    bne $t0,$t4,send
    nop
    lui $t5,0x0400        # wait for command readiness after final polygon
idle_gpu:
    lw $t2,4($t1)
    nop
    and $t2,$t2,$t5
    beq $t2,$zero,idle_gpu
    nop
    lui $t2,0x0300
    sw $t2,4($t1)         # enable display
forever:
    b forever
    nop
.section .rodata,"a",@progbits
.balign 4
packets:
.incbin "packets.bin"
packets_end:
