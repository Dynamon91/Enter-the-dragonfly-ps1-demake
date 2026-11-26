typedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;
#include "scene.h"
#include "world.h"
#include "player06.h"
#include "breath11.h"
#include "collect13.h"
#include "basket14.h"
static Player p;static Collect c;static Breath fire;static Baskets b;
void basket_init14(void){reset_player(&p);collect_reset(&c,&p);breath_reset(&fire);for(int i=0;i<FIRE_TARGETS;i++)fire.target[i].hp=0;basket_reset(&b);}
void basket_pos14(int x,int y,int z,int h){p.x=x;p.y=y;p.z=z;p.heading=p.camera=h;}
void basket_tick14(int btn){int x=p.x,z=p.z;step_player(&p,btn,0,0);breath_step(&fire,&p,btn);for(int i=0;i<FIRE_TARGETS;i++)fire.target[i].hp=0;if(btn&PAD_START)collect_reset(&c,&p);basket_step(&b,&c,&fire,&p,x,z,btn);c.tick=(c.tick+1)&255;}
void basket_status14(int*out){out[0]=c.score;out[1]=b.broken;out[2]=b.pickups;out[3]=p.x;out[4]=p.y;out[5]=p.z;for(int i=0;i<BASKET_COUNT;i++){out[6+i]=b.state[i];out[6+BASKET_COUNT+i]=b.age[i];}}
int basket_mesh14(int*out){EffectTri a[BASKET_MESH_MAX];int n=basket_mesh(&b,&c,&p,a);for(int i=0;i<n;i++){for(int j=0;j<3;j++){out[10*i+3*j]=a[i].v[j].x;out[10*i+3*j+1]=a[i].v[j].y;out[10*i+3*j+2]=a[i].v[j].z;}out[10*i+9]=a[i].color;}return n;}
int basket_floor14(int x,int z){return floor_at(x,z);}
#include "packet14.h"
void packet_roundtrip14(u32*in,u32*out){Packet q;packet_coords(&q,in[0],in[1],in[2]);for(int i=0;i<3;i++)out[i]=packetxy(&q,i);}
