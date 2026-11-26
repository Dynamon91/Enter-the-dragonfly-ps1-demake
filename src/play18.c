/* Separate native streamed traversal experiment; farm gameplay retained as fallback. */
typedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;
#include "scene.h"
#define PAD_SELECT 1
#define PAD_START 8
#define PAD_UP 16
#define PAD_RIGHT 32
#define PAD_DOWN 64
#define PAD_LEFT 128
#define PAD_L1 1024
#define PAD_R1 2048
#define PAD_CROSS 16384
#define PAD_SQUARE 32768
#define PAD_CIRCLE 8192
#define A_WALK_THRESHOLD 90
#include "rig11.h"
#include "cache18.c"
#include "colors17.h"
extern int cd17_init(void);extern int cd17_read(void*,U32,U32,U8*);
extern int iso17_pvd(const U8*,U32*);extern int iso17_find(const U8*,const char*,U32,U32*);
static int ab(int n){return n<0?-n:n;}
static const s16 sine[64]={0,401,799,1189,1567,1931,2276,2598,2896,3166,3406,3612,3784,3920,4017,4076,4096,4076,4017,3920,3784,3612,3406,3166,2896,2598,2276,1931,1567,1189,799,401,0,-401,-799,-1189,-1567,-1931,-2276,-2598,-2896,-3166,-3406,-3612,-3784,-3920,-4017,-4076,-4096,-4076,-4017,-3920,-3784,-3612,-3406,-3166,-2896,-2598,-2276,-1931,-1567,-1189,-799,-401};
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
extern void gte_setup(const u32*);extern void gte_project(const u32*,u32*);
typedef struct {int x,y,z;u32 screen;int u,v;} Point;
#include "frustum07.h"
#include "visibility09.h"
#include "packet14.h"
#define MAXT 10000
#define NO_PACKET 65535u
static Point actorp[NV];static Packet packet[MAXT];static u16 head[1024];static int count,dropped;
static Cache18 cache;static U8 idx[12288],scratch[2048];static U32 ext[2],data[2];static int status;
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
 if(count>=MAXT){dropped++;return;}int ax=(s16)a.screen,ay=(s16)(a.screen>>16),bx=(s16)b.screen,by=(s16)(b.screen>>16),cx=(s16)c.screen,cy=(s16)(c.screen>>16);
 if((ax<0&&bx<0&&cx<0)||(ax>319&&bx>319&&cx>319)||(ay<0&&by<0&&cy<0)||(ay>239&&by>239&&cy>239))return;
 if((bx-ax)*(cy-ay)==(cx-ax)*(by-ay))return;
 /* Reject oversized GPU primitives (PS1 hardware limits). */
 if(ab(ax-bx)>=1024||ab(ax-cx)>=1024||ab(bx-cx)>=1024||ab(ay-by)>=512||ab(ay-cy)>=512||ab(by-cy)>=512)return;
 int bucket=(a.z+b.z+c.z)/24;if(bucket>1023)bucket=1023;if(bucket<0)bucket=0;
 Packet*q=&packet[count];packet_coords(q,a.screen,b.screen,c.screen);q->uv[0]=a.u|(a.v<<8);q->uv[1]=b.u|(b.v<<8);q->uv[2]=c.u|(c.v<<8);q->id=id;q->next=head[bucket];head[bucket]=count++;
}
static void worldtri(Point a,Point b,Point c,int id){
 if(!(clipmask(a)|clipmask(b)|clipmask(c))){emit(a,b,c,id);return;}
 Point out[CLIP_CAP];int k=cliptriangle(a,b,c,out);
 for(int i=0;i<k;i++){Point p=project(out[i].x,out[i].y,out[i].z);out[i].screen=p.screen;}
 for(int i=1;i+1<k;i++)emit(out[0],out[i],out[i+1],id);
}
static void rect(int x,int y,int w,int h,u32 c){gp(0x60000000|c);gp(xy(x,y));gp(xy(w,h));}
static void number(int x,int y,int n){static const u16 digits[10]={0x7b6f,0x2492,0x73e7,0x73cf,0x5bc9,0x79cf,0x79ef,0x7249,0x7bef,0x7bcf};for(int d=0;d<4;d++){int div=d==0?1000:d==1?100:d==2?10:1;u16 bits=digits[(n/div)%10];for(int j=0;j<15;j++)if(bits&(1<<(14-j)))rect(x+d*9+(j%3)*2,y+(j/3)*2,2,2,0xf4f4f4);}}
static int relative(void*ctx,U32 lba,U32 n,U8*dst){(void)ctx;return cd17_read(0,data[0]+lba,n,dst);}
static int mount18(void){U32 pvd[2];if(!cd17_init()||!cd17_read(0,16,1,scratch)||!iso17_pvd(scratch,pvd)||!cd17_read(0,pvd[1],1,scratch)||!iso17_find(scratch,"HUBSECT.IDX;1",pvd[0],ext)||!iso17_find(scratch,"HUBSECT.DAT;1",pvd[0],data)||ext[1]!=10456||data[1]%2048)return 0;return cd17_read(0,ext[0],(ext[1]+2047)/2048,idx);}
typedef struct {int x,y,z,ground,vy,grounded,heading,camera,prev;} Player18;
static int update18(int x,int z){return cache18_update(&cache,idx,ext[1],data[1]/2048,x,z,relative,0);}
static int reset18(Player18*p){if(!update18(36848,-1200))return 0;int f=cache18_floor(&cache,36848,-1200,800,110);if(f==NONE18)return 0;*p=(Player18){36848,f,-1200,f,0,1,0,0,0};return 1;}
static void step18(Player18*p,int btn,int ax,int az){if((btn&PAD_START)&&!(p->prev&PAD_START)){status=reset18(p);p->prev=btn;return;}if(btn&PAD_L1)p->camera=(p->camera-1)&63;if(btn&PAD_R1)p->camera=(p->camera+1)&63;if(btn&PAD_SELECT)p->camera=p->heading;int dx=!!(btn&PAD_RIGHT)-!!(btn&PAD_LEFT),dz=!!(btn&PAD_UP)-!!(btn&PAD_DOWN);if(!dx&&!dz){dx=(ax>35)-(ax<-35);dz=(az>35)-(az<-35);}if(dx||dz){int dir=dz>0?(dx>0?8:dx<0?56:0):dz<0?(dx>0?24:dx<0?40:32):dx>0?16:48;p->heading=(p->camera+dir)&63;int speed=btn&PAD_SQUARE?38:19,nx=p->x+(sine[p->heading]*speed>>12),nz=p->z+(sine[(p->heading+16)&63]*speed>>12);int mid=cache18_floor(&cache,(p->x+nx)/2,(p->z+nz)/2,p->ground,110);int f=cache18_floor(&cache,nx,nz,p->ground,110);if(mid!=NONE18&&f!=NONE18){if(update18(nx,nz)){p->x=nx;p->z=nz;p->ground=f;status=1;}else status=0;}}
 if(p->grounded){p->y=p->ground;if((btn&PAD_CROSS)&&!(p->prev&PAD_CROSS)){p->vy=-38;p->grounded=0;}}if(!p->grounded){p->vy+=3;if((btn&PAD_CROSS)&&p->vy>8)p->vy=8;p->y+=p->vy;if(p->y>=p->ground){p->y=p->ground;p->vy=0;p->grounded=1;}}p->prev=btn;}
