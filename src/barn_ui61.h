/* Original model and texture data, using previously unused actor slots 48..50. */
#include "barn61.h"
#include "barndata61.h"
static Barn61 barn61;
static int barn_ready61;
static int barn_upload61(void){barn_ready61=0;for(int i=0;i<3;i++){
 if(!cd17_read(0,barn_extent61[0]+3*i,3,tbuf)||rd18(tbuf)!=0x54445445u||s18(tbuf+4)!=1||s18(tbuf+6)!=i||!rd18(tbuf+8)||rd18(tbuf+8)>1024||!rd18(tbuf+12)||rd18(tbuf+12)>1024||rd18(tbuf+16)!=4608||rd18(tbuf+20)!=barnmodels61[i].crc||texcrc19(tbuf+24,4608)!=barnmodels61[i].crc)return 0;
 uploadtex19(0,48+i,tbuf+24);}idle();barn_ready61=1;return 1;}
static int doorpass61(int x,int y,int z,int nx,int nz){return barn_pass61(&barn61,x,y,z,nx,nz);}
static int close61(int x,int z,int gx,int gz,int r){int dx=x-gx,dz=z-gz;return ab(dx)<=r&&ab(dz)<=r&&dx*dx+dz*dz<=r*r;}
static void queststep61(Player18*p){if(!barn_ready61)return;if(!barn61.phase&&p->grounded&&close61(p->x,p->z,3133,3756,900))for(int i=0;i<FIRE21;i++){
 Flame21*f=interactions.fire+i;
 /* Fuse tip is the original local (-83,-14,-450) transformed by yaw 48.
  * Breath particles are emitted above root; accept the local vertical band. */
 if(f->life&&close61(f->x,f->z,3133,3756,125)&&ab(f->y+414)<=180&&path20(&cache,p->x,p->ground,p->z,3133,-400,3756,900)){
  if(barn_hit61(&barn61,&talk60)){f->life=0;sfx_play(2);}break;}}
 barn_tick61(&barn61,&talk60,escape61);}
static void barn_draw61(Player18*p,int cx,int cy,int cz,int sn,int cs){if(!barn_ready61)return;
 for(int i=0;i<3;i++){const ActorPlacement61*a=barnprops61+i;if(i==2&&barn61.phase>=2)continue;if(ab(a->x-p->x)>2300||ab(a->z-p->z)>2300)continue;const ActorModel61*m=barnmodels61+i;int yaw=(a->yaw+(i==0?-barn61.door:i==1?barn61.door:0))&63;int as=sine[yaw],ac=sine[(yaw+16)&63];
  for(int f=0;f<m->nf;f++){Point q[3];const ActorFace61*t=m->f+f;for(int j=0;j<3;j++){const s16*v=m->v[t->ix[j]];q[j]=transform(a->x+((ac*v[0]+as*v[2])>>12),a->y+v[1],a->z+((ac*v[2]-as*v[0])>>12),cx,cy,cz,sn,cs);q[j].u=t->uv[j*2];q[j].v=t->uv[j*2+1];}worldtri(q[0],q[1],q[2],ACTOR_ID59+7+i);}}
 for(int i=0;i<5;i++){const EscapeCow61*c=barn61.cows+i;if(c->segment>=6||ab(c->x-p->x)>1536||ab(c->z-p->z)>1536)continue;const ActorModel59*m=models59;int as=sine[c->yaw],ac=sine[(c->yaw+16)&63];for(int f=0;f<m->nf;f++){Point q[3];const ActorFace59*t=m->f+f;for(int j=0;j<3;j++){const s16*v=m->v[t->ix[j]];q[j]=transform(c->x+((ac*v[0]+as*v[2])>>12),c->y+v[1],c->z+((ac*v[2]-as*v[0])>>12),cx,cy,cz,sn,cs);q[j].u=t->uv[j*2];q[j].v=t->uv[j*2+1];}worldtri(q[0],q[1],q[2],ACTOR_ID59);}}
}
static void barn_hud61(Player18*p){if(active60(&talk60))return;if(!close61(p->x,p->z,2897,3653,2300))return;rect(5,197,195,13,0x201c28);if(!barn61.phase)text60(10,198,"LIGHT THE FUSE",0xffffff);else if(barn61.phase<3)text60(10,198,"BARN DOORS OPENING",0xffffff);else if(barn61.phase==3){text60(10,198,"COWS ESCAPING",0xffffff);glyph60(100,198,'0'+barn61.escaped,0xffffff);text60(106,198,"/5",0xffffff);}else text60(10,198,"COWS FREED - TALK TO BILL",0xffffff);}
