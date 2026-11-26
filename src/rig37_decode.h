#include "bitpack37.h"
/* Same two Q12 matrix caches and checkpoint interval as v0.36. */
typedef struct {s16 words[RIG_WORDS];int frame;} RigCache;
static RigCache rig_current={{0},-1},rig_previous={{0},-1};
static void rig_identity37(RigCache*c){for(int j=0;j<RIG_WORDS;j++){int k=j%12;c->words[j]=(k==0||k==5||k==10)?4096:0;}}
static void rig_seek(RigCache*c,int frame){
 if(c->frame==frame)return;
 if(frame<0||frame>=ANIM_FRAMES){rig_identity37(c);c->frame=-1;return;}
 int base=frame-frame%RIG_STRIDE;
 if(c->frame<base||c->frame>frame){rig_identity37(c);c->frame=base-1;}
 while(c->frame<frame){int f=c->frame+1;if(!decode37_s16(rig37_bits+rig37_off[f],rig37_bits+rig37_off[f+1],c->words,RIG_WORDS,1)){rig_identity37(c);c->frame=-1;return;}c->frame=f;}
}
static void rig_prepare(int frame,int from,int blend){
 if(blend<4&&rig_previous.frame!=from){if(rig_current.frame==from){for(int j=0;j<RIG_WORDS;j++)rig_previous.words[j]=rig_current.words[j];rig_previous.frame=from;}else rig_seek(&rig_previous,from);}
 rig_seek(&rig_current,frame);
}