static void render18(Player18*p,Anim*a,int y){int sn=sine[p->camera],cs=sine[(p->camera+16)&63],cx=p->x-(sn*560>>12),cz=p->z-(cs*560>>12),cy=p->y-300;gte_setup(identity);count=dropped=0;for(int i=0;i<1024;i++)head[i]=NO_PACKET;
 /* Character submitted first, so the capped packet pool prioritizes it. */
 rig_prepare(a->frame,a->from,a->blend);int as=sine[p->heading],ac=sine[(p->heading+16)&63];for(int i=0;i<NV;i++){int x=(s16)vertices[i][0],yy=(s16)(vertices[i][0]>>16),z=(s16)vertices[i][1],q[3];skin_vertex(a,i,x,yy,z,q);x=q[0];yy=q[1];z=q[2];actorp[i]=transform(p->x+((ac*x+as*z)>>12),p->y-99+yy,p->z+((-as*x+ac*z)>>12),cx,cy,cz,sn,cs);}for(int i=0;i<NF;i++){const u16*f=faces[i];Point v[3];for(int j=0;j<3;j++){v[j]=actorp[f[j]];v[j].u=uvwords[i][j]&255;v[j].v=(uvwords[i][j]>>8)&255;}worldtri(v[0],v[1],v[2],MAT18+i);}
 for(int j=0;j<cache.count;j++){int k=cache.active[j];const U32*m=cache.meta[k];const U8*t=cache.bytes[k]+64;for(U32 i=0;i<m[1];i++,t+=36){int x[3],z[3],mask=15;for(int l=0;l<3;l++){x[l]=s18(t+6*l)+(int)m[4];z[l]=s18(t+6*l+4)+(int)m[6];int dx=x[l]-p->x,dz=z[l]-p->z;mask&=(dx<-1200?1:0)|(dx>1200?2:0)|(dz<-1200?4:0)|(dz>1200?8:0);}if(mask)continue;Point v[3];for(int l=0;l<3;l++)v[l]=transform(x[l],s18(t+6*l+2)+(int)m[5],z[l],cx,cy,cz,sn,cs);worldtri(v[0],v[1],v[2],(u16)(t[30]|t[31]<<8));}}
 gp(0xe3000000|(y<<10));gp(0xe4000000|319|((y+239)<<10));gp(0xe5000000|(y<<11));gp(0x02997154);gp(y<<16);gp((240<<16)|320);for(int b=1023;b>=0;b--)for(int i=head[b];i!=NO_PACKET;i=packet[i].next){Packet*q=&packet[i];int id=q->id;if(id<MAT18){gp(0x20000000|colors17[id]);for(int j=0;j<3;j++)gp(packetxy(q,j));}else{id-=MAT18;gp(0xe2000000);gp(0x24808080);gp(packetxy(q,0));gp(q->uv[0]|(uvwords[id][0]&0xffff0000u));gp(packetxy(q,1));gp(q->uv[1]|(uvwords[id][1]&0xffff0000u));gp(packetxy(q,2));gp(q->uv[2]);}}
 rect(5,5,115,19,0x252027);number(9,9,cache.count);number(50,9,cache.reads%10000);number(91,9,dropped%10000);rect(302,8,10,10,status?0x37bd4a:0x3030ee);idle();}
int main(void){Player18 p={36848,800,-1200,800,0,1,0,0,0};Anim a;anim_reset(&a);cache18_init(&cache);IMASK=0;JOY_CTRL=0x40;delay(100);JOY_CTRL=0;GP1=0;GP1=0x03000001;GP1=0x06c60260;GP1=0x07042018;GP1=0x08000001;GP1=0x04000001;gp(0xe1000400);gp(0xe2000000);gp(0xe6000000);for(int i=0;i<UPLOAD_WORDS;i++)gp(upload[i]);idle();status=mount18()&&reset18(&p);int y=0;for(;;){int ax,az,btn=read_pad(&ax,&az),ox=p.x,oz=p.z,was=p.grounded;if(cache.count)step18(&p,btn,ax,az);anim_step(&a,p.x!=ox||p.z!=oz,btn,was,p.grounded,p.vy,(btn&240)?127:(ab(ax)>ab(az)?ab(ax):ab(az)));render18(&p,&a,y);vb();vb();GP1=0x05000000|(y<<10);GP1=0x03000000;y^=256;}}
