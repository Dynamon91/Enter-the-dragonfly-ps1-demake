#include "spu49.h"
#define R(a) (*(volatile unsigned short*)(0xbf801c00u+(a)))
#define WAIT49 1000000u
static int mode49(unsigned v){R(0x1aa)=v;for(unsigned i=0;i<WAIT49;i++)if((R(0x1ae)&63)==(v&63))return 1;return 0;}
static int busy49(void){for(unsigned i=0;i<WAIT49;i++)if(!(R(0x1ae)&0x400))return 1;return 0;}
static int ready49;
static const Sample49* loaded49;static unsigned count49;
int spu49_load(const unsigned char*b,unsigned n,const Sample49*s,unsigned count){
 ready49=0;if(!valid_bank49(b,n,s,count))return 0;
 R(0x18c)=0xffff;R(0x18e)=0xff;R(0x180)=0;R(0x182)=0;
 if(!mode49(0x8000))return 0;R(0x1ac)=4;R(0x190)=0;R(0x192)=0;R(0x194)=0;R(0x196)=0;R(0x198)=0;R(0x19a)=0;
 R(0x1a6)=SPU49_BASE/8;
 for(unsigned i=0;i<n;i+=64){if(!mode49(0x8000))return 0;for(unsigned j=0;j<64;j+=2)R(0x1a8)=b[i+j]|((unsigned)b[i+j+1]<<8);if(!mode49(0x8010)||!busy49())return 0;}
 if(!mode49(0xc001))return 0;R(0x180)=0x3fff;R(0x182)=0x3fff;loaded49=s;count49=count;ready49=1;return 1;
}
int spu49_play(unsigned voice,unsigned id,unsigned left,unsigned right){
 if(!ready49||voice>=24||id>=count49||left>0x3fff||right>0x3fff)return 0;const Sample49*s=loaded49+id;
 unsigned v=voice*16;R(v)=left;R(v+2)=right;R(v+4)=s->pitch;R(v+6)=s->address/8;R(v+8)=0x00ff;R(v+10)=0x0000;R(v+14)=(s->address+(s->loop==0xffffffffu?s->bytes-16:s->loop/28*16))/8;
 R(voice<16?0x188:0x18a)=1u<<(voice&15);return 1;
}
void spu49_stop(unsigned voice){if(voice<24)R(voice<16?0x18c:0x18e)=1u<<(voice&15);}
