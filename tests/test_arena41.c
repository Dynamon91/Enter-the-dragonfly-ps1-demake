#include <assert.h>
#include <stdio.h>
#include "arena41.h"
#include "draw41.h"
static int required(const Arena41*a){return a->id==0?FIRE40:a->id==1?ICE40:a->id==2?a->ripto.phase-1:a->id==3?ELECTRIC40:(a->bhp&1)?FIRE40:ELECTRIC40;}
static int bot(const Arena41*a){int x=a->bx-a->px,y=a->by-a->py,k=0;int open=a->state==A41_OPEN;
 if(a->breath!=required(a)&&!(a->prev&A41_CYCLE))k|=A41_CYCLE;
 for(int i=0;i<6;i++)if(a->shot[i].life&&near41(a->px,a->py,a->shot[i].x,a->shot[i].y,38)){Shot41 q=a->shot[i];if(abs41(q.vy)>=abs41(q.vx))return k|(a->px>=q.x?A41_RIGHT:A41_LEFT)|A41_CHARGE;return k|(a->py>=q.y?A41_DOWN:A41_UP)|A41_CHARGE;}
 if(!open){/* stay away during attacks, especially charges */
  if(a->id>=3&&a->state==A41_ATTACK){if(abs41(a->dx)>abs41(a->dy))k|=a->py>=a->by?A41_DOWN:A41_UP;else k|=a->px>=a->bx?A41_RIGHT:A41_LEFT;return k|A41_CHARGE;}
  if(a->id==0&&a->state==A41_ATTACK){int d=abs41(x)+abs41(y),r=(24-a->timer)*5;if(d<r+12&&d>r-18){k|=abs41(x)>abs41(y)?(x>0?A41_RIGHT:A41_LEFT):(y>0?A41_DOWN:A41_UP);return k|A41_CHARGE;}}
  if(a->id==1||a->id==2){for(int i=0;i<6;i++)if(a->shot[i].life&&near41(a->px,a->py,a->shot[i].x,a->shot[i].y,34)){return k|(a->px>=a->bx?A41_RIGHT:A41_LEFT)|A41_CHARGE;}}
  return k;}
 if(abs41(x)<24&&abs41(y)<25){k|=a->py<130?A41_UP:A41_DOWN;return k|A41_CHARGE;}
 if(abs41(x)>abs41(y)){if(abs41(y)>12)k|=y>0?A41_DOWN:A41_UP;else if(abs41(x)>65||a->face!=(x>0?1:3))k|=x>0?A41_RIGHT:A41_LEFT;}
 else{if(abs41(x)>12)k|=x>0?A41_RIGHT:A41_LEFT;else if(abs41(y)>65||a->face!=(y>0?2:0))k|=y>0?A41_DOWN:A41_UP;}
 if(!k&&a->breath==required(a))k|=A41_BREATH;return k;
}
static void combat(void){Arena41 a;int wins=0;for(int id=0;id<5;id++){arena_init41(&a,id,wins);int t;for(t=0;t<12000&&a.state<A41_WIN;t++)step41(&a,bot(&a));printf("boss %d: state=%d hp=%d ticks=%d bhp=%d phase=%d\n",id,a.state,a.hp,t,a.bhp,a.ripto.phase);assert(a.state==A41_WIN);wins=a.wins;}assert(wins==31);}
static void checks(void){Arena41 a;arena_init41(&a,0,0);for(int i=0;i<100;i++)step41(&a,A41_LEFT);assert(a.px==20);arena_init41(&a,0,0);a.state=A41_OPEN;a.timer=10;a.py=150;a.face=2;step41(&a,A41_BREATH);assert(a.bhp==3);a.cd=0;a.face=0;a.breath=ICE40;step41(&a,A41_BREATH);assert(a.bhp==3);a.cd=0;a.breath=FIRE40;step41(&a,A41_BREATH);assert(a.bhp==2);arena_init41(&a,1,0);a.px=a.bx;a.py=a.by;for(int i=0;i<45;i++)step41(&a,0);assert(a.hp==3);for(int i=0;i<150;i++)step41(&a,0);assert(a.state==A41_LOST&&a.wins==0);arena_init41(&a,1,1);assert(a.hp==4&&a.wins==1);}
static unsigned char image[240][320][3];
static void recthost(int x,int y,int w,int h,unsigned int c){for(int j=y;j<y+h;j++)for(int i=x;i<x+w;i++)if(i>=0&&i<320&&j>=0&&j<240){image[j][i][0]=c;image[j][i][1]=c>>8;image[j][i][2]=c>>16;}}
int main(int argc,char**argv){checks();combat();if(argc>1){Arena41 a;arena_init41(&a,1,1);for(int i=0;i<70;i++)step41(&a,bot(&a));draw41(&a,recthost);FILE*f=fopen(argv[1],"wb");assert(f);fputs("P6\n320 240\n255\n",f);fwrite(image,1,sizeof image,f);fclose(f);}puts("Arena scenarios passed");}
