/* Actual actor upload and draw code on host with memory CD, no GPU execution. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef unsigned char U8;typedef unsigned int U32,u32;typedef unsigned short u16;typedef signed short s16;
typedef struct {int x,y,z,ground,vy,grounded,heading,camera,prev;} Player18;
typedef struct {int x,y,z;u32 screen;int u,v;} Point;
typedef int (*Read18)(void*,U32,U32,U8*);
static U32 rd18(const U8*p){return p[0]|(U32)p[1]<<8|(U32)p[2]<<16|(U32)p[3]<<24;}
static int s18(const U8*p){return (short)(p[0]|p[1]<<8);}
static int ab(int x){return x<0?-x:x;}
#include "tex19.h"
static const s16 sine[64]={0,401,799,1189,1567,1931,2276,2598,2896,3166,3406,3612,3784,3920,4017,4076,4096,4076,4017,3920,3784,3612,3406,3166,2896,2598,2276,1931,1567,1189,799,401,0,-401,-799,-1189,-1567,-1931,-2276,-2598,-2896,-3166,-3406,-3612,-3784,-3920,-4017,-4076,-4096,-4076,-4017,-3920,-3784,-3612,-3406,-3166,-2896,-2598,-2276,-1931,-1567,-1189,-799,-401};
static U8 bank[43008],tbuf[6144];static U32 actor_extent59[2]={100,43008};static int uploads,read_fail=-1,triangles,seen[7];
static int cd17_read(void*c,U32 l,U32 n,U8*d){(void)c;if(l<100||l>=121||n!=3||(l-100)%3||(int)((l-100)/3)==read_fail)return 0;memcpy(d,bank+(l-100)*2048,6144);return 1;}
static void uploadtex19(void*c,int slot,const U8*p){(void)c;assert(slot==41+uploads);assert(!memcmp(p,bank+uploads*6144+24,4608));uploads++;}
static void idle(void){}
static Point transform(int x,int y,int z,int cx,int cy,int cz,int sn,int cs){(void)cx;(void)cy;(void)cz;(void)sn;(void)cs;Point p={x,y,z,0,0,0};return p;}
static void worldtri(Point a,Point b,Point c,int id){assert(id>=0x7000&&id<0x7007);assert(a.u>=0&&a.u<256&&b.v>=0&&b.v<256&&c.u>=0&&c.u<256);assert(ab(a.x)<200000&&ab(b.y)<200000&&ab(c.z)<200000);triangles++;seen[id-0x7000]++;}
#include "actors59.h"
int main(int argc,char**argv){assert(argc==2);FILE*f=fopen(argv[1],"rb");assert(f&&fread(bank,1,sizeof bank,f)==sizeof bank&&fgetc(f)==EOF);fclose(f);assert(TEXCAP19==41);assert(actor_upload59()&&uploads==7);int peak=0,total=0;for(unsigned i=0;i<sizeof actors59/sizeof actors59[0];i++){const ActorPlacement59*a=actors59+i;Player18 p={0};p.x=a->x;p.y=a->y;p.z=a->z;triangles=0;int expected=0;for(unsigned j=0;j<sizeof actors59/sizeof actors59[0];j++)if(actor_visible59(actors59+j,p.x,p.z))expected+=models59[actors59[j].model].nf;renderactors59(&p,0,0,0,0,4096);assert(triangles==expected&&triangles>0);if(peak<triangles)peak=triangles;total+=triangles;}for(int i=0;i<7;i++)assert(seen[i]>0);Player18 p={0};p.x=100000;p.z=100000;triangles=0;renderactors59(&p,0,0,0,0,4096);assert(!triangles);for(int i=0;i<7;i++){read_fail=i;uploads=0;assert(!actor_upload59()&&uploads==i&&!actor_ready59);p.x=actors59[0].x;p.z=actors59[0].z;triangles=0;renderactors59(&p,0,0,0,0,4096);assert(!triangles);}read_fail=-1;for(int i=0;i<7;i++){uploads=0;bank[i*6144+24]^=1;assert(!actor_upload59()&&uploads==i&&!actor_ready59);bank[i*6144+24]^=1;}uploads=0;assert(actor_upload59());printf("60 source positions verified; %d total submitted main-mesh triangles, peak %d at sampled positions; 7 CRC and 7 read failures rejected\n",total,peak);return 0;}
