#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef unsigned int U32;typedef unsigned char U8;
static U8 bank[1617920],tbuf[6144],spu[0x80000];static U32 voice_extent60[2]={100,1617920};static int sfx_ready=1,keys,off,fail,words;static unsigned addr;
#define SPU_KON 0x188
#define SPU_KOF 0x18c
#define SPU_ATTR 0x1aa
static void wr(unsigned r,unsigned v){if(r==SPU_KON){assert(v==256);keys++;}if(r==SPU_KOF)off++;if(r==0x1a6){addr=v*8;assert(addr>=0x20000&&addr+64<=0x70000);words=0;}if(r==0x1a8){assert(words<32);spu[addr+2*words]=v;spu[addr+2*words+1]=v>>8;words++;}}
#define SPU_WRITE(r,v) wr(r,v)
#define SPU_DELAY() ((void)0)
static int spu_mode(int x){(void)x;return !fail;}
static int spu_wait(int m,int v){(void)m;(void)v;return 1;}
static int cd17_read(void*c,U32 l,U32 n,U8*p){(void)c;if(fail==2||l<100||n>3||l-100+n>sizeof bank/2048)return 0;memcpy(p,bank+(l-100)*2048,n*2048);return 1;}
#include "voice60.h"
int main(int argc,char**argv){assert(argc==2);FILE*f=fopen(argv[1],"rb");assert(f&&fread(bank,1,sizeof bank,f)==sizeof bank&&fgetc(f)==EOF);fclose(f);for(unsigned i=0;i<sizeof voices60/sizeof voices60[0];i++){const VoiceEntry60*e=voices60+i;int before=keys;assert(voice_play60(e->id)&&keys==before+1);assert(!memcmp(spu+VOICE_ADDR60,bank+e->lba*2048,e->bytes));bank[e->lba*2048+2]^=1;before=keys;assert(!voice_play60(e->id)&&keys==before);bank[e->lba*2048+2]^=1;}int before=keys;assert(!voice_play60(4105)&&!voice_play60(4113)&&keys==before);fail=1;assert(!voice_play60(4101)&&keys==before);fail=2;assert(!voice_play60(4101)&&keys==before);printf("23 original voice payloads copied exactly; 23 corrupt clips and 4 failure/missing cases reject key-on\n");}
