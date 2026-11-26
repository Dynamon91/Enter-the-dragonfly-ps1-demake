#include <assert.h>
#include <stdio.h>
#include "xa47.h"
static unsigned at,starts,stops,where,file,channel;static int failstart,failpos,failstop;
static int start(unsigned l,unsigned f,unsigned c){starts++;where=l;file=f;channel=c;return !failstart;}
static int pos(unsigned*p){*p=at;return !failpos;}
static int stop(void){stops++;return !failstop;}
static const Bus47 b={start,pos,stop};
int main(void){Track47 t={300,332,308,324,1,2,1};Player47 p={0};assert(valid47(&t));assert(begin47(&p,&b,&t)&&where==300&&file==1&&channel==2);at=22;assert(poll47(&p,&b)&&p.waiting);at=300;assert(poll47(&p,&b)&&!p.waiting);at=331;assert(poll47(&p,&b)&&p.loops==0);at=332;assert(poll47(&p,&b)&&p.loops==1&&where==308&&starts==2&&stops==1);at=308;assert(poll47(&p,&b));assert(stop47(&p,&b)&&p.state==XA47_IDLE);assert(stop47(&p,&b)&&stops==2);
 t.loop=0;assert(begin47(&p,&b,&t));at=340;assert(poll47(&p,&b)&&p.state==XA47_IDLE);t.channel=32;assert(!begin47(&p,&b,&t)&&p.state==XA47_IDLE);t.channel=2;assert(begin47(&p,&b,&t));at=300;assert(poll47(&p,&b));for(int i=0;i<120;i++)assert(poll47(&p,&b));assert(!poll47(&p,&b)&&p.state==XA47_FAULT);assert(!begin47(&p,&b,&t));
 p=(Player47){0};failstart=1;assert(!begin47(&p,&b,&t)&&p.state==XA47_FAULT);failstart=0;p=(Player47){0};assert(begin47(&p,&b,&t));failpos=1;assert(!poll47(&p,&b)&&p.state==XA47_FAULT);failpos=0;p=(Player47){0};assert(begin47(&p,&b,&t));failstop=1;assert(!stop47(&p,&b)&&p.state==XA47_FAULT);puts("XA transport: loop, EOF, stop, routing, stale and failure cases passed");return 0;}
