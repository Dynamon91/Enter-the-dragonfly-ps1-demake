/* Original English VAG one-shot. Uses existing CD scratch and SPU voice 8.
 * Optional: a failed upload never keys on. Actual hardware timing unverified. */
typedef struct {U32 id,lba,bytes,crc;} VoiceEntry60;
#include "voicedata60.h"
#define VOICE_ADDR60 0x20000u
#define VOICE_END60 0x70000u
static void voice_stop60(void){if(sfx_ready)SPU_WRITE(SPU_KOF,1u<<8);}
static int voice_play60(int id){
 voice_stop60();if(!sfx_ready||voice_extent60[1]!=VOICE_BYTES60)return 0;
 const VoiceEntry60*e=0;for(unsigned i=0;i<sizeof voices60/sizeof voices60[0];i++)if(voices60[i].id==(U32)id)e=voices60+i;
 if(!e||!e->bytes||e->bytes%16||e->bytes>VOICE_END60-VOICE_ADDR60||e->lba>=VOICE_BYTES60/2048||(e->bytes+2047)/2048>VOICE_BYTES60/2048-e->lba)return 0;
 U32 crc=~0u,done=0;for(U32 off=0;off<e->bytes;){U32 n=(e->bytes-off+2047)/2048;if(n>3)n=3;U32 take=e->bytes-off;if(take>n*2048)take=n*2048;
  if(!cd17_read(0,voice_extent60[0]+off/2048+e->lba,n,tbuf))goto fail;
  for(U32 k=0;k<take;k+=16){U32 j=off+k;U8 f=tbuf[k+1];if((tbuf[k]>>4)>4||(tbuf[k]&15)>12||f!=(j==e->bytes-16?7:j==e->bytes-32?1:0))goto fail;if(f==7)for(int a=2;a<16;a++)if(tbuf[k+a])goto fail;}
  for(U32 k=0;k<take;k++){crc^=tbuf[k];for(int j=0;j<8;j++)crc=(crc>>1)^(0xedb88320u&-(crc&1));}
  for(U32 k=0;k<take;k+=64){if(!spu_mode(0))goto fail;SPU_WRITE(0x1a6,(VOICE_ADDR60+done)/8);for(U32 j=0;j<64;j+=2){U32 v=k+j<take?tbuf[k+j]|(U32)tbuf[k+j+1]<<8:0;SPU_WRITE(0x1a8,v);}if(!spu_mode(0x10))goto fail;SPU_DELAY();if(!spu_wait(0x400,0))goto fail;done+=64;}
  off+=take;
 }
 if(~crc!=e->crc||!spu_mode(0))goto fail;
 SPU_WRITE(SPU_ATTR,0xc000);if(!spu_wait(0x3f,0))goto fail;
 SPU_WRITE(128,0x2600);SPU_WRITE(130,0x2600);SPU_WRITE(132,0x800);SPU_WRITE(134,VOICE_ADDR60/8);SPU_WRITE(136,0x000f);SPU_WRITE(138,0);SPU_WRITE(142,(VOICE_ADDR60+e->bytes-16)/8);SPU_WRITE(SPU_KON,1u<<8);return 1;
 fail:SPU_WRITE(SPU_ATTR,0xc000);voice_stop60();return 0;
}
