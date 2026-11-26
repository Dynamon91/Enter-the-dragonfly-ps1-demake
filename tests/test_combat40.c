#include <assert.h>
#include <stdio.h>
#include "combat40.h"
static void expose(Ripto40*b){for(int i=0;i<45;i++)ripto_tick40(b);assert(b->state==EXPOSE40);}
static void run(int pct,int exp,int phases){Ripto40 b;assert(ripto_start40(&b,pct,exp)==!!phases);if(!phases)return;assert(b.limit==phases);int hits=0;while(b.state!=END40){int br=b.phase-1;assert(!ripto_hit40(&b,br,1));expose(&b);assert(!ripto_hit40(&b,(br+1)%3,1));assert(!ripto_hit40(&b,br,0));assert(ripto_hit40(&b,br,1));assert(++hits<=16);}assert(b.cleared==phases);assert(ripto_full40(&b)==(phases==3));assert(!ripto_hit40(&b,ELECTRIC40,1));}
int main(void){run(69,0,0);run(70,0,1);run(84,0,1);run(85,0,2);run(99,0,2);run(100,0,3);run(0,1,3);Enemy40 e={2,0,0};assert(enemy_hit40(&e,ICE40,0));for(int i=0;i<89;i++)enemy_tick40(&e);assert(e.state==FROZEN40);enemy_tick40(&e);assert(e.state==NORMAL40);assert(enemy_hit40(&e,ICE40,0));assert(enemy_hit40(&e,ICE40,1)&&e.state==DEAD40);assert(!enemy_hit40(&e,FIRE40,0));puts("7 boss scenarios + ice/charge lifecycle passed");return 0;}
