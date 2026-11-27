#include "combat65.h"
#define ACTORS65 (sizeof actors59/sizeof actors59[0])
typedef struct {int x,y,z,vx,vz,life;} Shot65;
static Enemy65 enemies65[ACTORS65];static Shot65 shots65[12];static int hurt65,dead65,defeats65;
static void combat_reset65(void){for(unsigned i=0;i<ACTORS65;i++){enemies65[i]=(Enemy65){0,0,0,actors59[i].yaw};}for(int i=0;i<12;i++)shots65[i].life=0;hurt65=dead65=defeats65=0;}
static int aim65(int x,int z){int best=0,bestdot=-2147483647;for(int i=0;i<64;i++){int dot=x*sine[i]+z*sine[(i+16)&63];if(dot>bestdot){best=i;bestdot=dot;}}return best;}
static void combat_damage65(void){if(hurt65)return;if(interactions.health)damage21(&interactions);else dead65=1;hurt65=60;}
static void combat_step65(Player18*p,int ox,int oz,int charge,int mode,int fire){if(active60(&talk60))return;if(hurt65)hurt65--;
 for(int i=0;i<12;i++){Shot65*b=shots65+i;if(!b->life)continue;int nx=b->x+b->vx,nz=b->z+b->vz,g=cache18_floor(&cache,b->x,b->z,b->y+100,150),h=cache18_floor(&cache,nx,nz,g,110);if(g==NONE18||h==NONE18||b->y>=h||abs65(h-g)>110||!path20(&cache,b->x,g,b->z,nx,h,nz,100)){b->life=0;continue;}b->x=nx;b->z=nz;b->life--;if(close61(p->x,p->z,nx,nz,75)&&abs65(p->y-110-b->y)<=110){b->life=0;combat_damage65();}}
 for(unsigned i=0;i<ACTORS65;i++){const ActorPlacement59*a=actors59+i;Enemy65*e=enemies65+i;int m=a->model;if(m<2||m>5||ab(p->x-a->x)>1700||ab(p->z-a->z)>1700)continue;
 if(e->state==1){if(path20(&cache,p->x,p->ground,p->z,a->x,a->y,a->z,m==2?240:180)){e->state=2;if(m==2){if(interactions.health<3)interactions.health++;}else interactions.score+=reward65(m);sfx_play(1);}continue;}if(e->state)continue;
 int hit=0;if(charge&&p->grounded&&(ox!=p->x||oz!=p->z)&&path20(&cache,p->x,p->ground,p->z,a->x,a->y,a->z,190))for(int j=0;j<=4;j++)if(near21(ox+(p->x-ox)*j/4,p->y-70,oz+(p->z-oz)*j/4,a->x,a->y,a->z,145)){hit=2;break;}
 if(!hit&&mode==0)for(int j=0;j<FIRE21;j++){Flame21*f=interactions.fire+j;if(f->life&&near21(f->x,f->y,f->z,a->x,a->y,a->z,140)&&path20(&cache,p->x,p->ground,p->z,a->x,a->y,a->z,900)){f->life=0;hit=1;break;}}
 if(!hit&&mode==2&&fire&&light_ticks64==6){int target[3]={a->x,a->y,a->z};if(lightning_hit64(&cache,p->x,p->y,p->z,p->ground,p->heading,target,sine))hit=4;}
 if(hit&&defeat65(e,m,hit)){defeats65++;sfx_play(2);continue;}
 if(m!=3&&m!=4)continue;if(e->cool)e->cool--;int range=m==3?1300:1000;
 if(!path20(&cache,a->x,a->y,a->z,p->x,p->ground,p->z,range)){e->aim=0;continue;}e->yaw=aim65(p->x-a->x,p->z-a->z);
 if(!e->cool&&++e->aim>=22){e->aim=0;e->cool=55;for(int j=0;j<12;j++)if(!shots65[j].life){int s=sine[e->yaw],c=sine[(e->yaw+16)&63];shots65[j]=(Shot65){a->x+(s*100>>12),a->y-100,a->z+(c*100>>12),s*35>>12,c*35>>12,40};break;}}
 }}
static void combat_draw65(Player18*p,int cx,int cy,int cz,int sn,int cs){for(unsigned i=0;i<ACTORS65;i++){const ActorPlacement59*a=actors59+i;if(enemies65[i].state!=1||ab(a->x-p->x)>1300||ab(a->z-p->z)>1300)continue;const CollectFace*f=a->model==2?buttermesh:a->model==5?gemmesh5:gemmesh1;int n=a->model==2?NFACE20(buttermesh):a->model==5?NFACE20(gemmesh5):NFACE20(gemmesh1);mesh20(f,n,a->x,a->y-80,a->z,sine[collect.tick&63],sine[(collect.tick+16)&63],cx,cy,cz,sn,cs);}for(int i=0;i<12;i++){Shot65*b=shots65+i;if(!b->life)continue;Point q[4];for(int j=0;j<4;j++){int a=j&1?24:-24,v=j&2?24:-24;q[j]=transform(b->x+(cs*a>>12),b->y+v,b->z-(sn*a>>12),cx,cy,cz,sn,cs);q[j].u=q[j].v=0;}worldtri(q[0],q[1],q[2],0x83ff);worldtri(q[1],q[2],q[3],0x83ff);}}
static int actor_alive65(unsigned i){return !enemies65[i].state;}
static int actor_yaw65(unsigned i){return enemies65[i].yaw;}
