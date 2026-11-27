#ifndef UFO64_H
#define UFO64_H
#include "talk60.h"
#include "ufodata64.h"
/* Source cannon order, flags 3..6; crash flag 23 only after final path.
 * Reconstructed linear spline motion and timing. No fabricated platform ride. */
typedef struct {int stage,phase,timer,at,sub,steps,x,y,z,yaw;} Ufo64;
static void ufo_reset64(Ufo64*u){*u=(Ufo64){0,0,0,0,0,0,ufostart64[0],ufostart64[1],ufostart64[2],0};}
static int ufo_available64(const Ufo64*u,const Talk60*t,int i){if(i<0||i>=4||i!=u->stage||u->phase||!flag60(t->flags[0],0)||flag60(t->flags[0],23)||flag60(t->flags[0],i+3))return 0;for(int k=0;k<i;k++)if(!flag60(t->flags[0],k+3))return 0;return 1;}
static int ufo_trigger64(Ufo64*u,Talk60*t,int i,int breath){if(breath!=2||active60(t)||!ufo_available64(u,t,i))return 0;u->phase=1;u->timer=51;return 1;}
static int ufo_abs64(int n){return n<0?-n:n;}
static void ufo_tick64(Ufo64*u,Talk60*t){if(active60(t)||!u->phase||u->phase==4)return;
 if(u->phase==1){if(--u->timer<=0){put60(t->flags[0],3+u->stage,1);u->phase=2;u->at=ufooff64[u->stage];u->sub=u->steps=0;}return;}
 if(u->phase==3){if(--u->timer<=0){put60(t->flags[0],23,1);put60(t->flags[0],995,1);u->phase=4;}return;}
 const short*d=ufopath64[u->at];int dx=d[0]-u->x,dy=d[1]-u->y,dz=d[2]-u->z;int max=ufo_abs64(dx);if(ufo_abs64(dy)>max)max=ufo_abs64(dy);if(ufo_abs64(dz)>max)max=ufo_abs64(dz);
 if(max<=100){u->x=d[0];u->y=d[1];u->z=d[2];if(++u->at==ufooff64[u->stage+1]){if(++u->stage==4){u->phase=3;u->timer=30;}else u->phase=0;}return;}
 u->x+=dx*100/max;u->y+=dy*100/max;u->z+=dz*100/max;
 if(ufo_abs64(dx)>ufo_abs64(dz))u->yaw=dx>0?16:48;else u->yaw=dz>0?0:32;
}
#endif
