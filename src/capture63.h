#ifndef CAPTURE63_H
#define CAPTURE63_H
#include "talk60.h"
#include "dfdata63.h"
#define DF_COUNT63 4
#define BUB_COUNT63 12
#define DF_REWARDS63 6
#define BUB_ID63 0x700a
/* Original source flags 200,201,203,205 and conversation rewards 204,206.
 * Count committed source identities, not Give opcode calls. */
static int dragonfly_count63(const Talk60*t){static const unsigned short flags[]={200,201,203,204,205,206};int n=0;for(int i=0;i<DF_REWARDS63;i++)n+=flag60(t->flags[0],flags[i]);return n;}
static int df_visible63(const Talk60*t,int i){const DfPlacement63*d=dfplace63+i;return !flag60(t->flags[0],d->caught)&&(!d->gate||flag60(t->flags[0],d->gate));}
typedef struct {int x,y,z,vx,vz,ground,life;} Bubble63;
typedef struct {Bubble63 b[BUB_COUNT63];int tick,mode,cooldown,event,notice,last_count;} Capture63;
static void capture_reset63(Capture63*s){for(int i=0;i<BUB_COUNT63;i++)s->b[i].life=0;s->tick=s->mode=s->cooldown=s->event=s->notice=s->last_count=0;}
/* Pose retains source placement. Floor-relative hovering is a reconstruction,
 * not the original free-fly waypoint solver. Source elevated placements keep
 * their original height when >100 units above the sampled floor. */
static int df_pose63(const Cache18*c,int i,int tick,const short*sn,int*out){const DfPlacement63*d=dfplace63+i;int g=cache18_floor(c,d->x,d->z,d->y,300);if(g==NONE18)return 0;out[0]=d->x;out[1]=d->y<g-100?d->y:g-125;out[1]+=sn[(tick*2+i*11)&63]*14>>12;out[2]=d->z;out[3]=g;return 1;}
static int bubble_near63(const Bubble63*b,const int*p){int dx=p[0]-b->x,dz=p[2]-b->z;return abs18(dx)<=95&&abs18(dz)<=95&&abs18(p[1]-b->y)<=125&&dx*dx+dz*dz<=95*95;}
static void capture_step63(Capture63*s,Talk60*t,const Cache18*c,int x,int y,int z,int ground,int heading,int firing,const short*sn){
 s->event=0;s->tick=(s->tick+1)&255;if(s->notice)s->notice--;if(s->cooldown)s->cooldown--;
 for(int i=0;i<BUB_COUNT63;i++){Bubble63*b=s->b+i;if(!b->life)continue;int nx=b->x+b->vx,nz=b->z+b->vz,g=cache18_floor(c,nx,nz,b->ground,110);if(g==NONE18||b->y>=g||!path20(c,b->x,b->ground,b->z,nx,g,nz,70)){b->life=0;continue;}b->x=nx;b->z=nz;b->ground=g;b->life--;}
 if(s->mode&&firing&&!s->cooldown){int a=sn[heading&63],b=sn[(heading+16)&63],fx=x+(a*95>>12),fz=z+(b*95>>12);int g=cache18_floor(c,fx,fz,ground,110);if(g!=NONE18&&y-125<g&&path20(c,x,ground,z,fx,g,fz,110))for(int i=0;i<BUB_COUNT63;i++)if(!s->b[i].life){s->b[i]=(Bubble63){fx,y-125,fz,a*31>>12,b*31>>12,g,22};s->cooldown=7;break;}}
 for(int i=0;i<DF_COUNT63;i++){const DfPlacement63*d=dfplace63+i;if(!df_visible63(t,i)||abs18(x-d->x)>1000||abs18(z-d->z)>1000)continue;int p[4];if(!df_pose63(c,i,s->tick,sn,p))continue;if(path20(c,x,ground,z,p[0],p[3],p[2],650))put60(t->flags[0],d->found,1);
  for(int j=0;j<BUB_COUNT63;j++){Bubble63*b=s->b+j;if(b->life&&bubble_near63(b,p)&&path20(c,b->x,b->ground,b->z,p[0],p[3],p[2],125)){b->life=0;put60(t->flags[0],d->found,1);put60(t->flags[0],d->caught,1);break;}}
 }
 int n=dragonfly_count63(t);if(n>s->last_count){s->event=n-s->last_count;s->notice=100;}s->last_count=n;
}
#endif
