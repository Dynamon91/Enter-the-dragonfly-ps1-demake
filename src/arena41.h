#ifndef ARENA41_H
#define ARENA41_H
#include "combat40.h"
/* Original fan-designed collision lab; coordinates in arena units, 30 ticks/s. */
enum { A41_LEFT=1,A41_RIGHT=2,A41_UP=4,A41_DOWN=8,A41_BREATH=16,A41_CHARGE=32,A41_CYCLE=64 };
enum { A41_WIND,A41_ATTACK,A41_OPEN,A41_WIN,A41_LOST };
typedef struct { int x,y,vx,vy,life; } Shot41;
typedef struct { int id,px,py,bx,by,dx,dy,face,breath,hp,bhp,state,timer,inv,cd,prev,wins; Shot41 shot[6]; Ripto40 ripto; } Arena41;
static int abs41(int n){return n<0?-n:n;}
static int clamp41(int n,int lo,int hi){return n<lo?lo:n>hi?hi:n;}
static int near41(int x,int y,int bx,int by,int r){int dx=x-bx,dy=y-by;return dx*dx+dy*dy<=r*r;}
static void arena_init41(Arena41*a,int id,int wins){*a=(Arena41){0};a->id=clamp41(id,0,4);a->wins=wins&31;a->px=160;a->py=182;a->bx=160;a->by=76;a->face=0;a->hp=4;a->bhp=a->id==4?5:3+a->id;a->state=A41_WIND;a->timer=36;if(a->id==2)ripto_start40(&a->ripto,100,1);}
static void hurt41(Arena41*a){if(!a->inv&&a->hp){a->hp--;a->inv=45;if(!a->hp)a->state=A41_LOST;}}
static void win41(Arena41*a){a->wins|=1<<a->id;a->state=A41_WIN;}
static void spawn41(Arena41*a){for(int i=0;i<6;i++)if(!a->shot[i].life){int x=a->px-a->bx,y=a->py-a->by,d=abs41(x)>abs41(y)?abs41(x):abs41(y);if(d<1)d=1;a->shot[i]=(Shot41){a->bx,a->by,x*5/d,y*5/d,60};return;}}
static void step41(Arena41*a,int keys){
 if(a->state>=A41_WIN)return;
 int edge=keys&~a->prev;a->prev=keys;if(a->inv)a->inv--;if(a->cd)a->cd--;if(edge&A41_CYCLE)a->breath=(a->breath+1)%3;
 int dx=!!(keys&A41_RIGHT)-!!(keys&A41_LEFT),dy=!!(keys&A41_DOWN)-!!(keys&A41_UP),speed=(keys&A41_CHARGE)?5:3;
 if(dx||dy)a->face=abs41(dx)>abs41(dy)?(dx>0?1:3):(dy>0?2:0);
 a->px=clamp41(a->px+dx*speed,20,300);a->py=clamp41(a->py+dy*speed,44,204);
 if(a->id==2){ripto_tick40(&a->ripto);a->state=a->ripto.state==EXPOSE40?A41_OPEN:A41_WIND;a->timer=a->ripto.timer;if(a->state==A41_WIND&&a->timer%15==0)spawn41(a);}
 else if(!--a->timer){if(a->state==A41_WIND){a->state=A41_ATTACK;a->timer=24;int x=a->px-a->bx,y=a->py-a->by,d=abs41(x)>abs41(y)?abs41(x):abs41(y);if(d<1)d=1;a->dx=x*(a->id==4?4:6)/d;a->dy=y*(a->id==4?4:6)/d;}else if(a->state==A41_ATTACK){a->state=A41_OPEN;a->timer=48;}else{a->state=A41_WIND;a->timer=36;}}
 if(a->state==A41_ATTACK){if(a->id==0){int r=(24-a->timer)*5;if(abs41(abs41(a->px-a->bx)+abs41(a->py-a->by)-r)<9)hurt41(a);}else if(a->id==1){if(a->timer%8==0)spawn41(a);}else{a->bx=clamp41(a->bx+a->dx,32,288);a->by=clamp41(a->by+a->dy,56,190);if(a->id==4&&a->timer==24)spawn41(a);}}
 if(near41(a->px,a->py,a->bx,a->by,16))hurt41(a);
 for(int i=0;i<6;i++){Shot41*s=a->shot+i;if(!s->life)continue;s->x+=s->vx;s->y+=s->vy;s->life--;if(s->x<16||s->x>304||s->y<40||s->y>208)s->life=0;else if(near41(a->px,a->py,s->x,s->y,9)){hurt41(a);s->life=0;}}
 if(a->state==A41_LOST)return;
 if((keys&A41_BREATH)&&!a->cd){a->cd=12;int x=a->bx-a->px,y=a->by-a->py;int along=a->face==0?-y:a->face==1?x:a->face==2?y:-x;int cross=(a->face&1)?y:x;if(a->state==A41_OPEN&&along>0&&along<=82&&abs41(cross)<=18){if(a->id==2){ripto_hit40(&a->ripto,a->breath,1);if(ripto_full40(&a->ripto))win41(a);}else if(a->breath==(a->id==0?FIRE40:a->id==1?ICE40:a->id==3?ELECTRIC40:(a->bhp&1)?FIRE40:ELECTRIC40)){if(!--a->bhp)win41(a);else{a->state=A41_WIND;a->timer=36;}}}}
}
#endif
