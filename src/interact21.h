/* Persistent source-ID interactions. Rewards and behavior are reconstructed, not PS2 scripts. */
#include "objectids21.h"
#define OBJ21 39
#define FIRE21 24
#define LIFE21 13
#define BASK21 27
#define SHEEP21 12
/* state: 0 intact, 1 reward active, 2 consumed/expired. */
typedef struct {int x,y,z,vx,vy,vz,life;} Flame21;
typedef struct {int x,y,z,age;} Butterfly21;
typedef struct {U8 state[OBJ21],age[OBJ21];Butterfly21 butterfly[SHEEP21];Flame21 fire[FIRE21];int health,score,broken,pickups,healed,hit,cooldown,tick;} Interact21;
static int objectid21(U32 id,int kind){for(int i=0;i<OBJ21;i++)if(objectids21[i]==id&&kind==(i<BASK21?2:3))return i;return -1;}
static void interreset21(Interact21*s){for(int i=0;i<OBJ21;i++)s->state[i]=s->age[i]=0;for(int i=0;i<SHEEP21;i++)s->butterfly[i]=(Butterfly21){0,0,0,0};for(int i=0;i<FIRE21;i++)s->fire[i].life=0;s->health=3;s->score=s->broken=s->pickups=s->healed=s->hit=s->cooldown=s->tick=0;}
static int near21(int x,int y,int z,int gx,int gy,int gz,int r){int dx=x-gx,dz=z-gz;return abs18(dx)<=r&&abs18(dz)<=r&&dx*dx+dz*dz<=r*r&&y>=gy-200&&y<=gy+30;}
static void damage21(Interact21*s){if(s->health>0)s->health--;}
static void firestep21(Interact21*s,const Cache18*c,int x,int y,int z,int heading,int firing,int grounded,const short*sn){
 if(s->cooldown)s->cooldown--;
 for(int i=0;i<FIRE21;i++){Flame21*f=s->fire+i;if(!f->life)continue;int g=cache18_floor(c,f->x,f->z,f->y+135,170);f->x+=f->vx;f->y+=f->vy;f->z+=f->vz;int h=cache18_floor(c,f->x,f->z,g,110);if(g==NONE18||h==NONE18||f->y>=h||abs18(g-h)>110)f->life=0;else f->life--;}
 if(!firing||!grounded||s->cooldown)return;s->cooldown=3;int a=sn[heading&63],b=sn[(heading+16)&63];
 /* Check the initial mouth-to-particle path as well as subsequent motion. */
 int fx=x+(a*100>>12),fz=z+(b*100>>12);if(!path20(c,x,y,z,fx,y,fz,110))return;
 for(int k=0;k<3;k++)for(int i=0;i<FIRE21;i++)if(!s->fire[i].life){int side=(k-1)*8;s->fire[i]=(Flame21){fx,y-135,fz,(a*34+b*side)>>12,-1-(k==1),(b*34-a*side)>>12,LIFE21};break;}
}
static void interstep21(Interact21*s,const Cache18*c,int x,int y,int z,int ox,int oz,int heading,int charge,int firing,int grounded,int sx,int sy,int sz,const short*sn){
 s->broken=s->pickups=s->healed=s->hit=0;s->tick=(s->tick+1)&255;firestep21(s,c,x,y,z,heading,firing,grounded,sn);
 for(int i=0;i<OBJ21;i++)if(s->state[i]==1){if(i<BASK21){if(s->age[i]<10)s->age[i]++;}else if(++s->butterfly[i-BASK21].age>=180)s->state[i]=2;}
 for(int j=0;j<c->count;j++){int k=c->active[j];const U32*m=c->meta[k];const U8*t=c->bytes[k]+64+m[1]*36+m[2]*24;for(U32 n=0;n<m[3];n++,t+=16){int kind=s18(t+6);if(kind!=2&&kind!=3)continue;int id=objectid21(rd18(t+12),kind);if(id<0||s->state[id]==2)continue;int gx=s18(t)+(int)m[4],gy=s18(t+2)+(int)m[5],gz=s18(t+4)+(int)m[6];
 if(abs18(gx-x)>1500||abs18(gz-z)>1500)continue;
 if(!s->state[id]){int hit=0,r=kind==2?145:115;
 if(charge&&grounded&&(ox!=x||oz!=z)&&path20(c,x,y,z,gx,gy,gz,180))for(int h=0;h<=4;h++)if(near21(ox+(x-ox)*h/4,y-70,oz+(z-oz)*h/4,gx,gy,gz,r)){hit=1;break;}
 if(!hit)for(int h=0;h<FIRE21;h++){Flame21*f=s->fire+h;if(f->life&&near21(f->x,f->y,f->z,gx,gy,gz,kind==2?92:100)&&path20(c,f->x,f->y+135,f->z,gx,gy,gz,125)){hit=1;f->life=0;break;}}
 if(hit){s->state[id]=1;s->age[id]=0;s->hit++;if(kind==2)s->broken++;else s->butterfly[id-BASK21]=(Butterfly21){gx,gy-150,gz,0};}continue;}
 if(kind==2){if(s->age[id]>=10&&path20(c,x,y,z,gx,gy,gz,180)){s->state[id]=2;s->score++;s->pickups++;}}
 else{Butterfly21*b=s->butterfly+id-BASK21;if(b->age<10||!path20(c,x,y,z,gx,gy,gz,520))continue;int tx=s->health?sx:x,ty=s->health?sy:y-100,tz=s->health?sz:z;b->x+=(tx-b->x)/5;b->y+=(ty-b->y)/5;b->z+=(tz-b->z)/5;if(abs18(b->x-tx)<=24&&abs18(b->y-ty)<=24&&abs18(b->z-tz)<=24){s->state[id]=2;if(s->health<3){s->health++;s->healed++;}}}
 }}
}
