#ifndef PLATFORM65_H
#define PLATFORM65_H
#include "platformdata65.h"
typedef struct {int x,y,z,path,at,dir,phase,wait;} Lift65;
static int abs65(int x){return x<0?-x:x;}
static int deck65(const Lift65*l,int x,int z){int dx=x-l->x,dz=z-l->z;return abs65(dx)<=365&&abs65(dz)<=365&&dx*dx+dz*dz<=365*365;}
static void lift_reset65(Lift65*l,int i){l->x=platformstart65[i][0];l->y=platformstart65[i][1];l->z=platformstart65[i][2];l->path=l->at=l->phase=l->wait=0;l->dir=1;}
static void lift_path65(Lift65*l,int path){l->path=path;l->at=platformoff65[path];l->dir=1;}
/* Source calls/returns; spline evaluation reconstructed as bounded linear travel. */
static int lift_call65(Lift65*l,int i){if(l->phase)return 0;l->phase=1;lift_path65(l,i?2:0);return 1;}
static int lift_return65(Lift65*l,int i){if(l->phase!=2)return 0;l->phase=3;lift_path65(l,i?4:1);return 1;}
static int lift_motion65(Lift65*l,int i){if(!l->phase||l->phase==5||l->phase==6||(l->phase==2&&!i))return 0;const short*p=platformpath65[l->at];int dx=p[0]-l->x,dy=p[1]-l->y,dz=p[2]-l->z;int m=abs65(dx);if(abs65(dy)>m)m=abs65(dy);if(abs65(dz)>m)m=abs65(dz);int speed=l->phase==2?16:(i&&l->phase==1?50:66);
 if(m>speed){l->x+=dx*speed/m;l->y+=dy*speed/m;l->z+=dz*speed/m;return 0;}
 l->x=p[0];l->y=p[1];l->z=p[2];int next=l->at+l->dir;if(next>=platformoff65[l->path]&&next<platformoff65[l->path+1]){l->at=next;return 0;}
 if(l->phase==1){l->phase=5;l->wait=0;return 1;}
 if(l->phase==2){l->dir=-l->dir;l->at+=l->dir;return 0;}
 if(i&&l->path==4){lift_path65(l,5);return 0;}
 /* Endpoint differs slightly from placed pose. Do not teleport back to placement. */
 l->phase=0;return 2;
}
#endif
