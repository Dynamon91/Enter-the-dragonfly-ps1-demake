#include <assert.h>
#include <stdio.h>
#include "spu49.h"
int main(void){unsigned char b[64]={0};Sample49 s={0x1000,32,2048,28,0xffffffffu};b[1]=1;b[17]=7;
 assert(valid_bank49(b,64,&s,1));b[17]=0;assert(!valid_bank49(b,64,&s,1));b[17]=7;b[63]=1;assert(!valid_bank49(b,64,&s,1));b[63]=0;s.address=0x1008;assert(!valid_bank49(b,64,&s,1));s.address=0x1000;s.frames=0xffffffffu;assert(!valid_bank49(b,64,&s,1));s.frames=28;s.pitch=0;assert(!valid_bank49(b,64,&s,1));s.pitch=2048;s.bytes=16;s.loop=0;b[1]=7;b[17]=0;assert(valid_bank49(b,64,&s,1));b[0]=0x10;assert(!valid_bank49(b,64,&s,1));assert(!valid_bank49(b,0,&s,1));puts("Native bank validator: 9 scenarios passed");}
