/* Diagnostic fire breath, not a recovered PS2 damage routine. Y points down. */
#define FIRE_MAX 24
#define FIRE_LIFE 13
#define FIRE_TARGETS 3
#define FIRE_MESH_MAX (FIRE_MAX*2+FIRE_TARGETS*4)
typedef struct {int x,y,z,vx,vy,vz,life;} Flame;
typedef struct {int x,y,z,hp;} FireTarget;
typedef struct {Flame flame[FIRE_MAX];FireTarget target[FIRE_TARGETS];int cooldown,tick,hits;} Breath;
static void breath_reset(Breath*b){
 for(int i=0;i<FIRE_MAX;i++)b->flame[i].life=0;
 for(int i=0;i<FIRE_TARGETS;i++){FireTarget*t=b->target+i;t->x=SPAWN_X+(i-1)*230;t->z=SPAWN_Z+480+(i==1?0:90);t->y=floor_at(t->x,t->z)-105;t->hp=2;}
 b->cooldown=b->tick=b->hits=0;
}
static void breath_step(Breath*b,const Player*p,int btn){
 if(btn&PAD_START){breath_reset(b);return;}
 b->tick=(b->tick+1)&255;if(b->cooldown)b->cooldown--;
 for(int i=0;i<FIRE_MAX;i++){
  Flame*f=b->flame+i;if(!f->life)continue;
  int oldx=f->x,oldz=f->z;f->x+=f->vx;f->y+=f->vy;f->z+=f->vz;
  int ground=floor_at(f->x,f->z),old=floor_at(oldx,oldz);
  if(ground==32767||old==32767||f->y>=ground||ab(ground-old)>110){f->life=0;continue;}
  for(int j=0;j<FIRE_TARGETS;j++){FireTarget*t=b->target+j;if(t->hp&&ab(f->x-t->x)<=80&&ab(f->z-t->z)<=80&&ab(f->y-t->y)<=90){t->hp--;b->hits++;f->life=0;break;}}
  if(f->life)f->life--;
 }
 if(!(btn&PAD_CIRCLE)||b->cooldown||!p->grounded)return;
 b->cooldown=3;
 int sn=sine[p->heading],cs=sine[(p->heading+16)&63];
 for(int k=0;k<3;k++)for(int i=0;i<FIRE_MAX;i++)if(!b->flame[i].life){
  Flame*f=b->flame+i;int side=(k-1)*8;f->x=p->x+(sn*100>>12);f->z=p->z+(cs*100>>12);f->y=p->y-135;f->vx=(sn*34+cs*side)>>12;f->vz=(cs*34-sn*side)>>12;f->vy=-1-(k==1);f->life=FIRE_LIFE;break;
 }
}
/* Shared camera-facing diamond geometry and BGR color. Four triangles per dummy,
 * two per flame. Diagnostics are intentionally distinct from original enemies. */
typedef struct {int x,y,z;} EffectVertex;
typedef struct {EffectVertex v[3];u32 color;} EffectTri;
static int breath_mesh(const Breath*b,int sn,int cs,EffectTri*out){
 int n=0;
 for(int i=0;i<FIRE_TARGETS+FIRE_MAX;i++){
  int x,y,z,r,h;u32 color;
  if(i<FIRE_TARGETS){const FireTarget*t=b->target+i;if(!t->hp)continue;x=t->x;y=t->y;z=t->z;r=52;h=100;color=t->hp==2?0x00b0a050:0x003050b0;}
  else{const Flame*f=b->flame+i-FIRE_TARGETS;if(!f->life)continue;x=f->x;y=f->y;z=f->z;r=13+(FIRE_LIFE-f->life)*3;h=r;color=f->life>8?0x0050dfff:f->life>4?0x001080ff:0x000030d0;}
  EffectVertex top={x,y-h,z},bottom={x,y+h,z},left={x-(cs*r>>12),y,z+(sn*r>>12)},right={x+(cs*r>>12),y,z-(sn*r>>12)},center={x,y,z};
  if(i<FIRE_TARGETS){out[n++]=(EffectTri){{top,left,center},color};out[n++]=(EffectTri){{top,center,right},color>>1&0x007f7f7f};out[n++]=(EffectTri){{bottom,left,center},color>>1&0x007f7f7f};out[n++]=(EffectTri){{bottom,center,right},color};}
  else{EffectVertex tl=left,tr=right,bl=left,br=right;tl.y-=h;tr.y-=h;bl.y+=h;br.y+=h;out[n++]=(EffectTri){{tl,bl,tr},0x01000000};out[n++]=(EffectTri){{br,bl,tr},0x02000000};}
 }
 return n;
}
