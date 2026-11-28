#ifndef ETD_QUEST_ANIM_H
#define ETD_QUEST_ANIM_H
#include <stdint.h>
typedef struct {uint16_t tick[2];uint16_t blend;} QuestAnim;
typedef struct {unsigned a,b,w;} QuestSample;
/* Two source-derived six-sample clips; caller supplies validated nonzero periods. */
static inline void qa_step(QuestAnim *a,const uint16_t period[2],int talking){
 for(unsigned i=0;i<2;i++){if(++a->tick[i]>=period[i])a->tick[i]=0;}
 if(talking){if(a->blend<256)a->blend+=32;}else if(a->blend)a->blend-=32;
}
static inline QuestSample qa_sample(unsigned tick,unsigned period,unsigned kind){
 unsigned p=(tick%period)*6u;unsigned j=p/period;return (QuestSample){kind*6u+j,kind*6u+(j+1u)%6u,(p%period)*256u/period};
}
static inline int qa_lerp(int a,int b,unsigned w){return a+(b-a)*(int)w/256;}
static inline int qa_component(const signed char *d,unsigned stride,unsigned off,QuestSample idle,QuestSample talk,unsigned blend){
 int a=qa_lerp(d[idle.a*stride+off],d[idle.b*stride+off],idle.w);
 if(!blend)return a;int b=qa_lerp(d[talk.a*stride+off],d[talk.b*stride+off],talk.w);return qa_lerp(a,b,blend);
}
#endif
