#include "platform65.h"
static Lift65 lifts65[2];
static void reset_lifts65(void){for(int i=0;i<2;i++)lift_reset65(lifts65+i,i);}
static int player_floor65(int x,int z,int y,int range){int f=cache18_floor(&cache,x,z,y,range);for(int i=0;i<2;i++){const Lift65*l=lifts65+i;if(deck65(l,x,z)&&abs65(l->y-y)<=range&&(f==NONE18||abs65(l->y-y)<abs65(f-y)))f=l->y;}if(f==NONE18)for(int i=0;i<2;i++){const Lift65*l=lifts65+i;if(abs65(l->y-y)<=16&&abs65(l->x-x)<=430&&abs65(l->z-z)<=430){int lower=cache18_floor(&cache,x,z,y+1800,1800);if(lower!=NONE18&&lower>=y)f=lower;}}return f;}
/* Update rider and cache transactionally; a failed cache transition stalls the lift. */
static void lifts_step65(Player18*p,int mode,int fire){if(active60(&talk60))return;for(int i=0;i<2;i++){Lift65*l=lifts65+i;const int*a=polepos64[i];int call=15+2*i,ret=call+1;int rider=deck65(l,p->x,p->z)&&abs65(p->ground-l->y)<=16;int radius=i?6000:3000;int away=abs65(p->x-a[0])>radius||abs65(p->z-a[2])>radius;
 if(mode==2&&fire&&!l->phase&&lightning_hit64(&cache,p->x,p->y,p->z,p->ground,p->heading,a,sine)){if(lift_call65(l,i))put60(talk60.flags[0],call,1);}
 /* Lift 1 needs a ride-back trigger: board at the lower dock and wait.
  * Adaptation of source return condition, not original timing. */
 if(l->phase==2){if(!i&&rider&&p->grounded&&l->wait<30)l->wait++;else if(!rider)l->wait=0;if((!rider&&away)||(!i&&l->wait>=30)){if(lift_return65(l,i))put60(talk60.flags[0],ret,1);}}
 Lift65 next=*l;int event=0;
 /* The current jump cannot reach the source high dock. Lower the deck to a
  * real floor 80 units below it before boarding; the source flight path is unchanged. */
 if(l->phase==5){int ground=cache18_floor(&cache,l->x,l->z,l->y+1000,1000);if(ground!=NONE18&&ground>=l->y){int target=ground-80;if(next.y<target-32)next.y+=32;else{next.y=target;next.phase=6;next.wait=0;}}}
 else if(l->phase==6){if(rider&&p->grounded){if(++next.wait>=30){if(i){next.phase=2;lift_path65(&next,3);}else{next.phase=3;lift_path65(&next,1);put60(talk60.flags[0],ret,1);}}}else if(away){next.phase=3;lift_path65(&next,i?4:1);put60(talk60.flags[0],ret,1);}else next.wait=0;}
 else event=lift_motion65(&next,i);int dx=next.x-l->x,dy=next.y-l->y,dz=next.z-l->z;
 if(rider&&(dx||dy||dz)){int nx=p->x+dx,nz=p->z+dz;if(!cache23_move(&cache,idx,ext[1],data[1]/2048,p->x,p->z,nx,nz,relative,0))continue;p->x=nx;p->z=nz;p->y+=dy;p->ground+=dy;}
 *l=next;if(event==1)put60(talk60.flags[0],call,0);if(event==2)put60(talk60.flags[0],ret,0);
 }}
static void lifts_draw65(Player18*p,int cx,int cy,int cz,int sn,int cs){const ActorModel59*m=models59+6;for(int i=0;i<2;i++){const Lift65*l=lifts65+i;if(ab(l->x-p->x)>3000||ab(l->z-p->z)>3000)continue;for(int f=0;f<m->nf;f++){const ActorFace59*t=m->f+f;Point q[3];for(int j=0;j<3;j++){const short*v=m->v[t->ix[j]];q[j]=transform(l->x+v[0],l->y+v[1],l->z+v[2],cx,cy,cz,sn,cs);q[j].u=t->uv[j*2];q[j].v=t->uv[j*2+1];}worldtri(q[0],q[1],q[2],ACTOR_ID59+6);}}}
/* Only land from above on a deck; do not snap a grounded player upward. */
static int landing65(int x,int z,int before,int after,int ground){for(int i=0;i<2;i++){const Lift65*l=lifts65+i;if(deck65(l,x,z)&&before<=l->y&&after>=l->y&&l->y<ground)ground=l->y;}return ground;}
