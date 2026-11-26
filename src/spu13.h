/* Native SPU register driver. Startup upload only; bounded polling, audio optional. */
#include "sfx13.h"
#ifndef SPU_WRITE
#define SPU_WRITE(o,v) (*(volatile u16*)(0x1f801c00u+(o))=(u16)(v))
#define SPU_READ(o) (*(volatile u16*)(0x1f801c00u+(o)))
#define SPU_DELAY() do {for(volatile int z=0;z<256;z++)__asm__ volatile("nop");}while(0)
#endif
#define SPU_ATTR 0x1aa
#define SPU_STAT 0x1ae
#define SPU_KON 0x188
#define SPU_KOF 0x18c
#ifndef SPU_POLL_LIMIT
#define SPU_POLL_LIMIT 200000
#endif
static int sfx_ready,sfx_voice;
static int spu_wait(int mask,int value){for(int i=0;i<SPU_POLL_LIMIT;i++)if((SPU_READ(SPU_STAT)&mask)==value)return 1;return 0;}
static int spu_mode(int mode){SPU_WRITE(SPU_ATTR,0x8000|mode);return spu_wait(0x3f,mode);}
static int spu_upload(void){
 for(int i=0;i<SFX_BANK_BYTES/2;i+=32){
  if(!spu_mode(0))return 0;
  SPU_WRITE(0x1a6,(SFX_BANK_ADDR+i*2)/8);
  for(int k=0;k<32;k++)SPU_WRITE(0x1a8,sfx_bank[i+k]);
  if(!spu_mode(0x10))return 0;
  SPU_DELAY();if(!spu_wait(0x400,0))return 0;
 }
 return spu_mode(0);
}
static int sfx_init(void){sfx_ready=sfx_voice=0;SPU_WRITE(0x180,0);SPU_WRITE(0x182,0);SPU_WRITE(SPU_ATTR,0);if(!spu_wait(0x3f,0))return 0;SPU_WRITE(0x1ac,4);SPU_WRITE(SPU_KOF,0xffff);SPU_WRITE(SPU_KOF+2,0xff);for(int i=0x190;i<=0x19a;i+=2)SPU_WRITE(i,0);SPU_WRITE(0x184,0);SPU_WRITE(0x186,0);
 for(int v=0;v<24;v++){int o=v*16;SPU_WRITE(o,0);SPU_WRITE(o+2,0);SPU_WRITE(o+4,0);SPU_WRITE(o+6,SFX_BANK_ADDR/8);SPU_WRITE(o+8,0x000f);SPU_WRITE(o+10,0);SPU_WRITE(o+14,SFX_BANK_ADDR/8);}
 if(!spu_upload()){SPU_WRITE(SPU_ATTR,0);return 0;}SPU_WRITE(SPU_ATTR,0xc000);if(!spu_wait(0x3f,0))return 0;SPU_WRITE(0x180,0x3000);SPU_WRITE(0x182,0x3000);return sfx_ready=1;
}
static void sfx_stop(void){if(sfx_ready)SPU_WRITE(SPU_KOF,0x00f0);sfx_voice=0;}
static void sfx_play(int sample){if(!sfx_ready||(unsigned)sample>=2)return;int v=4+(sfx_voice++&3),o=v*16;SPU_WRITE(o,0x2200);SPU_WRITE(o+2,0x2200);SPU_WRITE(o+4,sfx_pitch[sample]);SPU_WRITE(o+6,sfx_start[sample]);SPU_WRITE(o+8,0x000f);SPU_WRITE(o+10,0);SPU_WRITE(o+14,SFX_BANK_ADDR/8);SPU_WRITE(SPU_KON,1u<<v);}
