/* Source placement IDs; provisional stationary combat, not original AI. */
#include "enemyids29.h"
#define ENEMY29_COUNT 25
#define ENEMY29_CONTACT_COOLDOWN 45
static U8 enemy_dead29[ENEMY29_COUNT];
static int enemy_cool29;
static int enemy_id29(U32 id){for(int i=0;i<ENEMY29_COUNT;i++)if(enemyids29[i]==id)return i;return -1;}
static void enemy_reset29(void){for(int i=0;i<ENEMY29_COUNT;i++)enemy_dead29[i]=0;enemy_cool29=0;}
static void enemy_step29(Interact21*s,const Cache18*c,int x,int y,int z,int ox,int oz,int charge,int grounded){
 if(enemy_cool29)enemy_cool29--;
 for(int j=0;j<c->count;j++){int k=c->active[j];const U32*m=c->meta[k];const U8*t=c->bytes[k]+64+m[1]*36+m[2]*24;for(U32 n=0;n<m[3];n++,t+=16){if(s18(t+6)!=4)continue;int i=enemy_id29(rd18(t+12));if(i<0||enemy_dead29[i])continue;
 int gx=s18(t)+(int)m[4],gy=s18(t+2)+(int)m[5],gz=s18(t+4)+(int)m[6];if(abs18(x-gx)>1400||abs18(z-gz)>1400)continue;int r=enemylarge29[i]?150:115;
 int contact=path20(c,x,y,z,gx,gy,gz,r);int hit=0;
 if(!enemylarge29[i]&&grounded&&charge&&(x!=ox||z!=oz)&&contact)hit=1;
 if(!hit)for(int h=0;h<FIRE21;h++){Flame21*f=s->fire+h;if(f->life&&near21(f->x,f->y,f->z,gx,gy,gz,r)&&path20(c,f->x,f->y+135,f->z,gx,gy,gz,r)){f->life=0;hit=1;break;}}
 if(hit){enemy_dead29[i]=1;continue;}if(contact&&!enemy_cool29){damage21(s);enemy_cool29=ENEMY29_CONTACT_COOLDOWN;}
 }}
}
