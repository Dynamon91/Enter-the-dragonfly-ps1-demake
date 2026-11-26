/* Native PS1 farm diagnostic. Source model + original terrain; no SDK dependency. */
typedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;
#include "scene.h"
#include "world.h"
#include "player06.h"
#define GP0 (*(volatile u32*)0x1f801810)
#define GP1 (*(volatile u32*)0x1f801814)
#define ISTAT (*(volatile u32*)0x1f801070)
#define IMASK (*(volatile u32*)0x1f801074)
#define JOY_DATA (*(volatile unsigned char*)0x1f801040)
#define JOY_STAT (*(volatile u32*)0x1f801044)
#define JOY_MODE (*(volatile u16*)0x1f801048)
#define JOY_CTRL (*(volatile u16*)0x1f80104a)
#define JOY_BAUD (*(volatile u16*)0x1f80104e)
#define NEAR 128
#define MAXT (6*(WF+NF))
extern void gte_setup(const u32*);extern void gte_project(const u32*,u32*);
typedef struct {int x,y,z;u32 screen;int u,v;} Point;
#include "frustum07.h"
#include "visibility.h"
#include "visibility09.h"
typedef struct {u32 xy[3];u16 uv[3];u16 id;int next;} Packet;
_Static_assert(sizeof(Packet)==24,"Packet budget");
_Static_assert(WF+NF<=65535,"Primitive ID overflow");
static Point worldp[WV],actorp[NV];static unsigned char worldseen[WV],facevisible[WF];static Packet packet[MAXT];static int head[1024],count;
static const u32 identity[11]={4096,0,4096,0,4096,0,0,0,220,160<<16,120<<16};
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
static u32 xy(int x,int y){return ((u32)x&65535)|(((u32)y&65535)<<16);}
static Point project(int x,int y,int z){Point p={x,y,z,0};if(z>=NEAR){u32 in[2]={xy(x,y),(u32)z},out[2];gte_project(in,out);p.screen=out[0];}return p;}
static Point transform(int x,int y,int z,int cx,int cy,int cz,int sn,int cs){
 Point p=camera_space(x,y,z,cx,cy,cz,sn,cs);if(!clipmask(p))p.screen=project(p.x,p.y,p.z).screen;return p;
}
static void emit(Point a,Point b,Point c,int id){
 if(count>=MAXT)return;int ax=(s16)a.screen,ay=(s16)(a.screen>>16),bx=(s16)b.screen,by=(s16)(b.screen>>16),cx=(s16)c.screen,cy=(s16)(c.screen>>16);
 if((ax<0&&bx<0&&cx<0)||(ax>319&&bx>319&&cx>319)||(ay<0&&by<0&&cy<0)||(ay>239&&by>239&&cy>239))return;
 if((bx-ax)*(cy-ay)==(cx-ax)*(by-ay))return;
 /* Reject oversized GPU primitives (PS1 hardware limits). */
 if(ab(ax-bx)>=1024||ab(ax-cx)>=1024||ab(bx-cx)>=1024||ab(ay-by)>=512||ab(ay-cy)>=512||ab(by-cy)>=512)return;
 int bucket=(a.z+b.z+c.z)/24;if(bucket>1023)bucket=1023;
 Packet*q=&packet[count];q->xy[0]=a.screen;q->xy[1]=b.screen;q->xy[2]=c.screen;q->uv[0]=a.u|(a.v<<8);q->uv[1]=b.u|(b.v<<8);q->uv[2]=c.u|(c.v<<8);q->id=id;q->next=head[bucket];head[bucket]=count++;
}
static void worldtri(Point a,Point b,Point c,int id){
 if(!(clipmask(a)|clipmask(b)|clipmask(c))){emit(a,b,c,id);return;}
 Point out[CLIP_CAP];int k=cliptriangle(a,b,c,out);
 for(int i=0;i<k;i++){Point p=project(out[i].x,out[i].y,out[i].z);out[i].screen=p.screen;}
 for(int i=1;i+1<k;i++)emit(out[0],out[i],out[i+1],id);
}
static void render(Player*p,int y){
 int sn=sine[p->camera],cs=sine[(p->camera+16)&63];int cx=p->x-(sn*560>>12),cz=p->z-(cs*560>>12),cy=p->y-300;
 gte_setup(identity);count=0;for(int i=0;i<1024;i++)head[i]=-1;
 for(int i=0;i<WV;i++)worldseen[i]=0;
 for(int i=0;i<WF;i++)facevisible[i]=0;
 for(int i=0;i<CLUSTER_COUNT;i++)if(cluster_visible(clusters[i],cx,cy,cz,sn,cs)){
  int start=clusters[i][6],n=clusters[i][7];for(int j=0;j<n;j++)facevisible[cluster_faces[start+j]]=1;
 }
 for(int i=0;i<WF;i++){if(!facevisible[i])continue;const u16*f=worldfaces[i];for(int j=0;j<3;j++){int k=f[j];if(!worldseen[k]){worldp[k]=transform(world[k][0],world[k][1],world[k][2],cx,cy,cz,sn,cs);worldseen[k]=1;}}Point a=worldp[f[0]],b=worldp[f[1]],c=worldp[f[2]];a.u=worlduv[i][0]&255;a.v=(worlduv[i][0]>>8)&255;b.u=worlduv[i][1]&255;b.v=(worlduv[i][1]>>8)&255;c.u=worlduv[i][2]&255;c.v=(worlduv[i][2]>>8)&255;worldtri(a,b,c,i);}
 int as=sine[p->heading],ac=sine[(p->heading+16)&63];
 for(int i=0;i<NV;i++){int x=(s16)vertices[i][0],yy=(s16)(vertices[i][0]>>16),z=(s16)vertices[i][1];actorp[i]=transform(p->x+((ac*x+as*z)>>12),p->y-99+yy,p->z+((-as*x+ac*z)>>12),cx,cy,cz,sn,cs);}
 for(int i=0;i<NF;i++){const u16*f=faces[i];Point a=actorp[f[0]],b=actorp[f[1]],c=actorp[f[2]];a.u=uvwords[i][0]&255;a.v=(uvwords[i][0]>>8)&255;b.u=uvwords[i][1]&255;b.v=(uvwords[i][1]>>8)&255;c.u=uvwords[i][2]&255;c.v=(uvwords[i][2]>>8)&255;worldtri(a,b,c,WF+i);}
 gp(0xe3000000|(y<<10));gp(0xe4000000|319|((y+239)<<10));gp(0xe5000000|(y<<11));gp(0x02997154);gp(y<<16);gp((240<<16)|320);
 for(int b=1023;b>=0;b--)for(int i=head[b];i>=0;i=packet[i].next){Packet*q=&packet[i];int id=q->id;if(id<WF){gp(worldwindow[id]);gp(0x24808080);gp(q->xy[0]);gp(q->uv[0]|(worlduv[id][0]&0xffff0000u));gp(q->xy[1]);gp(q->uv[1]|(worlduv[id][1]&0xffff0000u));gp(q->xy[2]);gp(q->uv[2]);}else{id-=WF;gp(0xe2000000);gp(0x24808080);gp(q->xy[0]);gp(q->uv[0]|(uvwords[id][0]&0xffff0000u));gp(q->xy[1]);gp(q->uv[1]|(uvwords[id][1]&0xffff0000u));gp(q->xy[2]);gp(q->uv[2]);}}
 idle();
}
int main(void){Player p;int y=0,ax,az;reset_player(&p);IMASK=0;JOY_CTRL=0x40;delay(100);JOY_CTRL=0;GP1=0;GP1=0x03000001;GP1=0x06c60260;GP1=0x07042018;GP1=0x08000001;GP1=0x04000001;gp(0xe1000400);gp(0xe2000000);gp(0xe6000000);for(int i=0;i<UPLOAD_WORDS;i++)gp(upload[i]);for(int i=0;i<WORLD_UPLOAD_WORDS;i++)gp(worldupload[i]);idle();for(;;){int btn=read_pad(&ax,&az);step_player(&p,btn,ax,az);render(&p,y);vb();vb();GP1=0x05000000|(y<<10);GP1=0x03000000;y^=256;}}
