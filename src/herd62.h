#ifndef HERD62_H
#define HERD62_H
#include "barn61.h"
#include "herddata62.h"
typedef struct {int x,y,z,at,sub,yaw,state;} HerdCow62;
typedef struct {HerdCow62 cow[5];} Herd62;
static void herd_reset62(Herd62*h){for(int i=0;i<5;i++){HerdCow62*c=h->cow+i;const short*p=herdpoints62[herdoff62[i]];c->x=p[0];c->y=p[1];c->z=p[2];c->at=herdoff62[i];c->sub=0;c->yaw=32;c->state=0;}}
static int herd_hit62(Herd62*h,Talk60*t,int i){if(i<0||i>=5||!flag60(t->flags[0],7)||active60(t)||h->cow[i].state)return 0;h->cow[i].state=1;return 1;}
typedef int (*HerdFloor62)(void*,int,int,int);
/* Movement only while nearby player cache contains both positions; no remote CD reads. */
static void herd_tick62(Herd62*h,Talk60*t,int px,int pz,HerdFloor62 floor,void*ctx){if(!flag60(t->flags[0],7)||active60(t))return;for(int i=0;i<5;i++){HerdCow62*c=h->cow+i;if(c->state!=1||abs61(c->x-px)>1100||abs61(c->z-pz)>1100)continue;
 const short*a=herdpoints62[c->at],*b=herdpoints62[c->at+1];int sub=c->sub+1;int x=a[0]+(b[0]-a[0])*sub/4,z=a[2]+(b[2]-a[2])*sub/4;int y=floor(ctx,x,z,c->y);if(y==32767||abs61(y-c->y)>70)continue;
 c->yaw=heading61(b[0]-a[0],b[2]-a[2]);c->x=x;c->y=y;c->z=z;c->sub=sub;if(sub==4){c->sub=0;c->at++;if(c->at+1==herdoff62[i+1]){int dx=x-14394,dz=z+5061;if(dx*dx+dz*dz<=850*850&&abs61(y+192)<=110){c->state=2;put60(t->flags[0],8+i,1);}else c->state=3;}}
 }}
#endif
