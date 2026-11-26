/* Original positions and mesh; reconstructed hit and reward behavior. */
#include "basketdata14.h"
typedef struct {unsigned char state[BASKET_COUNT],age[BASKET_COUNT];int broken,pickups;} Baskets;
static void basket_reset(Baskets*b){for(int i=0;i<BASKET_COUNT;i++)b->state[i]=b->age[i]=0;b->broken=b->pickups=0;}
static int basket_overlap(int x,int y,int z,const s16*g,int r){return ab(x-g[0])<=r&&ab(z-g[2])<=r&&y>=g[1]-200&&y<=g[1]+30;}
static void basket_step(Baskets*b,Collect*c,Breath*fire,const Player*p,int oldx,int oldz,int btn){
 if(btn&PAD_START){basket_reset(b);return;}b->broken=b->pickups=0;
 for(int i=0;i<BASKET_COUNT;i++){const s16*g=basketpos[i];if(b->state[i]==0){int hit=0;
  if((btn&PAD_SQUARE)&&p->grounded&&(p->x!=oldx||p->z!=oldz)&&path_to_gem(p,g,170))for(int k=0;k<=4;k++){int x=oldx+(p->x-oldx)*k/4,z=oldz+(p->z-oldz)*k/4;if(basket_overlap(x,p->y-70,z,g,145)){hit=1;break;}}
  if(!hit)for(int j=0;j<FIRE_MAX;j++){Flame*f=fire->flame+j;if(f->life&&basket_overlap(f->x,f->y,f->z,g,92)){f->life=0;hit=1;break;}}
  if(hit){b->state[i]=1;b->age[i]=0;b->broken++;}continue;}
 if(b->state[i]==1){if(b->age[i]<10){b->age[i]++;continue;}if(path_to_gem(p,g,180)){b->state[i]=2;c->score+=g[3];b->pickups++;}}
 }
}
static int basket_mesh(const Baskets*b,const Collect*c,const Player*p,EffectTri*out){int n=0;for(int i=0;i<BASKET_COUNT;i++){const s16*g=basketpos[i];if(ab(p->x-g[0])>3400||ab(p->z-g[2])>3400)continue;if(!b->state[i])n+=add_collect(out+n,basketmesh,NFACE(basketmesh),g[0],g[1],g[2],0,4096);else if(b->state[i]==1)n+=add_collect(out+n,gemmesh1,NFACE(gemmesh1),g[0],g[1]-16-(10-b->age[i])*5,g[2],sine[c->tick&63],sine[(c->tick+16)&63]);}return n;}
_Static_assert(NFACE(gemmesh1)<=NFACE(basketmesh),"basket reward capacity");
