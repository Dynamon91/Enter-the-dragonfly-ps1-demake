/* Asset-free diagnostic: automatic or controller-driven combat sequence rendered as GPU bars.
 * No claim of real gameplay, geometry or emulator verification. */
typedef unsigned int u32;
#include "combat40.h"
#define GP0 (*(volatile u32*)0x1f801810)
#define GP1 (*(volatile u32*)0x1f801814)
#define ISTAT (*(volatile u32*)0x1f801070)
static void gp(u32 x){while(!(GP1&(1u<<26))){}GP0=x;}
static u32 xy(int x,int y){return (u32)x|((u32)y<<16);}
static void rect(int x,int y,int w,int h,u32 c){gp(0x60000000|c);gp(xy(x,y));gp(xy(w,h));}
#define JOY_DATA (*(volatile unsigned char*)0x1f801040)
#define JOY_STAT (*(volatile u32*)0x1f801044)
#define JOY_MODE (*(volatile unsigned short*)0x1f801048)
#define JOY_CTRL (*(volatile unsigned short*)0x1f80104a)
#define JOY_BAUD (*(volatile unsigned short*)0x1f80104e)
static void delay(int n){while(n--)__asm__ volatile("nop");}
static int waitpad(u32 mask){for(int i=0;i<6000;i++)if(JOY_STAT&mask)return 1;return 0;}
static int bytepad(int v,int ack){if(!waitpad(1))return -1;JOY_DATA=v;if(!waitpad(2))return -1;int r=JOY_DATA;if(ack){if(!waitpad(1u<<9))return -1;for(int i=0;i<6000&&(JOY_STAT&128);i++){}JOY_CTRL=0x1013;ISTAT=~128u;}return r;}
static int pad(void){int id,lo,hi;JOY_CTRL=0;delay(40);JOY_MODE=13;JOY_BAUD=0x88;JOY_CTRL=0x1013;delay(100);if(bytepad(1,1)<0)goto fail;id=bytepad(0x42,1);if(id!=0x41&&id!=0x73&&id!=0x53)goto fail;if(bytepad(0,1)!=0x5a)goto fail;lo=bytepad(0,1);hi=bytepad(0,id!=0x41);if(lo<0||hi<0)goto fail;if(id!=0x41)for(int i=0;i<4;i++)if(bytepad(0,i<3)<0)goto fail;JOY_CTRL=0;return (~(lo|(hi<<8)))&65535;fail:JOY_CTRL=0;return 0;}
static void vblank(void){ISTAT=~1u;while(!(ISTAT&1u)){}ISTAT=~1u;}
void main40(void){
 GP1=0;GP1=0x03000001;GP1=0x05000000;GP1=0x06c60260;GP1=0x07042018;GP1=0x08000001;
 gp(0xe1000400);gp(0xe3000000);gp(0xe4000000|319|(239<<10));gp(0xe5000000);gp(0xe6000000);GP1=0x03000000;
 Ripto40 b;Enemy40 e={2,0,0};ripto_start40(&b,100,0);int frame=0,done=0,auto_mode=1,breath=FIRE40,prev=0;
 for(;;){vblank();int keys=pad(),edge=keys&~prev;prev=keys;
 if(edge&1)auto_mode=!auto_mode;if(edge&4096)breath=(breath+1)%3;
 if(edge&16384){ripto_start40(&b,100,0);e=(Enemy40){2,0,0};done=0;}
 if(!auto_mode){if(edge&8192){ripto_hit40(&b,breath,1);enemy_hit40(&e,breath,0);}if(edge&32768)enemy_hit40(&e,breath,1);}
 if(frame&1){ripto_tick40(&b);enemy_tick40(&e);if(auto_mode&&b.state==EXPOSE40&&b.timer==40)ripto_hit40(&b,b.phase-1,1);if(auto_mode&&frame%180==1&&e.state!=DEAD40)enemy_hit40(&e,ICE40,0);if(auto_mode&&frame%180==91)enemy_hit40(&e,ICE40,1);if(auto_mode&&b.state==END40&&++done==120){ripto_start40(&b,100,0);e=(Enemy40){2,0,0};done=0;}}
 rect(0,0,320,240,0x241a18);for(int i=0;i<3;i++)rect(20+96*i,20,88,12,i<b.cleared?0x55d070:i==b.phase-1?0x40caff:0x494048);
 rect(30,54,260,24,0x494048);if(b.shield)rect(30,54,80*b.shield,24,b.phase==1?0xe0a060:0x2050ff);
 rect(30,90,260,24,0x494048);if(b.hp)rect(30,90,40*b.hp,24,0x5050d0);
 rect(30,126,260,12,0x494048);if(b.timer)rect(30,126,4*b.timer,12,b.state==EXPOSE40?0x70d060:0x2080e0);
 rect(30,164,80,40,e.state==DEAD40?0x444444:e.state==FROZEN40?0xffc080:0x70a050);
 if(ripto_full40(&b))rect(130,164,160,40,0x55d070);
 rect(30,216,32,10,auto_mode?0x55d070:0x2080e0);rect(72,216,32,10,breath==FIRE40?0x2050ff:breath==ICE40?0xffc080:0x40caff);frame=(frame+1)%36000;}
}
