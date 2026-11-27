#ifndef SWIM67_H
#define SWIM67_H
#include "watermat67.h"
/* Wet surfaces come from the actual resident render triangles. Only shallow-sloped
 * original ocean material surfaces count. A separate collision floor must exist. */
static int waterplane67(const Cache18*c,int x,int z){int best=NONE18;
 for(int j=0;j<c->count;j++){int k=c->active[j];const U32*m=c->meta[k];const U8*t=c->bytes[k]+64;int qx=x-(int)m[4],qz=z-(int)m[6];
 for(U32 i=0;i<m[1];i++,t+=36){if(!surface67((U16)(t[30]|t[31]<<8)))continue;
 int ax=s18(t),ay=s18(t+2)+(int)m[5],az=s18(t+4),bx=s18(t+6)-ax,by=s18(t+8)+(int)m[5]-ay,bz=s18(t+10)-az,cx=s18(t+12)-ax,cy=s18(t+14)+(int)m[5]-ay,cz=s18(t+16)-az;
 if(ay< -370||ay> -190||ay+by< -370||ay+by> -190||ay+cy< -370||ay+cy> -190||abs18(by)>150||abs18(cy)>150||abs18(by-cy)>150)continue;
 long long d=cross18(bx,bz,cx,cz),u=cross18(qx-ax,qz-az,cx,cz),v=cross18(bx,bz,qx-ax,qz-az);if(d<0){d=-d;u=-u;v=-v;}if(!d||u<0||v<0||u+v>d)continue;int y=ay+ratio18(u*by+v*cy,d);if(y<best)best=y;
 }}return best;}
/* Source flag 3 surfaces at water height are excluded from the solid-bed query.
 * Flag 0 floor candidates remain subject to the original slope limit. */
static int solid67(const Cache18*c,int x,int z,int ref,int limit){int best=NONE18,dist=limit+1;
 for(int j=0;j<c->count;j++){int k=c->active[j];const U32*m=c->meta[k];const U8*t=c->bytes[k]+64+36*m[1];int qx=x-(int)m[4],qz=z-(int)m[6];
 for(U32 i=0;i<m[2];i++,t+=24){if(s18(t+18)!=0)continue;
 int ax=s18(t),ay=s18(t+2)+(int)m[5],az=s18(t+4),bx=s18(t+6)-ax,by=s18(t+8)+(int)m[5]-ay,bz=s18(t+10)-az,cx=s18(t+12)-ax,cy=s18(t+14)+(int)m[5]-ay,cz=s18(t+16)-az;
 long long d=cross18(bx,bz,cx,cz);if(!d)continue;long long a=d<0?-d:d,nx=cross18(by,bz,cy,cz),nz=cross18(bx,by,cx,cy);if((nx<0?-nx:nx)>2*a||(nz<0?-nz:nz)>2*a)continue;
 long long u=cross18(qx-ax,qz-az,cx,cz),v=cross18(bx,bz,qx-ax,qz-az);if(d<0){d=-d;u=-u;v=-v;}if(u<0||v<0||u+v>d)continue;int y=ay+ratio18(u*by+v*cy,d),dd=abs18(y-ref);if(dd<dist){best=y;dist=dd;}
 }}return best;}
static int wet67(const Cache18*c,int x,int z,int *s,int *bed){int w=waterplane67(c,x,z);if(w==NONE18)return 0;
 int shallow=solid67(c,x,z,w,140);if(shallow!=NONE18)return 0;
 int f=solid67(c,x,z,w+140,4000);if(f==NONE18||f<w+140||f>w+3200)return 0;*s=w;*bed=f;return 1;}
typedef struct {int active,surface,bed;} Swim67;
static Swim67 swim67;
static void swim_reset67(void){swim67.active=0;swim67.surface=swim67.bed=0;}
/* Called after the original step routine. Handles the dry -> water edge before
 * invoking land movement; cache must commit before a position is published. */
static void swim_step67(Player18*p,int btn,int ax,int az){
 if((btn&PAD_START)&&!(p->prev&PAD_START)){swim_reset67();step18(p,btn,ax,az);return;}
 int dx=!!(btn&PAD_RIGHT)-!!(btn&PAD_LEFT),dz=!!(btn&PAD_UP)-!!(btn&PAD_DOWN);if(!dx&&!dz){dx=(ax>35)-(ax<-35);dz=(az>35)-(az<-35);}
 int cam=p->camera;if(btn&PAD_L1)cam=(cam-1)&63;if(btn&PAD_R1)cam=(cam+1)&63;if(btn&PAD_SELECT)cam=p->heading;
 int dir=dz>0?(dx>0?8:dx<0?56:0):dz<0?(dx>0?24:dx<0?40:32):dx>0?16:48;int heading=(dx||dz)?(cam+dir)&63:p->heading;
 int speed=(btn&PAD_SQUARE)?34:22,nx=p->x,nz=p->z;if(dx||dz){nx+=sine[heading]*speed>>12;nz+=sine[(heading+16)&63]*speed>>12;}
 int ws,wb,ms,mb;
 if(!swim67.active){int ns,nf;if(p->grounded&&wet67(&cache,nx,nz,&ns,&nf)&&p->y>=ns-145&&p->y<=ns+140&&cache23_move(&cache,idx,ext[1],data[1]/2048,p->x,p->z,nx,nz,relative,0)){p->x=nx;p->z=nz;p->y=ns+20;p->ground=nf;p->vy=0;p->grounded=0;swim67=(Swim67){1,ns,nf};p->heading=heading;p->camera=cam;p->prev=btn;return;}step18(p,btn,ax,az);if(wet67(&cache,p->x,p->z,&ns,&nf)&&p->y>=ns&&p->y<nf){swim67=(Swim67){1,ns,nf};p->grounded=0;p->vy=0;p->ground=nf;if(p->y>nf-80)p->y=nf-80;}return;}
 p->heading=heading;p->camera=cam;
 if(wet67(&cache,nx,nz,&ws,&wb)&&wet67(&cache,(p->x+nx)/2,(p->z+nz)/2,&ms,&mb)&&abs18(ws-swim67.surface)<=80&&abs18(wb-swim67.bed)<=140&&abs18(mb-swim67.bed)<=140){if(cache23_move(&cache,idx,ext[1],data[1]/2048,p->x,p->z,nx,nz,relative,0)){p->x=nx;p->z=nz;swim67.surface=ws;swim67.bed=wb;}}
 else if((dx||dz)&&p->y<=swim67.surface+70){int f=solid67(&cache,nx,nz,swim67.surface,145);int mid=solid67(&cache,(p->x+nx)/2,(p->z+nz)/2,swim67.surface,145);if(f!=NONE18&&(mid!=NONE18||wet67(&cache,(p->x+nx)/2,(p->z+nz)/2,&ms,&mb))&&cache23_move(&cache,idx,ext[1],data[1]/2048,p->x,p->z,nx,nz,relative,0)){p->x=nx;p->z=nz;p->ground=p->y=f;p->grounded=1;p->vy=0;p->prev=btn;swim_reset67();return;}}
 int yy=p->y;if(btn&PAD_SQUARE)yy+=18;else if(btn&PAD_CROSS)yy-=22;else if(yy<swim67.surface+20)yy+=4;int lo=swim67.surface+20,hi=swim67.bed-80;if(yy<lo)yy=lo;if(yy>hi)yy=hi;p->y=yy;p->ground=swim67.bed;p->grounded=0;p->vy=0;p->prev=btn;
}
#endif
