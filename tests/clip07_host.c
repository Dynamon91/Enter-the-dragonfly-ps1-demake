typedef unsigned int u32;
typedef struct {int x,y,z;u32 screen;int u,v;} Point;
#include "../src/frustum07.h"
int clip07(const int *a,int *o){Point p[3],r[CLIP_CAP];for(int i=0;i<3;i++){p[i]=(Point){a[5*i],a[5*i+1],a[5*i+2],0,a[5*i+3],a[5*i+4]};}int n=cliptriangle(p[0],p[1],p[2],r);for(int i=0;i<n;i++){o[5*i]=r[i].x;o[5*i+1]=r[i].y;o[5*i+2]=r[i].z;o[5*i+3]=r[i].u;o[5*i+4]=r[i].v;}return n;}
