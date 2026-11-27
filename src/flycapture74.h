#ifndef CAPTURE63_H
#define CAPTURE63_H
#include "flydata74.h"
#define BUB_COUNT63 12
#define BUB_ID63 0x700a
/* Hub EDF flags 201,202,203,207,208,209. */
typedef struct {U8 flags[128];} HubFlies73;
static HubFlies73 hubflies73;
static int flag73(const HubFlies73*t,int n){return !!(t->flags[n>>3]&(1u<<(n&7)));}
static void put73(HubFlies73*t,int n){t->flags[n>>3]|=1u<<(n&7);}
static int dragonfly_count63(const HubFlies73*t){int n=0;for(int i=0;i<DF_COUNT63;i++)n+=flag73(t,dfplace63[i].caught);return n;}
static int df_visible63(const HubFlies73*t,int i){return !dfplace63[i].gate&&!flag73(t,dfplace63[i].caught);}
typedef struct {int x,y,z,vx,vz,ground,life;} Bubble63;
typedef struct {Bubble63 b[BUB_COUNT63];int tick,mode,cooldown,event,notice,last_count;} Capture63;
static void capture_reset63(Capture63*s){for(int i=0;i<BUB_COUNT63;i++)s->b[i].life=0;s->tick=s->mode=s->cooldown=s->event=s->notice=s->last_count=0;}
/* Pose retains source placement. Floor-relative hovering is a reconstruction,
 * not the original free-fly waypoint solver. Source elevated placements keep
 * their original height when >100 units above the sampled floor. */
static int df_pose63(const Cache18*c,int i,int tick,const short*sn,int*out){const DfPlacement63*d=dfplace63+i;int g=cache18_floor(c,d->x,d->z,d->y,300);if(g==NONE18)return 0;out[0]=d->x;out[1]=d->y<g-100?d->y:g-125;out[1]+=sn[(tick*2+i*11)&63]*14>>12;out[2]=d->z;out[3]=g;return 1;}
static int bubble_near63(const Bubble63*b,const int*p){int dx=p[0]-b->x,dz=p[2]-b->z;return abs18(dx)<=95&&abs18(dz)<=95&&abs18(p[1]-b->y)<=125&&dx*dx+dz*dz<=95*95;}
static void capture_step63(Capture63*s,HubFlies73*t,const Cache18*c,int x,int y,int z,int ground,int heading,int firing,const short*sn){
 s->event=0;s->tick=(s->tick+1)&255;if(s->notice)s->notice--;if(s->cooldown)s->cooldown--;
 for(int i=0;i<BUB_COUNT63;i++){Bubble63*b=s->b+i;if(!b->life)continue;int nx=b->x+b->vx,nz=b->z+b->vz,g=cache18_floor(c,nx,nz,b->ground,110);if(g==NONE18||b->y>=g||!path20(c,b->x,b->ground,b->z,nx,g,nz,70)){b->life=0;continue;}b->x=nx;b->z=nz;b->ground=g;b->life--;}
 if(s->mode==1&&firing&&!s->cooldown){int a=sn[heading&63],b=sn[(heading+16)&63],fx=x+(a*95>>12),fz=z+(b*95>>12);int g=cache18_floor(c,fx,fz,ground,110);if(g!=NONE18&&y-125<g&&path20(c,x,ground,z,fx,g,fz,110))for(int i=0;i<BUB_COUNT63;i++)if(!s->b[i].life){s->b[i]=(Bubble63){fx,y-125,fz,a*31>>12,b*31>>12,g,22};s->cooldown=7;break;}}
 for(int i=0;i<DF_COUNT63;i++){const DfPlacement63*d=dfplace63+i;if(!df_visible63(t,i)||abs18(x-d->x)>1000||abs18(z-d->z)>1000)continue;int p[4];if(!df_pose63(c,i,s->tick,sn,p))continue;if(path20(c,x,ground,z,p[0],p[3],p[2],650))put73(t,d->found);
  for(int j=0;j<BUB_COUNT63;j++){Bubble63*b=s->b+j;if(b->life&&bubble_near63(b,p)&&path20(c,b->x,b->ground,b->z,p[0],p[3],p[2],125)){b->life=0;put73(t,d->found);put73(t,d->caught);break;}}
 }
 int n=dragonfly_count63(t);if(n>s->last_count){s->event=n-s->last_count;s->notice=100;}s->last_count=n;
}
#endif
