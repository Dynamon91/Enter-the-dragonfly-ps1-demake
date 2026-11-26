typedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;
#define GP0 (*(volatile u32*)0x1f801810)
#define GP1 (*(volatile u32*)0x1f801814)
#define ISTAT (*(volatile u32*)0x1f801070)
#define IMASK (*(volatile u32*)0x1f801074)
#define JOY_DATA (*(volatile unsigned char*)0x1f801040)
#define JOY_STAT (*(volatile u32*)0x1f801044)
#define JOY_MODE (*(volatile u16*)0x1f801048)
#define JOY_CTRL (*(volatile u16*)0x1f80104a)
#define JOY_BAUD (*(volatile u16*)0x1f80104e)
static void gp(u32 x){while(!(GP1&(1u<<25))){}GP0=x;}
static void idle(void){GP1=0x02000000;ISTAT=~2u;gp(0x1f000000);while(!(GP1&(1u<<24))){}GP1=0x02000000;ISTAT=~2u;}
static void vb(void){ISTAT=~1u;while(!(ISTAT&1)){}ISTAT=~1u;}
static void delay(int n){while(n--)__asm__ volatile("nop");}
static int joy_wait(u32 mask){for(int i=0;i<6000;i++)if(JOY_STAT&mask)return 1;return 0;}
static int joy_byte(int val,int ack){
 if(!joy_wait(1))return -1;JOY_DATA=val;if(!joy_wait(2))return -1;int r=JOY_DATA;
 if(ack){if(!joy_wait(1u<<9))return -1;for(int i=0;i<6000&&(JOY_STAT&128);i++){}JOY_CTRL=0x1013;ISTAT=~128u;}
 return r;
}
static int read_pad(int*ax,int*az){
 int id,a,b,lo,hi,rx,ry,lx,ly;*ax=*az=0;JOY_CTRL=0;delay(40);JOY_MODE=0x000d;JOY_BAUD=0x88;JOY_CTRL=0x1013;delay(100);
 a=joy_byte(1,1);if(a<0)goto fail;id=joy_byte(0x42,1);if(id!=0x41&&id!=0x73&&id!=0x53)goto fail;
 b=joy_byte(0,1);if(b!=0x5a)goto fail;lo=joy_byte(0,1);hi=joy_byte(0,id!=0x41);if(lo<0||hi<0)goto fail;
 if(id!=0x41){rx=joy_byte(0,1);ry=joy_byte(0,1);lx=joy_byte(0,1);ly=joy_byte(0,0);if(rx<0||ry<0||lx<0||ly<0)goto fail;*ax=lx-128;*az=128-ly;}
 JOY_CTRL=0;return (~(lo|(hi<<8)))&65535;
 fail:JOY_CTRL=0;return 0;
}
#include "resident17.c"
extern int cd17_init(void);extern int cd17_read(void*,U32,U32,U8*);
#include "colors17.h"
static Resident17 resident;static U8 idx[12288],scratch[2048];static U32 ext[2],data[2],volume;static int status;
static u32 xy(int x,int y){return ((u32)x&65535)|(((u32)y&65535)<<16);}
static int s16r(const U8*p){return (s16)(p[0]|p[1]<<8);}
static unsigned u16r(const U8*p){return (unsigned)(p[0]|p[1]<<8);}
static int read_relative(void*ctx,U32 lba,U32 n,U8*dst){(void)ctx;return cd17_read(0,data[0]+lba,n,dst);}
static int mount(void){U32 pvd[2];if(!cd17_init()||!cd17_read(0,16,1,scratch)||!iso17_pvd(scratch,pvd))return 0;volume=pvd[0];if(!cd17_read(0,pvd[1],1,scratch)||!iso17_find(scratch,"HUBSECT.IDX;1",volume,ext)||!iso17_find(scratch,"HUBSECT.DAT;1",volume,data)||ext[1]!=10456||data[1]%2048)return 0;return cd17_read(0,ext[0],(ext[1]+2047)/2048,idx);}
static void rect(int x,int y,int w,int h,u32 c){gp(0x60000000|c);gp(xy(x,y));gp(xy(w,h));}
static void number(int x,int y,int n){static const u16 digits[10]={0x7b6f,0x2492,0x73e7,0x73cf,0x5bc9,0x79cf,0x79ef,0x7249,0x7bef,0x7bcf};for(int d=0;d<4;d++){int div=d==0?1000:d==1?100:d==2?10:1;u16 bits=digits[(n/div)%10];for(int j=0;j<15;j++)if(bits&(1<<(14-j)))rect(x+d*9+(j%3)*2,y+(j/3)*2,2,2,0xf4f4f4);}}
/* Orthographic inspection, fit the full block AABB. Sort top-down by Y. */
static u16 order[2730];static int depth[2730];static int last_id=-1,last_mode=-1;
static void draw(int y,int collision){gp(0xe3000000|(y<<10));gp(0xe4000000|319|((y+239)<<10));gp(0xe5000000|(y<<11));gp(0x02241b19);gp(y<<16);gp((240<<16)|320);if(resident.active>=0){const U8*p=resident.slots[resident.active];int nr=resident.meta[1],nc=resident.meta[2];int loX=s16r(p+40),loZ=s16r(p+44),hiX=s16r(p+46),hiZ=s16r(p+50);int spanX=hiX-loX,spanZ=hiZ-loZ,span=spanX>spanZ?spanX:spanZ;if(span<1)span=1;int stride=collision?24:36,n=collision?nc:nr;const U8*q=p+64+(collision?36*nr:0);/* Maximum 24-byte records in one 64 KiB block. */if(n>2730)n=2730;
 if(last_id!=(int)resident.meta[0]||last_mode!=collision){last_id=resident.meta[0];last_mode=collision;for(int i=0;i<n;i++){const U8*t=q+i*stride;int z=s16r(t+2)+s16r(t+8)+s16r(t+14);int j=i;while(j&&depth[order[j-1]]<z){order[j]=order[j-1];j--;}depth[i]=z;order[j]=i;}}
 for(int i=0;i<n;i++){const U8*t=q+order[i]*stride;u32 c=collision?0x759c46:colors17[u16r(t+30)];gp(0x20000000|c);for(int k=0;k<3;k++){int x=s16r(t+6*k),z=s16r(t+6*k+4);gp(xy(160+(x-(loX+hiX)/2)*196/span,128-(z-(loZ+hiZ)/2)*196/span));}}
 const U8*obj=p+64+36*nr+24*nc;for(U32 i=0;i<resident.meta[3];i++,obj+=16){int x=160+(s16r(obj)-(loX+hiX)/2)*196/span,z=128-(s16r(obj+4)-(loZ+hiZ)/2)*196/span;rect(x-1,z-1,3,3,0x35efed);}
 number(10,9,resident.meta[0]);number(120,9,nr);number(230,9,nc);}
 rect(302,8,10,10,status==1?0x37bd4a:0x3030ee);if(collision)rect(302,22,10,10,0x66ccaa);idle();}
int main(void){int y=0,ax,az,prev=0,collision=0;resident17_init(&resident);IMASK=0;JOY_CTRL=0x40;delay(100);JOY_CTRL=0;GP1=0;GP1=0x03000001;GP1=0x06c60260;GP1=0x07042018;GP1=0x08000001;GP1=0x04000001;gp(0xe1000400);gp(0xe2000000);gp(0xe6000000);status=mount();if(status)status=resident17_switch(&resident,idx,ext[1],START17,data[1]/2048,read_relative,0);for(;;){int btn=read_pad(&ax,&az),edge=btn&~prev;prev=btn;int step=(edge&32?1:0)-(edge&128?1:0)+(edge&2048?10:0)-(edge&1024?10:0);if(edge&16384)collision^=1;if(step&&resident.active>=0){int next=(int)resident.meta[0]+step;if(next<0)next=0;if(next>=174)next=173;if(next!=(int)resident.meta[0])status=resident17_switch(&resident,idx,ext[1],next,data[1]/2048,read_relative,0);}draw(y,collision);vb();GP1=0x05000000|(y<<10);GP1=0x03000000;y^=256;}}
