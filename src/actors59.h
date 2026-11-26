/* Original static main meshes; reserve terrain slots 41..47 exclusively. */
#include "actorsdata59.h"
#define ACTOR_ID59 0x7000
#define ACTOR_SLOT59 41
static int actor_ready59;
static int actor_upload59(void){
 actor_ready59=0;
 for(int i=0;i<7;i++){
  if(!cd17_read(0,actor_extent59[0]+3*i,3,tbuf)||rd18(tbuf)!=0x54445445u||s18(tbuf+4)!=1||s18(tbuf+6)!=i||rd18(tbuf+8)==0||rd18(tbuf+8)>1024||rd18(tbuf+12)==0||rd18(tbuf+12)>1024||rd18(tbuf+16)!=4608||rd18(tbuf+20)!=models59[i].crc||texcrc19(tbuf+24,4608)!=models59[i].crc)return 0;
  uploadtex19(0,ACTOR_SLOT59+i,tbuf+24);
 }
 idle();actor_ready59=1;return 1;
}
static int actor_visible59(const ActorPlacement59*a,int x,int z){int radius=a->model==6?3000:1536;return ab(a->x-x)<=radius&&ab(a->z-z)<=radius;}
static void renderactors59(Player18*p,int cx,int cy,int cz,int sn,int cs){
 if(!actor_ready59)return;
 for(unsigned i=0;i<sizeof actors59/sizeof actors59[0];i++){
  const ActorPlacement59*a=actors59+i;if(!actor_visible59(a,p->x,p->z))continue;
  const ActorModel59*m=models59+a->model;int as=sine[a->yaw],ac=sine[(a->yaw+16)&63];
  for(int f=0;f<m->nf;f++){Point q[3];const ActorFace59*t=m->f+f;
   for(int j=0;j<3;j++){const s16*v=m->v[t->ix[j]];q[j]=transform(a->x+((ac*v[0]+as*v[2])>>12),a->y+v[1],a->z+((ac*v[2]-as*v[0])>>12),cx,cy,cz,sn,cs);q[j].u=t->uv[j*2];q[j].v=t->uv[j*2+1];}
   worldtri(q[0],q[1],q[2],ACTOR_ID59+a->model);
  }
 }
}
