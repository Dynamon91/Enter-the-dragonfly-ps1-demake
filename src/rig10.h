/* Fixed-point CPU skinning: Q12 rotations, integer translation, Q8 weights. */
#include "rig.h"
enum {A_IDLE,A_WALK,A_RUN,A_CHARGE,A_JUMP_START,A_JUMP_CYCLE,A_JUMP_LAND,A_GLIDE,A_FIRE};
typedef struct {int clip,tick,frame,from,blend;} Anim;
static void anim_reset(Anim*a){a->clip=A_IDLE;a->tick=0;a->frame=0;a->from=0;a->blend=4;}
static void anim_step(Anim*a,int moved,int btn,int was_grounded,int grounded,int vy,int analog){
 int clip=a->clip;
 if(!grounded){if(vy>=0&&(btn&PAD_CROSS))clip=A_GLIDE;else if(was_grounded)clip=A_JUMP_START;else if(clip==A_JUMP_START&&a->tick+1<animclips[clip][1])clip=A_JUMP_START;else clip=A_JUMP_CYCLE;}
 else if(!was_grounded)clip=A_JUMP_LAND;
 else if(clip==A_JUMP_LAND&&a->tick+1<animclips[clip][1])clip=A_JUMP_LAND;
 else if(btn&PAD_CIRCLE)clip=A_FIRE;
 else if(moved)clip=(btn&PAD_SQUARE)?A_CHARGE:analog>A_WALK_THRESHOLD?A_RUN:A_WALK;
 else clip=A_IDLE;
 if(clip!=a->clip){a->from=a->frame;a->clip=clip;a->tick=0;a->blend=0;}
 else {a->tick++;if(a->tick>=animclips[clip][1])a->tick=0;if(a->blend<4)a->blend++;}
 a->frame=animclips[clip][0]+a->tick;
}
static void skin_pose(int frame,int i,int x,int y,int z,int*out){
 int acc[3]={0,0,0};
 for(int j=0;j<4;j++){int w=skinweights[i][j];if(!w)continue;const s16*m=bonemats[frame][skinbones[i][j]];
  for(int k=0;k<3;k++){const s16*r=m+4*k;int v=((r[0]*x+r[1]*y+r[2]*z+2048)>>12)+r[3];acc[k]+=v*w;}}
 for(int k=0;k<3;k++)out[k]=(acc[k]+128)>>8;
}
static void skin_vertex(const Anim*a,int i,int x,int y,int z,int*out){
 skin_pose(a->frame,i,x,y,z,out);if(a->blend<4){int old[3];skin_pose(a->from,i,x,y,z,old);for(int k=0;k<3;k++)out[k]=(old[k]*(4-a->blend)+out[k]*a->blend+2)>>2;}
}
