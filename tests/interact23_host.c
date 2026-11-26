#include "../src/cache23.c"
#include "../src/collect21.h"
#include "../src/interact21.h"
static const short sn[64]={0,401,799,1189,1567,1931,2276,2598,2896,3166,3406,3612,3784,3920,4017,4076,4096,4076,4017,3920,3784,3612,3406,3166,2896,2598,2276,1931,1567,1189,799,401,0,-401,-799,-1189,-1567,-1931,-2276,-2598,-2896,-3166,-3406,-3612,-3784,-3920,-4017,-4076,-4096,-4076,-4017,-3920,-3784,-3612,-3406,-3166,-2896,-2598,-2276,-1931,-1567,-1189,-799,-401};
void reset21(Interact21*s){interreset21(s);}
int id21(U32 id,int kind){return objectid21(id,kind);}
void hurt21(Interact21*s){damage21(s);}
void step21(Interact21*s,const Cache18*c,int x,int y,int z,int ox,int oz,int heading,int charge,int firing,int grounded,int sx,int sy,int sz){interstep21(s,c,x,y,z,ox,oz,heading,charge,firing,grounded,sx,sy,sz,sn);}
void greset21(Collect20*s,int x,int y,int z){collectreset20(s,x,y,z);}
void gstep21(Collect20*s,const Cache18*c,int x,int y,int z,int heading,int hp){collectstep21(s,c,x,y,z,heading,sn,hp);}

/* Opaque cache access for host tests; no pointer-size-dependent Python ABI. */
U32 cache22_size(void){return sizeof(Cache18);}
int cache22_count(Cache18*c){return c->count;}
int cache22_id(Cache18*c,int i){return i>=0&&i<c->count?c->ids[c->active[i]]:-1;}
U32 cache22_bytes(Cache18*c){return c->used_bytes;}
U32 cache22_copied(Cache18*c){return c->copied_bytes;}
int cache22_reads(Cache18*c){return c->reads;}
const U8* cache22_data(Cache18*c,int i){return i>=0&&i<c->count?c->bytes[c->active[i]]:0;}

int cache23_pending(Cache18*c){return c->plan_valid?c->plan_count-c->plan_done:-1;}
U32 cache23_ticks(Cache18*c){return c->ticks;}
U32 cache23_cancels(Cache18*c){return c->cancels;}
