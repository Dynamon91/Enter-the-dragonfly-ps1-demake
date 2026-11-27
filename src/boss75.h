#ifndef BOSS75_H
#define BOSS75_H
/* Original EDF health 3,20,5; two shields 10. Original vulnerability classes.
 * Timings, stationary attack loop and single-arena stage handoff reconstructed. */
enum {BOSS_FIRE75=0,BOSS_ICE75=1,BOSS_LIGHT75=2};
enum {BOSS_SHIELD75=0,BOSS_EXPOSED75=1,BOSS_WINDUP75=2,BOSS_STUCK75=3,BOSS_WON75=4};
typedef struct {int stage,hp,shield,phase,tick,cooldown,invuln,mode,hitnotice,won;unsigned char flags[128];} Boss75;
static const int hp75[]={3,20,5};
static int flagboss75(const Boss75*b,int n){return !!(b->flags[n/8]&(1u<<(n&7)));}
static void setboss75(Boss75*b,int n){b->flags[n/8]|=1u<<(n&7);}
static void boss_reset75(Boss75*b){volatile unsigned char*q=(volatile unsigned char*)b;for(unsigned i=0;i<sizeof *b;i++)q[i]=0;b->hp=3;b->shield=10;}
static int boss_attack75(Boss75*b,int breath){if(b->won||b->cooldown||breath<0||breath>2)return 0;
 if(b->phase==BOSS_SHIELD75){if(breath!=b->stage)return 0;if(--b->shield==0){b->phase=BOSS_EXPOSED75;b->tick=0;}b->cooldown=9;b->hitnotice=12;return 1;}
 if(!(b->phase==BOSS_EXPOSED75||(b->phase==BOSS_STUCK75&&breath==BOSS_LIGHT75)))return 0;
 if(b->stage==2&&breath!=BOSS_LIGHT75)return 0;
 b->cooldown=9;b->hitnotice=12;if(--b->hp>0)return 1;
 if(b->stage<2){b->stage++;b->hp=hp75[b->stage];b->shield=b->stage==1?10:0;b->phase=b->stage==1?BOSS_SHIELD75:BOSS_WINDUP75;b->tick=0;setboss75(b,b->stage==1?52:53);}
 else {b->phase=BOSS_WON75;b->won=1;setboss75(b,199);setboss75(b,102);setboss75(b,103);setboss75(b,562);}return 1;}
static int boss_tick75(Boss75*b){if(b->won)return 0;if(b->cooldown)b->cooldown--;if(b->invuln)b->invuln--;if(b->hitnotice)b->hitnotice--;b->tick++;
 if(b->phase==BOSS_SHIELD75||b->phase==BOSS_EXPOSED75){if(b->tick>=75){b->tick=0;return b->stage+1;}return 0;}
 if(b->phase==BOSS_WINDUP75&&b->tick>=65){b->tick=0;b->phase=BOSS_STUCK75;return 3;}
 if(b->phase==BOSS_STUCK75&&b->tick>=90){b->phase=BOSS_WINDUP75;b->tick=0;}return 0;}
#endif
