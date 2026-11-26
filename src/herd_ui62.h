#include "herd62.h"
static Herd62 herd62;
static int herd_floor62(void*ctx,int x,int z,int y){return cache18_floor((const Cache18*)ctx,x,z,y,70);}
static void herd_step62(Player18*p,int ox,int oz,int charge){if(!flag60(talk60.flags[0],7)||active60(&talk60))return;
 for(int i=0;i<5;i++){HerdCow62*c=herd62.cow+i;if(c->state||!p->grounded||!close61(p->x,p->z,c->x,c->z,900))continue;
 int hit=0;if(charge&&(ox!=p->x||oz!=p->z)&&path20(&cache,p->x,p->ground,p->z,c->x,c->y,c->z,190))for(int j=0;j<=4;j++)if(near21(ox+(p->x-ox)*j/4,p->y-70,oz+(p->z-oz)*j/4,c->x,c->y,c->z,165)){hit=1;break;}
 if(!hit)for(int j=0;j<FIRE21;j++){Flame21*f=interactions.fire+j;if(f->life&&near21(f->x,f->y,f->z,c->x,c->y,c->z,130)&&path20(&cache,p->x,p->ground,p->z,c->x,c->y,c->z,900)){f->life=0;hit=1;break;}}
 if(hit&&herd_hit62(&herd62,&talk60,i))sfx_play(2);
 }herd_tick62(&herd62,&talk60,p->x,p->z,herd_floor62,&cache);
}
static void herd_draw62(Player18*p,int cx,int cy,int cz,int sn,int cs){if(!flag60(talk60.flags[0],7))return;for(int i=0;i<5;i++){HerdCow62*c=herd62.cow+i;if(ab(c->x-p->x)>1536||ab(c->z-p->z)>1536)continue;const ActorModel59*m=models59;int as=sine[c->yaw],ac=sine[(c->yaw+16)&63];for(int f=0;f<m->nf;f++){Point q[3];const ActorFace59*t=m->f+f;for(int j=0;j<3;j++){const s16*v=m->v[t->ix[j]];q[j]=transform(c->x+((ac*v[0]+as*v[2])>>12),c->y+v[1],c->z+((ac*v[2]-as*v[0])>>12),cx,cy,cz,sn,cs);q[j].u=t->uv[j*2];q[j].v=t->uv[j*2+1];}worldtri(q[0],q[1],q[2],ACTOR_ID59);}}}
static void herd_hud62(Player18*p){if(active60(&talk60)||!flag60(talk60.flags[0],7)||!close61(p->x,p->z,14394,-5061,6500))return;int n=0;for(int i=0;i<5;i++)n+=flag60(talk60.flags[0],8+i);rect(5,197,205,13,0x201c28);if(n==5)text60(10,198,"ALL COWS HERDED - TALK TO DEAN",0xffffff);else{text60(10,198,"HERDED COWS",0xffffff);glyph60(88,198,'0'+n,0xffffff);text60(94,198,"/5",0xffffff);}}
