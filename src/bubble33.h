/* Reconstructed bubble breath and dragonfly flight. No PS2 script claim. */
#include "progress33.h"
#include "dragonflyids33.h"
#define DF33 4
#define BUB33 12
#define BUB_LIFE33 22
typedef struct {int x,y,z,vx,vz,ground,life;} Bubble33;
typedef struct {Bubble33 b[BUB33];int tick,cooldown,breath,event;} Capture33;
static void capture_reset33(Capture33*s){for(int i=0;i<BUB33;i++)s->b[i].life=0;s->tick=s->cooldown=s->breath=s->event=0;}
static int df_index33(U32 id){for(int i=0;i<DF33;i++)if(df_ids33[i]==id)return i;return -1;}
static int df_pose33(const Cache18*c,const U8*t,const U32*m,int id,int tick,const short*sn,int*xyz){int x=s18(t)+(int)m[4],y=s18(t+2)+(int)m[5],z=s18(t+4)+(int)m[6];int f=cache18_floor(c,x,z,y,180);if(f==NONE18)return 0;int phase=(tick+id*13)&63;xyz[0]=x;xyz[1]=f-78+(sn[(phase*2)&63]*18>>12);xyz[2]=z;return 1;}
static int bubble_near33(const Bubble33*b,int x,int y,int z){int dx=x-b->x,dz=z-b->z,dy=y-b->y;return abs18(dx)<=78&&abs18(dz)<=78&&abs18(dy)<=92&&dx*dx+dz*dz<=78*78;}
static void capture_step33(Capture33*s,Progress33*p,const Cache18*c,int x,int y,int z,int heading,int firing,int grounded,const short*sn){s->event=0;s->tick=(s->tick+1)&255;if(s->cooldown)s->cooldown--;
 for(int i=0;i<BUB33;i++){Bubble33*b=s->b+i;if(!b->life)continue;int nx=b->x+b->vx,nz=b->z+b->vz,f=cache18_floor(c,nx,nz,b->ground,110);if(f==NONE18||abs18(f-b->ground)>100||b->y>=f||!path20(c,b->x,b->ground,b->z,nx,f,nz,70)){b->life=0;continue;}b->x=nx;b->z=nz;b->ground=f;b->life--;}
 if(s->breath&&firing&&grounded&&!s->cooldown){int a=sn[heading&63],b=sn[(heading+16)&63],fx=x+(a*95>>12),fz=z+(b*95>>12);int f=cache18_floor(c,fx,fz,y,110);if(f!=NONE18&&path20(c,x,y,z,fx,f,fz,110)){for(int i=0;i<BUB33;i++)if(!s->b[i].life){s->b[i]=(Bubble33){fx,y-125,fz,a*31>>12,b*31>>12,f,BUB_LIFE33};s->cooldown=7;break;}}}
 for(int j=0;j<c->count;j++){int k=c->active[j];const U32*m=c->meta[k];const U8*t=c->bytes[k]+64+m[1]*36+m[2]*24;for(U32 n=0;n<m[3];n++,t+=16){if(s18(t+6)!=4)continue;int id=df_index33(rd18(t+12));if(id<0||!df_enabled33[id]||progress_has33(p,id))continue;int a[3];if(!df_pose33(c,t,m,id,s->tick,sn,a))continue;int floor=cache18_floor(c,a[0],a[2],a[1]+78,110);if(floor==NONE18)continue;
 for(int i=0;i<BUB33;i++){Bubble33*b=s->b+i;if(b->life&&bubble_near33(b,a[0],a[1]-55,a[2])&&path20(c,b->x,b->ground,b->z,a[0],floor,a[2],100)){b->life=0;s->event+=progress_take33(p,id);break;}}
 }}
}
