/* Source flags: fuse 48 -> rescue 0 -> door 1 -> escaped 7.
 * Six source spline control points per cow, approximated by linear segments.
 * No synthetic quest-completion inputs; call only on a real flame hit. */
#ifndef BARN61_H
#define BARN61_H
#include "talk60.h"
typedef struct {int x,y,z,segment,tick,steps,yaw;} EscapeCow61;
typedef struct {EscapeCow61 cows[5];int phase,timer,door,escaped;} Barn61;
static int abs61(int n){return n<0?-n:n;}
static int heading61(int dx,int dz){if(abs61(dx)>2*abs61(dz))return dx>0?16:48;if(abs61(dz)>2*abs61(dx))return dz>0?0:32;return dz>0?(dx>0?8:56):(dx>0?24:40);}
static void barn_reset61(Barn61*b,const short route[5][7][3]){b->phase=b->timer=b->door=b->escaped=0;for(int i=0;i<5;i++){EscapeCow61*c=b->cows+i;c->x=route[i][0][0];c->y=route[i][0][1];c->z=route[i][0][2];c->yaw=16;c->segment=c->tick=c->steps=0;}}
static int barn_hit61(Barn61*b,Talk60*t){if(b->phase||active60(t))return 0;put60(t->flags[0],48,1);b->phase=1;b->timer=20;return 1;}
static void barn_tick61(Barn61*b,Talk60*t,const short route[5][7][3]){if(active60(t)||!b->phase||b->phase==4)return;
 if(b->phase==1){if(--b->timer<=0){put60(t->flags[0],0,1);b->phase=2;}return;}
 if(b->phase==2){if(++b->door==16){put60(t->flags[0],1,1);b->phase=3;}return;}
 int finished=0;for(int i=0;i<5;i++){EscapeCow61*c=b->cows+i;if(c->segment>=6){finished++;continue;}
  const short*a=route[i][c->segment],*d=route[i][c->segment+1];int dx=d[0]-a[0],dy=d[1]-a[1],dz=d[2]-a[2];
  if(!c->steps){int x=abs61(dx),z=abs61(dz);c->steps=((x>z?x:z)+(x<z?x:z)/2+65)/66;if(c->steps<1)c->steps=1;c->yaw=heading61(dx,dz);}
  int k=++c->tick;c->x=a[0]+dx*k/c->steps;c->y=a[1]+dy*k/c->steps;c->z=a[2]+dz*k/c->steps;
  if(k==c->steps){c->segment++;c->tick=c->steps=0;if(c->segment==6)finished++;}
 }b->escaped=finished;if(finished==5){put60(t->flags[0],7,1);b->phase=4;}}
/* Thin closed-door proxy, restricted to the original doorway and height.
 * Only used during the locked/partially open phase, not terrain replacement. */
static int barn_pass61(const Barn61*b,int x,int y,int z,int nx,int nz){if(b->phase>=3||y< -1300||y> -350)return 1;int a=x-2897,d=nx-2897;if((a<0&&d>=0)||(a>=0&&d<0)){int zz=z+(nz-z)*a/(a-d);if(zz>=2990&&zz<=4405)return 0;}return 1;}
#endif
