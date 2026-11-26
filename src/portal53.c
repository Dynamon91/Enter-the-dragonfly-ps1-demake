#include "scene52.h"
typedef S52Byte U8;typedef S52Word U32;
#include "progress33.h"
#include "portal53.h"
static const U8 gates53[9]={0,1,6,15,25,35,45,55,65};
static int ledger53(const Progress33*p){
 if(!p||p->mode||p->count>90||(p->bosses&~4u)||(p->visited&~511u))return 0;
 unsigned n=0;for(int i=0;i<120;i++)if(progress_has33(p,i)){if(i>=90)return 0;n++;}return n==p->count;
}
int portal53_gate(const Progress33*p,int current,int target,int completion){
 if(!ledger53(p)||current< -1||current>9||target<0||target>9||completion<0||completion>100)return PORTAL53_BAD_STATE;
 if(current==target|| (current==-1&&target!=0) || (current>0&&target!=0))return PORTAL53_BAD_ROUTE;
 if(target==9)return completion>=70?PORTAL53_OK:PORTAL53_LOCKED;
 return p->count>=gates53[target]?PORTAL53_OK:PORTAL53_LOCKED;
}
static int s16(const U8*p){unsigned x=p[0]|(unsigned)p[1]<<8;return x>=32768?(int)x-65536:(int)x;}
static int s32(U32 x){return x<=0x7fffffffu?(int)x:-1-(int)(~x);}
static long long cross(int ax,int az,int bx,int bz){return (long long)ax*bz-(long long)az*bx;}
static long long abs64(long long x){return x<0?-x:x;}
/* Same bounded quotient and slope limit as the original cache floor query. */
static int ratio(long long a,long long b){int neg=a<0;unsigned long long n=abs64(a),d=b;unsigned q=0;for(int i=15;i>=0;i--)if(n>=(d<<i)){n-=d<<i;q|=1u<<i;}return neg?-(int)q:(int)q;}
static int floor53(const Cache52*c,const Spawn53*s,int*ground){
 const Page52*page=c->pages+c->active;int best=111,found=0;
 for(U32 k=0;k<page->count;k++){
  const U32*m=page->meta[k];const U8*p=c->buf[c->active]+page->offset[k]+64+36*m[1];
  int qx=s->x-s32(m[4]),qz=s->z-s32(m[6]);
  for(U32 i=0;i<m[2];i++,p+=24){
   int ax=s16(p),az=s16(p+4),ay=s16(p+2)+s32(m[5]);
   int bx=s16(p+6)-ax,by=s16(p+8)-s16(p+2),bz=s16(p+10)-az;
   int cx=s16(p+12)-ax,cy=s16(p+14)-s16(p+2),cz=s16(p+16)-az;
   long long d=cross(bx,bz,cx,cz);if(!d)continue;
   if(abs64(cross(by,bz,cy,cz))>2*abs64(d)||abs64(cross(bx,by,cx,cy))>2*abs64(d))continue;
   long long u=cross(qx-ax,qz-az,cx,cz),v=cross(bx,bz,qx-ax,qz-az);
   if(d<0){d=-d;u=-u;v=-v;}if(u<0||v<0||u+v>d)continue;
   int y=ay+ratio(u*by+v*cy,d),dist=y-s->y;if(dist<0)dist=-dist;
   if(dist<best){*ground=y;best=dist;found=1;}
  }
 }
 return found;
}
/* Byte copy avoids libc in the freestanding build. No cache data is copied. */
static void copy53(void*d,const void*s,unsigned n){volatile U8*a=d;const volatile U8*b=s;while(n--)*a++=*b++;}
int portal53_enter(Cache52*c,Progress33*p,const Scene52*target,const Spawn53*spawn,int completion,S52Read read,void*ctx,Spawn53*out){
 if(!c||!target||!spawn||!out||!read||c->active< -1||c->active>1||target->level>9||spawn->heading<0||spawn->heading>63||spawn->x< -200000||spawn->x>200000||spawn->y< -200000||spawn->y>200000||spawn->z< -200000||spawn->z>200000)return PORTAL53_BAD_STATE;
 int current=c->active<0?-1:(int)c->scene[c->active].level;
 int e=portal53_gate(p,current,(int)target->level,completion);if(e)return e;
 Cache52 staged;copy53(&staged,c,sizeof staged);
 if(!scene52_switch(&staged,target,spawn->x,spawn->z,read,ctx))return PORTAL53_LOAD_FAILED;
 int y;if(!floor53(&staged,spawn,&y))return PORTAL53_NO_FLOOR;
 /* Only after terrain and spawn checks succeed. Texture, script and audio
  * transactions are separate and not yet wired to this prototype. */
 copy53(c,&staged,sizeof staged);if(target->level<9)progress_visit33(p,target->level);
 out->x=spawn->x;out->y=y;out->z=spawn->z;out->heading=spawn->heading;return PORTAL53_OK;
}
