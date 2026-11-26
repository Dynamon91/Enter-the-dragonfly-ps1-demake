typedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;
#include "scene.h"
#include "world.h"
#include "player06.h"
#include "breath11.h"
#include "collect13.h"
static Collect c;static Player p;
void collect_init13(void){reset_player(&p);collect_reset(&c,&p);}
void collect_pos13(int x,int y,int z,int heading){p.x=x;p.y=y;p.z=z;p.heading=heading;}
void collect_tick13(int btn){collect_step(&c,&p,btn);}
void collect_status13(int*out){out[0]=c.score;out[1]=c.tick;out[2]=c.sx;out[3]=c.sy;out[4]=c.sz;for(int i=0;i<GEM_COUNT;i++)out[5+i]=c.taken[i];}
int collect_mesh13(int*out){EffectTri a[COLLECT_MESH_MAX];int n=collect_mesh(&c,&p,a);for(int i=0;i<n;i++){for(int j=0;j<3;j++){out[10*i+3*j]=a[i].v[j].x;out[10*i+3*j+1]=a[i].v[j].y;out[10*i+3*j+2]=a[i].v[j].z;}out[10*i+9]=a[i].color;}return n;}
static Breath diagnostic;static int enabled,previous;
void diag_reset13(void){enabled=previous=0;breath_reset(&diagnostic);diagnostic12(&diagnostic,&enabled,0,0);}
int diag_tick13(int btn){diagnostic12(&diagnostic,&enabled,btn,previous);previous=btn;return diagnostic.target[0].hp;}

void collect_events13(int*out){out[0]=c.events;out[1]=c.direct_events;out[2]=c.assist_events;out[3]=c.target;}
int collect_floor13(int x,int z){return floor_at(x,z);}
