#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "talk60.h"
static void expect(Talk60*t,int actor,const int*ids,int n,int reward){int before=t->rewards;assert(begin60(t,actor));for(int i=0;i<n;i++){assert(active60(t)&&t->line==ids[i]);assert(*talktext60(t->line));assert(t->rewards==before);advance60(t);}assert(!active60(t)&&t->rewards==before+reward&&!flag60(t->flags[1],905));}
#define RUN(actor,reward,...) do{const int ids[]={__VA_ARGS__};expect(&t,actor,ids,sizeof ids/sizeof ids[0],reward);}while(0)
int main(void){Talk60 t;reset60(&t);RUN(0,0,4101,4102,4103);assert(flag60(t.flags[0],20));RUN(0,0,4104,4105);RUN(1,0,4116);RUN(1,0,4117);RUN(2,0,4120);RUN(2,0,4121);assert(!t.rewards);
 put60(t.flags[0],0,1);RUN(0,0,4161,4162,4163);assert(flag60(t.flags[0],21));RUN(0,0,4106,4107);RUN(1,1,4110,4111,4112,4113,4115);assert(flag60(t.flags[0],206));RUN(1,0,4110);RUN(2,0,4122);RUN(2,0,4123);for(int i=8;i<=12;i++)put60(t.flags[0],i,1);RUN(2,1,4124);assert(flag60(t.flags[0],204));RUN(2,0,4125);assert(t.rewards==2);put60(t.flags[0],6,1);RUN(0,0,4119);
 /* All combinations of relevant source flags, both grab/wait forms. */
 int flags[]={0,6,8,9,10,11,12,21,22,204,206};int cases=0;
 for(int m=0;m<(1<<11);m++)for(int a=0;a<3;a++)for(int wait=0;wait<2;wait++){
  reset60(&t);for(int i=0;i<11;i++)put60(t.flags[0],flags[i],!!(m&(1<<i)));t.greeted[a]=wait;int first=0,reward=0;
  if(a==0)first=(m&2)?4119:!(m&1)?(wait?4104:4101):(m&(1<<7))?4106:4161;
  if(a==1){if(wait&&(m&(1<<10)))first=4110;else if(!(m&1))first=wait?4117:4116;else first=4110,reward=1;}
  if(a==2){if((m&124)==124){first=wait&&(m&(1<<9))?4125:4124;reward=first==4124;}else if(!(m&1))first=wait?4121:4120;else first=wait&&(m&(1<<8))?4123:4122;}
  assert(begin60(&t,a)&&t.line==first);int n=0;while(active60(&t)){assert(++n<=6);advance60(&t);}assert(t.rewards==reward&&!flag60(t.flags[1],905));cases++;
 }
 printf("%d source branch combinations; sequential quest flags and reward checks passed\n",cases);return 0;}
