#ifndef COMBAT40_H
#define COMBAT40_H
/* Reconstructed encounter rules; timings and HP are tuning, not extracted. */
enum { FIRE40, ICE40, ELECTRIC40, BUBBLE40 };
enum { NORMAL40, FROZEN40, DEAD40 };
typedef struct { unsigned char hp, state, frost; } Enemy40;
static int enemy_hit40(Enemy40 *e,int breath,int charge){
 if(e->state==DEAD40)return 0;
 if(charge && e->state==FROZEN40){e->hp=0;e->state=DEAD40;return 1;}
 if(breath==ICE40 && !charge){e->state=FROZEN40;e->frost=90;return 1;}
 if(breath==FIRE40 || breath==ELECTRIC40 || charge){if(e->hp)--e->hp;if(!e->hp)e->state=DEAD40;return 1;}return 0;
}
static void enemy_tick40(Enemy40 *e){if(e->state==FROZEN40 && e->frost && !--e->frost)e->state=NORMAL40;}
enum { ATTACK40, EXPOSE40, END40 };
typedef struct { unsigned char phase,limit,shield,hp,state,timer,cleared,final; } Ripto40;
static int ripto_limit40(int pct,int expanded){return expanded?3:pct>=100?3:pct>=85?2:pct>=70?1:0;}
static void ripto_phase40(Ripto40 *b,int phase){b->phase=phase;b->shield=phase==3?0:3;b->hp=phase==1?3:phase==2?1:6;b->state=ATTACK40;b->timer=45;}
static int ripto_start40(Ripto40 *b,int pct,int expanded){*b=(Ripto40){0};b->limit=ripto_limit40(pct,expanded);if(!b->limit)return 0;ripto_phase40(b,1);return 1;}
static void ripto_tick40(Ripto40 *b){if(!b->phase||b->state==END40)return;if(b->timer&&!--b->timer){b->state=b->state==ATTACK40?EXPOSE40:ATTACK40;b->timer=b->state==EXPOSE40?60:45;}}
/* hit is provided by collision/range validation in the caller. */
static int ripto_hit40(Ripto40 *b,int breath,int hit){
 if(!hit||b->state!=EXPOSE40||!b->phase||breath!=(b->phase==1?FIRE40:b->phase==2?ICE40:ELECTRIC40))return 0;
 if(b->shield)--b->shield;else if(b->hp)--b->hp;
 if(!b->hp){b->cleared=b->phase;if(b->phase==b->limit){b->state=END40;b->final=b->phase==3;}else ripto_phase40(b,b->phase+1);}else{b->state=ATTACK40;b->timer=45;}return 1;
}
/* Award the campaign's Ripto bit only for a full three-phase victory. */
static int ripto_full40(const Ripto40 *b){return b->state==END40&&b->final&&b->cleared==3;}
#endif
