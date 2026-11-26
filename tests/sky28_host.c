/* Run exact sky pass with host projection and record GPU words. Not an emulator. */
typedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;typedef unsigned char U8;
typedef struct {int x,y,z;u32 screen;int u,v;} Point;
#include "frustum07.h"
#include "visibility09.h"
static int uvaxis19(int a,int b,int c,int*out){int lo=a<b?a:b;if(c<lo)lo=c;int hi=a>b?a:b;if(c>hi)hi=c;int base=(lo>>10)*1024;if(hi-base>=4096)return 0;out[0]=(a-base)>>4;out[1]=(b-base)>>4;out[2]=(c-base)>>4;return 1;}
static Point project(int x,int y,int z){int xx=160+220*x/z,yy=120+220*y/z;Point p={x,y,z,((u32)xx&65535)|(((u32)yy&65535)<<16),0,0};return p;}
static u32 words[SKY_HOST_CAP];static int nword,overflow;static void gp(u32 x){if(nword<SKY_HOST_CAP)words[nword++]=x;else overflow=1;}
static void idle(void){}
static void uploadrect19(int x,int y,int w,int h,const U8*p){(void)x;(void)y;(void)w;(void)h;(void)p;}
#include "sky28.h"
int skyhost28(int sn,int cs,u32*out){nword=overflow=0;sky_draw28(sn,cs);if(overflow)return -1;for(int i=0;i<nword;i++)out[i]=words[i];return nword;}
