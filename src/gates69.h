#ifndef GATES69_H
#define GATES69_H
#include "gatedata69.h"
/* Group 3 source flags; timers approximate original scripted pauses.
 * Front: charge/flame; remaining buttons: Super Smash. Prison button's EDF
 * sets 12 only; do not fabricate gate_prison.scr execution or flag 18. */
typedef struct {unsigned char state[5],timer[5],door[3],smash; unsigned char flags[128];} Gates69;
static Gates69 gates69;
static int flag69(int n){return !!(gates69.flags[n>>3]&(1u<<(n&7)));}
static void setflag69(int n){gates69.flags[n>>3]|=1u<<(n&7);}
static void reset_gates69(void){volatile unsigned char*p=(volatile unsigned char*)&gates69;for(unsigned i=0;i<sizeof gates69;i++)p[i]=0;}
static int press69(int i,int hit){if(i<0||i>=5||gates69.state[i]||!(i==0?(hit==1||hit==2):hit==3))return 0;gates69.state[i]=1;gates69.timer[i]=i==1?1:40;switch(i){case 0:setflag69(0);break;case 1:setflag69(12);break;case 2:setflag69(3);break;case 3:setflag69(6);setflag69(16);break;case 4:setflag69(11);break;}return 1;}
static void tick_gates69(void){for(int i=0;i<5;i++)if(gates69.state[i]==1&&!--gates69.timer[i]){gates69.state[i]=2;switch(i){case 0:setflag69(14);break;case 2:setflag69(4);setflag69(15);break;case 3:setflag69(7);setflag69(13);break;case 4:setflag69(10);break;}}static const unsigned char f[]={3,16,11};for(int i=0;i<3;i++)if(flag69(f[i])&&gates69.door[i]<32)gates69.door[i]++;}
/* Thin oriented closed-door proxy based on recovered local bounds. Gate
 * opening animation is vertical lift; retain collision until fully open. */
static int gate_pass69(int x,int y,int z,int nx,int nz){for(int i=0;i<3;i++){if(gates69.door[i]>=32)continue;const int*a=gatepos69[i];if(abs18(x-a[0])>900||abs18(z-a[2])>900||y<a[1]-1000||y>a[1]+120)continue;int sn=sine[a[3]],cs=sine[(a[3]+16)&63];int z0=((x-a[0])*sn+(z-a[2])*cs)>>12,z1=((nx-a[0])*sn+(nz-a[2])*cs)>>12;if((z0<0&&z1>=0)||(z0>=0&&z1<0)){int u0=((x-a[0])*cs-(z-a[2])*sn)>>12,u1=((nx-a[0])*cs-(nz-a[2])*sn)>>12;int u=u0+(u1-u0)*z0/(z0-z1);if(abs18(u)<=620)return 0;}}return 1;}
/* Triangle while airborne is the reconstructed Super Smash control. It is
 * committed only when actual movement lands on a source button. */
static void smash_input69(Player18*p,int btn){if(swim67.active){gates69.smash=0;return;}if(!p->grounded&&(btn&4096)&&!(p->prev&4096)){gates69.smash=1;p->vy=52;}}
static int gates_step69(Player18*p,int ox,int oz,int btn,int flame){int hit=0;if(swim67.active){gates69.smash=0;tick_gates69();return 0;}
 for(int i=0;i<5;i++){const int*a=buttonpos69[i];if(gates69.state[i]||abs18(p->x-a[0])>850||abs18(p->z-a[2])>850)continue;
  int attack=0;if(i==0&&p->grounded&&(btn&PAD_SQUARE)&&(ox!=p->x||oz!=p->z)&&near68(p->x,p->y,p->z,a[0],a[1],a[2],180,125))attack=1;
  if(i==0&&flame)for(int j=0;j<FIRE21;j++){Flame21*f=interactions.fire+j;if(f->life&&near68(f->x,f->y,f->z,a[0],a[1]-40,a[2],140,205)&&path20(&cache,p->x,p->ground,p->z,a[0],p->ground,a[2],900)){f->life=0;attack=2;break;}}
  if(i&&gates69.smash&&p->grounded&&near68(p->x,p->y,p->z,a[0],a[1],a[2],190,125))attack=3;
  if(attack&&press69(i,attack))hit++;
 }if(p->grounded)gates69.smash=0;tick_gates69();return hit;}
#endif
