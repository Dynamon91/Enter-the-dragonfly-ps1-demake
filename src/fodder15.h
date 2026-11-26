/* Diagnostic fodder encounter, with original geometry and reconstructed health logic.
 * No source sheep locations lie in this sector. L2/R2 are development controls. */
#include "fodderdata15.h"
#define PAD_L2 256
#define PAD_R2 512
#define SHEEP_X (SPAWN_X)
#define SHEEP_Z (SPAWN_Z+380)
typedef struct {int state,health,x,y,z,heading,tick,age,bx,by,bz,hit,healed,prev;} Fodder;
static void fodder_reset(Fodder*f){f->state=0;f->health=3;f->x=SHEEP_X;f->z=SHEEP_Z;f->y=floor_at(f->x,f->z);f->heading=32;f->tick=f->age=f->hit=f->healed=f->prev=0;f->bx=f->by=f->bz=0;}
static int fodder_near(int x,int y,int z,const Fodder*f,int r){int dx=x-f->x,dz=z-f->z;return ab(dx)<=r&&ab(dz)<=r&&dx*dx+dz*dz<=r*r&&y>=f->y-190&&y<=f->y+25;}
static void fodder_step(Fodder*f,Collect*c,Breath*b,const Player*p,int oldx,int oldz,int btn){
 if(btn&PAD_START){fodder_reset(f);return;}int pressed=btn&~f->prev;f->prev=btn;f->hit=f->healed=0;f->tick=(f->tick+1)&255;
 if(pressed&PAD_L2){if(f->health>0)f->health--;}
 if(pressed&PAD_R2){if(f->state)f->state=0;else if(f->y!=32767){f->state=1;f->age=0;}}
 if(f->state==1){int hit=0;s16 pos[3]={(s16)f->x,(s16)f->y,(s16)f->z};
  if((btn&PAD_SQUARE)&&p->grounded&&(p->x!=oldx||p->z!=oldz)&&path_to_gem(p,pos,180))for(int k=0;k<=4;k++){int x=oldx+(p->x-oldx)*k/4,z=oldz+(p->z-oldz)*k/4;if(fodder_near(x,p->y-70,z,f,115)){hit=1;break;}}
  if(!hit)for(int j=0;j<FIRE_MAX;j++){Flame*a=b->flame+j;if(a->life&&fodder_near(a->x,a->y,a->z,f,100)){a->life=0;hit=1;break;}}
  if(hit){f->state=2;f->age=0;f->bx=f->x;f->by=f->y-150;f->bz=f->z;f->hit=1;}return;
 }
 if(f->state==2){if(++f->age>=180){f->state=3;return;}if(f->age<10)return;
  s16 pos[3]={(s16)f->x,(s16)f->y,(s16)f->z};if(!path_to_gem(p,pos,520))return;
  int x=f->health?c->sx:p->x,y=f->health?c->sy:p->y-100,z=f->health?c->sz:p->z;
  f->bx+=(x-f->bx)/5;f->by+=(y-f->by)/5;f->bz+=(z-f->bz)/5;
  if(ab(x-f->bx)<=24&&ab(y-f->by)<=24&&ab(z-f->bz)<=24){f->state=3;if(f->health<3){f->health++;f->healed=1;}}
 }
}
static int fodder_mesh(const Fodder*f,EffectTri*out){if(f->state==1)return add_collect(out,sheepmesh,NFACE(sheepmesh),f->x,f->y,f->z,sine[f->heading],sine[(f->heading+16)&63]);if(f->state!=2)return 0;
 int n=add_collect(out,buttermesh,NFACE(buttermesh),f->bx,f->by,f->bz,0,4096);/* last four faces are original wing planes; flap around local Z */
 int a=sine[(f->tick*8)&63]*3/4,cs=sine[(((f->tick*8)&63)+16)&63];if(cs<0)cs=-cs;for(int i=n-4;i<n;i++)for(int j=0;j<3;j++){EffectVertex*v=&out[i].v[j];int x=v->x-f->bx;v->x=f->bx+(x*cs>>12);v->y=f->by-(ab(x)*a>>12);}return n;
}
