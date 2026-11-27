#ifndef PORTAL73_H
#define PORTAL73_H
#include "session72.h"
#include "portaldata73.h"
static int nearportal73(int x,int y,int z){for(int i=0;i<9;i++){const Portal73*p=portals73+i;int dx=x-p->x,dz=z-p->z,dy=y-p->floor;if(!p->ready)continue;if(dx>=-520&&dx<=520&&dz>=-520&&dz<=520&&dy>=-150&&dy<=150&&dx*dx+dz*dz<=520*520)return i;}return -1;}
static int unlocked_count73(U72 count,int i){return i>=0&&i<9&&portals73[i].ready&&count>=(U72)portals73[i].threshold;}
static int unlocked73(const Session72*s,int i){return unlocked_count73(total72(s,1),i);}
static int request73(Session72*s,int to){if(s->magic!=SESSION72_MAGIC||s->world>=10||to<0||to>=10||(U72)to==s->world)return 0;s->requested=(U72)to+1;return 1;}
static int pop73(Session72*s){U72 w=s->requested;s->requested=0;return w>=1&&w<=10?(int)w-1:-1;}
#endif
