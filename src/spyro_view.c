/* Native rotating textured Spyro mesh diagnostic; no SDK or BIOS calls. */
typedef unsigned int u32; typedef unsigned short u16; typedef signed int s32;
#include "scene.h"
#define GP0 (*(volatile u32*)0x1f801810)
#define GP1 (*(volatile u32*)0x1f801814)
#define ISTAT (*(volatile u32*)0x1f801070)
#define IMASK (*(volatile u32*)0x1f801074)
extern void gte_setup(const u32*);
extern void gte_project(const u32*,u32*);
static u32 projected[NV][2];
static int head[1024],next[NF];
static void gp(u32 x) { while (!(GP1&(1u<<25))) {} GP0=x; }
static void idle(void) { GP1=0x02000000; ISTAT=~2u; gp(0x1f000000); while (!(GP1&(1u<<24))) {} GP1=0x02000000; ISTAT=~2u; }
static void vb(void) { ISTAT=~1u;while(!(ISTAT&1)){} ISTAT=~1u; }
static void render(int frame,int y) {
    int i,b;
    gte_setup(matrices[frame]);
    for(i=0;i<NV;i++)gte_project(vertices[i],projected[i]);
    for(i=0;i<1024;i++)head[i]=-1;
    for(i=0;i<NF;i++){
        const u16 *f=faces[i];
        u32 d0=projected[f[0]][1],d1=projected[f[1]][1],d2=projected[f[2]][1];
        if(d0<64||d1<64||d2<64)continue;
        b=(d0+d1+d2)/3;if(b>1023)b=1023;
        next[i]=head[b];head[b]=i;
    }
    gp(0xe3000000|(y<<10)); gp(0xe4000000|319|((y+239)<<10));gp(0xe5000000|(y<<11));
    gp(0x02302018);gp(y<<16);gp((240<<16)|320);
    for(b=1023;b>=0;b--)for(i=head[b];i>=0;i=next[i]){
        const u16 *f=faces[i];
        gp(0x24808080);gp(projected[f[0]][0]);gp(uvwords[i][0]);gp(projected[f[1]][0]);gp(uvwords[i][1]);gp(projected[f[2]][0]);gp(uvwords[i][2]);
    }
    idle();
}
int main(void) {
    int frame=0,y=0;
    IMASK=0;GP1=0;GP1=0x03000001;GP1=0x06c60260;GP1=0x07042018;GP1=0x08000001;
    GP1=0x04000001; /* FIFO DMA request mode; GPUSTAT bit25 = FIFO not full */
    gp(0xe1000400);gp(0xe2000000);gp(0xe6000000);
    for(int i=0;i<UPLOAD_WORDS;i++)gp(upload[i]);idle();
    for(;;){render(frame,y);vb();vb();GP1=0x05000000|(y<<10);GP1=0x03000000;y^=256;frame=(frame+1)&63;}
}
