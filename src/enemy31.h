/* Reconstructed AI, source poses. Persistent state keyed by original placement ID. */
#include "enemyids29.h"
#define ENEMY29_COUNT 25
#define N_IDLE31 0
#define N_READY31 1
#define N_JUMP31 2
#define N_RECOVER31 3
#define N_DIE31 4
#define N_GONE31 5
typedef struct {int x,y,z,hx,hy,hz;int tx,tz;U8 initialized,mode,timer,heading;} Ninja31;
static Ninja31 ninjas31[ENEMY29_COUNT];
static int enemy_cool31;
static int enemy_id29(U32 id){for(int i=0;i<ENEMY29_COUNT;i++)if(enemyids29[i]==id)return i;return -1;}
static void enemy_reset31(void){for(unsigned i=0;i<sizeof(ninjas31);i++)((volatile U8*)ninjas31)[i]=0;enemy_cool31=0;}
static int heading31(int dx,int dz,const short*sn){int best=-2147483647,heading=0;for(int q=0;q<64;q++){int d=dx*sn[q]+dz*sn[(q+16)&63];if(d>best){best=d;heading=q;}}return heading;}
static int lift31(const Ninja31*n){return n->mode==N_JUMP31? (int)n->timer*(34-n->timer)*80/289:0;}
static int phase31(const Ninja31*n,int tick){switch(n->mode){case N_READY31:return 13+n->timer*6/18;case N_JUMP31:return 19+n->timer*8/34;case N_RECOVER31:return 13+(n->timer%12)*6/12;case N_DIE31:return 27+n->timer*8/60;default:return 1+(tick%80)*12/80;}}
static int move31(Ninja31*n,const Cache18*c,int nx,int nz){if(abs18(nx-n->hx)>460||abs18(nz-n->hz)>460)return 0;int f=cache18_floor(c,nx,nz,n->y,45);if(f==NONE18||!path20(c,n->x,n->y,n->z,nx,f,nz,40))return 0;n->x=nx;n->y=f;n->z=nz;return 1;}
static void enemy_step31(Interact21*s,const Cache18*c,int x,int y,int z,int ox,int oz,int charge,int grounded,const short*sn){
 if(enemy_cool31)enemy_cool31--;
 for(int i=0;i<ENEMY29_COUNT;i++){Ninja31*n=ninjas31+i;if(n->mode==N_DIE31&&++n->timer>=60){n->mode=N_GONE31;n->timer=0;}}
 for(int j=0;j<c->count;j++){int k=c->active[j];const U32*m=c->meta[k];const U8*t=c->bytes[k]+64+m[1]*36+m[2]*24;for(U32 o=0;o<m[3];o++,t+=16){if(s18(t+6)!=4)continue;int i=enemy_id29(rd18(t+12));if(i<0)continue;Ninja31*n=ninjas31+i;if(n->mode>=N_DIE31)continue;
 int gx=s18(t)+(int)m[4],gy=s18(t+2)+(int)m[5],gz=s18(t+4)+(int)m[6];if(abs18(x-gx)>1600||abs18(z-gz)>1600)continue;
 if(!n->initialized){int f=cache18_floor(c,gx,gz,gy,110);if(f==NONE18)continue;*n=(Ninja31){gx,f,gz,gx,f,gz,0,0,1,0,0,0};}
 int dx=x-n->x,dz=z-n->z,r=enemylarge29[i]?150:115;
 int contact=path20(c,x,y,z,n->x,n->y,n->z,r);int hit=0;
 if(!enemylarge29[i]&&grounded&&charge&&(x!=ox||z!=oz)&&contact&&lift31(n)<35)hit=1;
 if(!hit)for(int h=0;h<FIRE21;h++){Flame21*f=s->fire+h;if(f->life&&near21(f->x,f->y,f->z,n->x,n->y-lift31(n),n->z,r)&&path20(c,f->x,f->y+135+lift31(n),f->z,n->x,n->y,n->z,r)){f->life=0;hit=1;break;}}
 if(hit){n->mode=N_DIE31;n->timer=0;continue;}
 int nearby=abs18(dx)<580&&abs18(dz)<580&&path20(c,n->x,n->y,n->z,x,y,z,580);
 if(n->mode==N_IDLE31){if(nearby){n->mode=N_READY31;n->timer=0;n->heading=heading31(dx,dz,sn);}else if(n->x!=n->hx||n->z!=n->hz){int a=n->hx-n->x,b=n->hz-n->z;n->heading=heading31(a,b,sn);int mx=abs18(a)>10?(a>0?10:-10):a,mz=abs18(b)>10?(b>0?10:-10):b;move31(n,c,n->x+mx,n->z+mz);}}
 else if(n->mode==N_READY31){if(!nearby){n->mode=N_IDLE31;n->timer=0;}else{n->heading=heading31(dx,dz,sn);if(++n->timer>=18){int a=sn[n->heading],b=sn[(n->heading+16)&63];n->tx=a;n->tz=b;n->mode=N_JUMP31;n->timer=0;}}}
 else if(n->mode==N_JUMP31){if(++n->timer>=34){n->mode=N_RECOVER31;n->timer=0;}else{if(n->timer>=5&&n->timer<=24){int speed=enemylarge29[i]?11:14;int nx=n->x+(n->tx*speed>>12),nz=n->z+(n->tz*speed>>12);if(!move31(n,c,nx,nz)){n->tx=n->tz=0;}}
 if(n->timer>=9&&n->timer<=26&&!enemy_cool31&&path20(c,x,y,z,n->x,n->y,n->z,r)){damage21(s);enemy_cool31=45;}}}
 else if(n->mode==N_RECOVER31&&++n->timer>=24){n->mode=N_IDLE31;n->timer=0;}
 }}
}
