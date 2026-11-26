typedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;
#include "scene.h"
#include "world.h"
#include "player06.h"
#include "breath11.h"
#include "collect15.h"
#include "basket14.h"
#include "fodder15.h"
static Player p;static Collect c;static Breath fire;static Fodder f;static Baskets b;
void fodder_init15(void){reset_player(&p);collect_reset(&c,&p);breath_reset(&fire);for(int i=0;i<FIRE_TARGETS;i++)fire.target[i].hp=0;fodder_reset(&f);basket_reset(&b);}
void fodder_pos15(int x,int y,int z,int h){p.x=x;p.y=y;p.z=z;p.heading=p.camera=h;}
int fodder_floor15(int x,int z){return floor_at(x,z);}
void fodder_tick15(int btn){int x=p.x,z=p.z;step_player(&p,btn,0,0);breath_step(&fire,&p,btn);for(int i=0;i<FIRE_TARGETS;i++)fire.target[i].hp=0;collect_step(&c,&p,btn,f.health);basket_step(&b,&c,&fire,&p,x,z,btn);fodder_step(&f,&c,&fire,&p,x,z,btn);}
void fodder_status15(int*out){int a[]={f.state,f.health,f.hit,f.healed,f.age,p.x,p.y,p.z,f.bx,f.by,f.bz,c.score,c.assist_events,c.direct_events};for(int i=0;i<14;i++)out[i]=a[i];}
static void copy_mesh(EffectTri*a,int n,int*out){for(int i=0;i<n;i++){for(int j=0;j<3;j++){out[10*i+3*j]=a[i].v[j].x;out[10*i+3*j+1]=a[i].v[j].y;out[10*i+3*j+2]=a[i].v[j].z;}out[10*i+9]=a[i].color;}}
int fodder_mesh15(int*out){EffectTri a[FODDER_MESH_MAX];int n=fodder_mesh(&f,a);copy_mesh(a,n,out);return n;}
int fodder_collect15(int*out){EffectTri a[COLLECT_MESH_MAX];int n=collect_mesh(&c,&p,a,f.health);copy_mesh(a,n,out);return n;}
int fodder_basket15(int*out){EffectTri a[BASKET_MESH_MAX];int n=basket_mesh(&b,&c,&p,a);copy_mesh(a,n,out);return n;}
