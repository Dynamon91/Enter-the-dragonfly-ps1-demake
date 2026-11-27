#ifndef FLIGHT75_H
#define FLIGHT75_H
#include "routesdata75.h"
/* Source locator order; linear interpolation, looping and speed scale reconstructed. */
typedef struct {int p[3],next,active;} Flight75;
static Flight75 flight75[DF_COUNT63];
static int absflight75(int n){return n<0?-n:n;}
static void flight_init75(Flight75*f,int i){f->p[0]=dfplace63[i].x;f->p[1]=dfplace63[i].y;f->p[2]=dfplace63[i].z;f->next=routes75[i][2];f->active=1;}
static int flight_move75(Flight75*f,int i){const int*r=routes75[i];if(!r[1])return 0;if(!f->active)flight_init75(f,i);const int*p=routepoints75[r[0]+f->next];int d[3],max=0;for(int j=0;j<3;j++){d[j]=p[j]-f->p[j];int a=absflight75(d[j]);if(a>max)max=a;}if(max<=r[3]){for(int j=0;j<3;j++)f->p[j]=p[j];f->next++;if(f->next==r[1])f->next=0;return 1;}for(int j=0;j<3;j++)f->p[j]+=d[j]*r[3]/max;return 0;}
static void flight_pos75(int i,int*p){Flight75*f=flight75+i;if(f->active){for(int j=0;j<3;j++)p[j]=f->p[j];}else{p[0]=dfplace63[i].x;p[1]=dfplace63[i].y;p[2]=dfplace63[i].z;}}
static void flight_tick75(int i,int x,int z){int p[3];flight_pos75(i,p);const int*r=routes75[i];if(r[1]&&absflight75(x-p[0])<=r[4]&&absflight75(z-p[2])<=r[4])flight_move75(flight75+i,i);}
static void flight_reset75(void){for(int i=0;i<DF_COUNT63;i++)flight75[i].active=0;}
#endif
