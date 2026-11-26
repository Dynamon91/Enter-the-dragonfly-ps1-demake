typedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;
#include "scene.h"
#include "world.h"
#include "player06.h"
#define A_WALK_THRESHOLD 90
#include "rig11.h"
#include "breath11.h"
void matrix11(int frame,s16*out){rig_seek(&rig_current,frame);for(int i=0;i<RIG_WORDS;i++)out[i]=rig_current.words[i];}
void pose11(int frame,int from,int blend,int*out){Anim a={0,0,frame,from,blend};rig_prepare(frame,from,blend);for(int i=0;i<NV;i++)skin_vertex(&a,i,(s16)vertices[i][0],(s16)(vertices[i][0]>>16),(s16)vertices[i][1],out+3*i);}
static Player p;static Breath b;
void fire_reset11(void){reset_player(&p);breath_reset(&b);}
void fire_position11(int x,int y,int z,int heading,int grounded){p.x=x;p.y=y;p.z=z;p.heading=heading;p.grounded=grounded;}
void fire_step11(int btn){breath_step(&b,&p,btn);}
void fire_status11(int*out){out[0]=b.hits;out[1]=0;for(int i=0;i<FIRE_MAX;i++)out[1]+=b.flame[i].life!=0;for(int i=0;i<FIRE_TARGETS;i++){out[2+i]=b.target[i].hp;out[5+i]=floor_at(b.target[i].x,b.target[i].z);}}
int fire_mesh11(int sn,int cs,EffectTri*out){return breath_mesh(&b,sn,cs,out);}
