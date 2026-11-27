/* Source-derived Luau container and capture controller. No artificial quest unlocks. */
#ifndef LUAU_OBJECTS68_H
#define LUAU_OBJECTS68_H
#include "propsdata68.h"
#include "dfdata68.h"
#define PROP68_COUNT (sizeof actors59/sizeof actors59[0])
#define DF68_COUNT (sizeof dfplace63/sizeof dfplace63[0])
#define PROP68_ID 0x7000
#define BUB68_ID 0x7002
#define BUB68_COUNT 12
typedef struct {int x,y,z,vx,vz,floor,life;} Bubble68;
typedef struct {U8 prop[PROP68_COUNT],found[DF68_COUNT],caught[DF68_COUNT];Bubble68 b[BUB68_COUNT];int tick,mode,cool,breaks,pickups,score,flies;} Objects68;
static Objects68 objects68;
static void reset_objects68(void){volatile U8 *q=(volatile U8*)&objects68;for(unsigned i=0;i<sizeof objects68;i++)q[i]=0;}
static int near68(int x,int y,int z,int a,int b,int c,int r,int v){int dx=x-a,dz=z-c;return abs18(dx)<=r&&abs18(dz)<=r&&abs18(y-b)<=v&&dx*dx+dz*dz<=r*r;}
/* Sample the actual water column along the underwater segment. Missing beds block. */
static int waterpath68(const Cache18*c,int x,int y,int z,int gx,int gy,int gz){if(!near68(x,y,z,gx,gy,gz,350,250))return 0;for(int i=0;i<=4;i++){int s,b,xx=x+(gx-x)*i/4,yy=y+(gy-y)*i/4,zz=z+(gz-z)*i/4;if(!wet67(c,xx,zz,&s,&b)||yy<s+20||yy>b-20)return 0;}return 1;}
static int pose68(const Cache18*c,int i,int*p,const short*sn){const DfPlacement63*d=dfplace63+i;if(d->deferred||objects68.caught[i])return 0;int f=cache18_floor(c,d->x,d->z,d->y,350);if(f==NONE18)return 0;p[0]=d->x;p[1]=(d->y<f-100?d->y:f-125)+(sn[(objects68.tick*2+i*11)&63]*14>>12);p[2]=d->z;p[3]=f;return 1;}
static void objects_step68(Player18*p,int ox,int oy,int oz,int btn,const short*sn){Objects68*s=&objects68;s->breaks=s->pickups=0;s->tick=(s->tick+1)&255;
 for(unsigned i=0;i<PROP68_COUNT;i++){const ActorPlacement59*a=actors59+i;int wet=a->model==0;int target=a->y-100;
  if(s->prop[i]==2||wet!=swim67.active||!near68(p->x,p->y,p->z,a->x,target,a->z,350,250))continue;
  int path=wet?waterpath68(&cache,p->x,p->y-40,p->z,a->x,target,a->z):path20(&cache,p->x,p->ground,p->z,a->x,a->y,a->z,350);if(!path)continue;
  if(!s->prop[i]){int hit=0;if((btn&PAD_SQUARE)&&(ox!=p->x||oz!=p->z||(wet&&oy!=p->y)))for(int k=0;k<=4;k++)if(near68(ox+(p->x-ox)*k/4,p->y-60,oz+(p->z-oz)*k/4,a->x,target,a->z,145,150)){hit=1;break;}if(hit){s->prop[i]=1;s->breaks++;}continue;}
  if(near68(p->x,p->y-40,p->z,a->x,target,a->z,180,160)){s->prop[i]=2;s->score+=wet?2:5;s->pickups++;}
 }
 /* Existing dry-floor collector cannot see submerged gems. Reuse the same
    source-ID ledger, and require a real water column along the pickup path. */
 if(swim67.active)for(int j=0;j<cache.count;j++){int k=cache.active[j];const U32*m=cache.meta[k];const U8*t=cache.bytes[k]+64+36*m[1]+24*m[2];for(U32 n=0;n<m[3];n++,t+=16){if(s18(t+6)!=1)continue;int id=gemid20(rd18(t+12)),value=s18(t+8),x=s18(t)+(int)m[4],y=s18(t+2)+(int)m[5]-40,z=s18(t+4)+(int)m[6];if(id>=0&&!collect.taken[id]&&near68(p->x,p->y-40,p->z,x,y,z,180,160)&&waterpath68(&cache,p->x,p->y-40,p->z,x,y,z))take20(&collect,id,value,0);}}
 if(s->cool)s->cool--;for(int i=0;i<BUB68_COUNT;i++){Bubble68*b=s->b+i;if(!b->life)continue;int x=b->x+b->vx,z=b->z+b->vz,f=cache18_floor(&cache,x,z,b->floor,110);if(swim67.active||f==NONE18||b->y>=f||!path20(&cache,b->x,b->floor,b->z,x,f,z,70)){b->life=0;continue;}b->x=x;b->z=z;b->floor=f;b->life--;}
 if(!swim67.active&&s->mode&&(btn&PAD_CIRCLE)&&!s->cool){int a=sn[p->heading&63],b=sn[(p->heading+16)&63],x=p->x+(a*95>>12),z=p->z+(b*95>>12),f=cache18_floor(&cache,x,z,p->ground,110);if(f!=NONE18&&p->y-125<f&&path20(&cache,p->x,p->ground,p->z,x,f,z,110))for(int i=0;i<BUB68_COUNT;i++)if(!s->b[i].life){s->b[i]=(Bubble68){x,p->y-125,z,a*31>>12,b*31>>12,f,22};s->cool=7;break;}}
 if(!swim67.active)for(unsigned i=0;i<DF68_COUNT;i++){const DfPlacement63*d=dfplace63+i;if(abs18(d->x-p->x)>1000||abs18(d->z-p->z)>1000)continue;int q[4];if(!pose68(&cache,i,q,sn))continue;if(path20(&cache,p->x,p->ground,p->z,q[0],q[3],q[2],650))s->found[i]=1;for(int j=0;j<BUB68_COUNT;j++){Bubble68*b=s->b+j;if(b->life&&near68(b->x,b->y,b->z,q[0],q[1],q[2],95,125)&&path20(&cache,b->x,b->floor,b->z,q[0],q[3],q[2],125)){b->life=0;s->found[i]=s->caught[i]=1;s->flies++;break;}}}
}
#endif
