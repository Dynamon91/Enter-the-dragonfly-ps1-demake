/* Exact signed-16 matrix checkpoint/delta decoder. Two fixed-size caches. */
typedef struct {s16 words[RIG_WORDS];int frame;} RigCache;
static RigCache rig_current={{0},-1},rig_previous={{0},-1};
static s16 rig_read16(const unsigned char **p){unsigned v=(*p)[0]|((unsigned)(*p)[1]<<8);*p+=2;return (s16)v;}
static void rig_seek(RigCache*c,int frame){
 if(c->frame==frame)return;
 int base=frame-frame%RIG_STRIDE;
 if(c->frame<base||c->frame>frame){const unsigned char*p=rig_stream+rig_offsets[base];for(int j=0;j<RIG_WORDS;j++)c->words[j]=rig_read16(&p);c->frame=base;}
 while(c->frame<frame){const unsigned char*p=rig_stream+rig_offsets[++c->frame];int j=0;while(j<RIG_WORDS){unsigned t=*p++;if(t==0x80){c->words[j++]=rig_read16(&p);}else if(t==0x81){j+=*p++;}else{int d=t>=128?(int)t-256:(int)t;c->words[j]=(s16)(c->words[j]+d);j++;}}}
}
static void rig_prepare(int frame,int from,int blend){
 if(blend<4&&rig_previous.frame!=from){if(rig_current.frame==from){for(int j=0;j<RIG_WORDS;j++)rig_previous.words[j]=rig_current.words[j];rig_previous.frame=from;}else rig_seek(&rig_previous,from);}
 rig_seek(&rig_current,frame);
}
