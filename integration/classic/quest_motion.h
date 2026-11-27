#ifndef ETD_QUEST_MOTION_H
#define ETD_QUEST_MOTION_H
#include "quest_motion_data.h"
#include "kite_vm.h"
/* Regenerate quest_motion_data.h from the local PS2 source. */
typedef struct {uint16_t tick[3];uint8_t stage[3];} QuestMotion;
enum {QM_WAIT,QM_MOVE,QM_ARRIVED};
static inline int qm_near(int x,int y,int z,unsigned i){
 if(i>=3)return 0;const int32_t *q=quest_trigger[i];
 if(x<q[0]-300||x>q[0]+300||y<q[1]-220||y>q[1]+220||z<q[2]-300||z>q[2]+300)return 0;
 int dx=x-q[0],dz=z-q[2];return dx*dx+dz*dz<=90000;
}
static inline void qm_pos(const QuestMotion*m,unsigned i,int out[3]){
 unsigned n=quest_count[i]-1,t=m->tick[i],d=quest_duration[i];
 if(t>=d){for(unsigned k=0;k<3;k++)out[k]=quest_points[i][n][k];return;}
 unsigned j=t*n/d;int rem=(int)(t*n%d);for(unsigned k=0;k<3;k++){int a=quest_points[i][j][k],b=quest_points[i][j+1][k];out[k]=a+(b-a)*rem/(int)d;}
}
static inline unsigned qm_step(QuestMotion*m,KiteVm*v,unsigned mask){
 unsigned events=0;if(v->active)return 0;
 for(unsigned i=0;i<3;i++){
  if(m->stage[i]==QM_WAIT&&(mask&(1u<<i))){m->stage[i]=QM_MOVE;m->tick[i]=0;events|=1u<<i;}
  else if(m->stage[i]==QM_MOVE&&++m->tick[i]>=quest_duration[i]){m->stage[i]=QM_ARRIVED;m->tick[i]=quest_duration[i];kite_arrive(v,i);events|=8u<<i;}
 }
 return events;
}
#endif
