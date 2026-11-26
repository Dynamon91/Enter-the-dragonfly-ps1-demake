/* Source-derived three-recovery dependency; 30 nominal updates/s. */
#include "questdata34.h"
#define Q34_REWARD 3
#define Q34_IDLE 0
#define Q34_MOVING 1
#define Q34_ARRIVED 2
#define Q34_RETURNED 3
typedef struct {int stage[3],timer[3],seen,near,event,reward;} Quest34;
static void quest_reset34(Quest34*q){for(int i=0;i<3;i++)q->stage[i]=q->timer[i]=0;q->seen=q->event=q->reward=0;q->near=-1;}
static void quest_pos34(const Quest34*q,int id,int*xyz){int n=qcount34[id]-1,t=q->timer[id],d=qduration34[id];if(t>=d){for(int k=0;k<3;k++)xyz[k]=qpoints34[id][n][k];return;}int p=t*n,seg=p/d,frac=p%d;for(int k=0;k<3;k++){int a=qpoints34[id][seg][k],b=qpoints34[id][seg+1][k];xyz[k]=a+(b-a)*frac/d;}}
static int quest_near34(const Cache18*c,int x,int y,int z,int gx,int gy,int gz,int r){if(abs18(x-gx)>r||abs18(z-gz)>r||abs18(y-gy)>200)return 0;int f=cache18_floor(c,gx,gz,gy,180);return f!=NONE18&&path20(c,x,y,z,gx,f,gz,r);}
static void quest_step34(Quest34*q,Progress33*p,const Cache18*c,int x,int y,int z,int grounded,int talk){q->event=0;q->near=-1;for(int i=0;i<3;i++)if(q->stage[i]==Q34_MOVING&&++q->timer[i]>=qduration34[i]){q->stage[i]=Q34_ARRIVED;q->timer[i]=qduration34[i];}
 if(!grounded)return;int best=1000000;
 for(int j=0;j<c->count;j++){int k=c->active[j];const U32*m=c->meta[k];const U8*t=c->bytes[k]+64+m[1]*36+m[2]*24;for(U32 n=0;n<m[3];n++,t+=16){if(s18(t+6)!=4)continue;U32 id=rd18(t+12);int gx=s18(t)+(int)m[4],gy=s18(t+2)+(int)m[5],gz=s18(t+4)+(int)m[6];for(int i=0;i<3;i++){
  if(id==qtrigger34[i]&&q->stage[i]==Q34_IDLE&&quest_near34(c,x,y,z,gx,gy,gz,300)){q->stage[i]=Q34_MOVING;q->timer[i]=0;q->event|=1;}
  if(id==qnpc34[i]&&quest_near34(c,x,y,z,gx,gy,gz,360)){int dx=x-gx,dz=z-gz,dist=dx*dx+dz*dz;if(dist<best){best=dist;q->near=i;}}
 }}}
 if(talk&&q->near>=0){int i=q->near;q->seen|=1<<i;q->event|=2;if(q->stage[i]==Q34_ARRIVED){q->stage[i]=Q34_RETURNED;q->event|=4;}if(q->stage[0]==3&&q->stage[1]==3&&q->stage[2]==3&&!q->reward){q->reward=1;if(progress_take33(p,Q34_REWARD))q->event|=8;}}
}
