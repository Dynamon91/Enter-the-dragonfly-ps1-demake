/* Asset-free diagnostic: automatic combat sequence rendered as GPU bars.
 * No claim of real gameplay, geometry or emulator verification. */
typedef unsigned int u32;
#include "combat40.h"
#define GP0 (*(volatile u32*)0x1f801810)
#define GP1 (*(volatile u32*)0x1f801814)
#define ISTAT (*(volatile u32*)0x1f801070)
static void gp(u32 x){while(!(GP1&(1u<<26))){}GP0=x;}
static u32 xy(int x,int y){return (u32)x|((u32)y<<16);}
static void rect(int x,int y,int w,int h,u32 c){gp(0x60000000|c);gp(xy(x,y));gp(xy(w,h));}
static void vblank(void){ISTAT=~1u;while(!(ISTAT&1u)){}ISTAT=~1u;}
void main40(void){
 GP1=0;GP1=0x03000001;GP1=0x05000000;GP1=0x06c60260;GP1=0x07042018;GP1=0x08000001;
 gp(0xe1000000);gp(0xe3000000);gp(0xe4000000|319|(239<<10));gp(0xe5000000);gp(0xe6000000);GP1=0x03000000;
 Ripto40 b;Enemy40 e={2,0,0};ripto_start40(&b,100,0);int frame=0,done=0;
 for(;;){vblank();if(frame&1){ripto_tick40(&b);enemy_tick40(&e);if(b.state==EXPOSE40&&b.timer==40)ripto_hit40(&b,b.phase-1,1);if(frame%180==1&&e.state!=DEAD40)enemy_hit40(&e,ICE40,0);if(frame%180==91)enemy_hit40(&e,ICE40,1);if(b.state==END40&&++done==120){ripto_start40(&b,100,0);e=(Enemy40){2,0,0};done=0;}}
 rect(0,0,320,240,0x241a18);for(int i=0;i<3;i++)rect(20+96*i,20,88,12,i<b.cleared?0x55d070:i==b.phase-1?0x40caff:0x494048);
 rect(30,54,260,24,0x494048);if(b.shield)rect(30,54,80*b.shield,24,b.phase==1?0xe0a060:0x2050ff);
 rect(30,90,260,24,0x494048);if(b.hp)rect(30,90,40*b.hp,24,0x5050d0);
 rect(30,126,260,12,0x494048);if(b.timer)rect(30,126,4*b.timer,12,b.state==EXPOSE40?0x70d060:0x2080e0);
 rect(30,164,80,40,e.state==DEAD40?0x444444:e.state==FROZEN40?0xffc080:0x70a050);
 if(ripto_full40(&b))rect(130,164,160,40,0x55d070);
 frame=(frame+1)%36000;}
}
