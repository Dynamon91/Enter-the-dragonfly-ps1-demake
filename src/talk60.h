/* Source-derived conversation VM. Camera/sound cues deferred. Reward is pending,
 * not a fabricated dragonfly capture. World flags commit only at script end. */
#ifndef TALK60_H
#define TALK60_H
typedef struct {unsigned short op,a,b;} TalkOp60;
typedef struct {const TalkOp60 *ops;unsigned short n,name;} TalkScript60;
#include "talkdata60.h"
typedef struct {unsigned char flags[2][128],stage[2][128];int script,pc,line,speaker,condition,pending,rewards;unsigned char greeted[3];} Talk60;
static void reset60(Talk60*t){unsigned char*p=(unsigned char*)t;for(unsigned i=0;i<sizeof *t;i++)p[i]=0;t->script=-1;}
static int flag60(const unsigned char*f,int n){return !!(f[n/8]&(1u<<(n&7)));}
static void put60(unsigned char*f,int n,int on){if(on)f[n/8]|=1u<<(n&7);else f[n/8]&=~(1u<<(n&7));}
static void copyflags60(unsigned char d[2][128],unsigned char s[2][128]){for(int i=0;i<2;i++)for(int j=0;j<128;j++)d[i][j]=s[i][j];}
static int active60(const Talk60*t){return t->script>=0;}
static int advance60(Talk60*t){if(!active60(t))return 0;const TalkScript60*s=scripts60+t->script;t->line=0;
 for(int budget=0;budget<128;budget++){
  if(t->pc<0||t->pc>=s->n)break;TalkOp60 o=s->ops[t->pc++];
  switch(o.op){case 0:copyflags60(t->flags,t->stage);t->rewards+=t->pending;t->greeted[t->script/2]=1;t->script=-1;t->pending=0;return 0;
   case 1:case 2:case 3:t->line=o.a;t->speaker=o.op;return 1;
   case 4:case 5:case 6:if(o.a>=1024||(o.b!=2&&o.b!=9))goto bad;{unsigned char*f=t->stage[o.b==9];if(o.op==6)t->condition&=flag60(f,o.a);else put60(f,o.a,o.op==4);}break;
   case 7:t->pc=t->condition?o.b:o.a;break;case 8:if(o.a!=1||t->pending)goto bad;t->pending=1;break;case 9:t->condition=1;break;default:goto bad;}
 }bad:t->script=-1;t->line=0;t->pending=0;return 0;
}
static int begin60(Talk60*t,int actor){if(active60(t)||actor<0||actor>=3)return 0;copyflags60(t->stage,t->flags);t->script=actor*2+!!t->greeted[actor];t->pc=0;t->pending=0;t->condition=1;return advance60(t);}
#endif
