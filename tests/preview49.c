#include <stdio.h>
#include "screen49.h"
static unsigned char pixels[240][320][3];
static void rect(int x,int y,int w,int h,unsigned c){for(int j=y;j<y+h;j++)for(int i=x;i<x+w;i++)if(i>=0&&i<320&&j>=0&&j<240){pixels[j][i][0]=c;pixels[j][i][1]=c>>8;pixels[j][i][2]=c>>16;}}
int main(void){screen49(rect,1,0,4864);fputs("P6\n320 240\n255\n",stdout);fwrite(pixels,1,sizeof pixels,stdout);return 0;}
