#include "hubcapture73.h"
#include "font72.h"
static int hub_near73(Player18*p){int i=nearportal73(p->x,p->ground,p->z);if(i<0||!p->grounded)return -1;const Portal73*q=portals73+i;return path20(&cache,p->x,p->ground,p->z,q->x,q->floor,q->z,600)?i:-1;}
static void hubtext73(int x,int y,const char*s,u32 c){for(;*s;s++,x+=6){int ch=*s;if(ch<32||ch>126)continue;for(int j=0;j<10;j++)for(int i=0;i<6;i++)if(font72[ch-32][j]&(1<<(5-i)))rect(x+i,y+j,1,1,c);}}
static U72 liveflies73(void){return total72(SESSION72,1)-(valid72(SESSION72->slot)?SESSION72->slot[0].flies:0)+dragonfly_count63(&hubflies73);}
static void hubhud73(Player18*p){int i=hub_near73(p);if(i<0)return;rect(5,195,310,40,0x30203c);hubtext73(10,198,portalname73[i],0xffffff);if(unlocked_count73(liveflies73(),i))hubtext73(10,211,"TRIANGLE: TRAVEL",0x91d8ad);else{hubtext73(10,211,"DRAGONFLIES NEEDED:",0xffce80);number(132,212,portals73[i].threshold);}}
static void hub_arrival73(Player18*p){U72 w=SESSION72->arrival;SESSION72->arrival=0;if(!w||w>8)return;const Portal73*q=portals73+w-1;if(!q->return_ready||!update18(q->rx,q->rz))return;int f=cache18_floor(&cache,q->rx,q->rz,q->ry,110);if(f==NONE18){reset18(p);return;}*p=(Player18){q->rx,f,q->rz,f,0,1,q->yaw,q->yaw,0};}
