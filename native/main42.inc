void *memset(void *p,int v,unsigned long n){volatile unsigned char *b=p;while(n--)*b++=(unsigned char)v;return p;}
#include "arena41.h"
#include "draw41.h"
#include "view42.h"
static View42 view;
static void tri42(P42 a,P42 b,P42 c,unsigned col){gp(0x20000000|col);gp(xy(a.x,a.y));gp(xy(b.x,b.y));gp(xy(c.x,c.y));}
static void draw_page41(int y){gp(0xe3000000|((unsigned)y<<10));gp(0xe4000000|319|((unsigned)(y+239)<<10));gp(0xe5000000|((unsigned)y<<11));}
static void sync41(void){GP1=0x02000000;gp(0x1f000000);while(!(GP1&(1u<<24))){}GP1=0x02000000;ISTAT=~2u;}
void main40(void){
 GP1=0;GP1=0x03000001;GP1=0x05000000;GP1=0x06c60260;GP1=0x07042018;GP1=0x08000001;
 gp(0xe1000400);gp(0xe3000000);gp(0xe4000000|319|(239<<10));gp(0xe5000000);gp(0xe6000000);GP1=0x03000000;
 Arena41 a;arena_init41(&a,0,0);int prev=0,frame=0,latch=0,page=256,ready=0;
 for(;;){vblank();if(ready){GP1=0x05000000|((unsigned)page<<10);page=256-page;ready=0;}int p=pad(),edge=p&~prev;prev=p;if(edge&8)arena_init41(&a,a.id,a.wins);if(edge&1){int id=(a.id+1)%5;arena_init41(&a,id,a.wins);}if(edge&4096)latch=A41_CYCLE;
 if(++frame==2){frame=0;int k=((p&128)?A41_LEFT:0)|((p&32)?A41_RIGHT:0)|((p&16)?A41_UP:0)|((p&64)?A41_DOWN:0)|((p&8192)?A41_BREATH:0)|((p&32768)?A41_CHARGE:0)|latch;step41(&a,k);latch=0;draw_page41(page);render42(&view,&a,rect,tri42);sync41();ready=1;}}
}
