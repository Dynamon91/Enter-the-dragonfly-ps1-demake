typedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;
#include "scene.h"
#include "world.h"
#include "player06.h"
#define A_WALK_THRESHOLD 90
#include "rig10.h"
void pose10(int frame,int *out){for(int i=0;i<NV;i++)skin_pose(frame,i,(s16)vertices[i][0],(s16)(vertices[i][0]>>16),(s16)vertices[i][1],out+3*i);}
void reset10(Anim*a){anim_reset(a);}
void step10(Anim*a,int moved,int btn,int was,int grounded,int vy,int analog){anim_step(a,moved,btn,was,grounded,vy,analog);}
void vertex10(const Anim*a,int i,int*out){skin_vertex(a,i,(s16)vertices[i][0],(s16)(vertices[i][0]>>16),(s16)vertices[i][1],out);}
