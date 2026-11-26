#ifndef SCREEN43_H
#define SCREEN43_H
#include "draw41.h"
#include "view42.h"
/* 3x5 monochrome glyphs, custom tiny diagnostic font. */
static const unsigned short font43[]={0x7b6f,0x2492,0x73e7,0x73cf,0x5bc9,0x79cf,0x79ef,0x7249,0x7bef,0x7bcf,0x2bed,0x6bae,0x7927,0x6b6e,0x79e7,0x79e4,0x796f,0x5bed,0x7497,0x126e,0x5bad,0x4927,0x5fed,0x5f6d,0x7b6f,0x7be4,0x7b7b,0x7bad,0x79cf,0x7492,0x5b6f,0x5b6a,0x5bfd,0x5aad,0x5a92,0x72a7};
static void text43(Rect41 r,int x,int y,const char*s,unsigned c){for(;*s;s++,x+=8){int n=*s>='0'&&*s<='9'?*s-'0':*s>='A'&&*s<='Z'?*s-'A'+10:-1;if(n<0)continue;for(int i=0;i<15;i++)if(font43[n]&(1u<<(14-i)))r(x+2*(i%3),y+2*(i/3),2,2,c);}}
static void num43(Rect41 r,int x,int y,int n){char s[4]={(char)('0'+n/100),(char)('0'+n/10%10),(char)('0'+n%10),0};text43(r,x,y,s,0xffffff);}
static const char*const names43[]={"DRAGON REALMS","DRAGONFLY DOJO","CROP CIRCLE COUNTRY","LUAU ISLAND","CLOUD 9","MONKEY MONASTERY","HONEY MARSH","THIEVES DEN","JURASSIC JUNGLE","EMERALD FOREST","BAKED ALASKA","CUTTHROATS COVE","BRIARWOOD VILLAGE","LANTERN GROTTO","MOONLIT CANOPY","CRYSTAL ORCHARD","FROSTBITE PASS","GLACIER FOUNDRY","AVALANCHE ABBEY","SUNKEN OBSERVATORY","STORMBREAK COAST","CORSAIR CAVERNS","GNORC IRONWORKS","CLOCKWORK CITADEL","THUNDER QUARRY","OBSIDIAN RAMPARTS","TWIN TYRANTS KEEP","ENCHANTED REALMS","FORGOTTEN REALMS","GNORC KINGDOM","CRUSH","GULP","RIPTO","GNASTY GNORC","FINAL ALLIANCE"};
static void screen43(View42*v,const Session43*s,Rect41 rect,Tri42 tri){const Arena41*a=&s->a;if(s->route.current_kind==WP38_BOSS){render42(v,a,rect,tri);rect(0,0,320,16,0x30251e);text43(rect,8,3,names43[30+a->id],0xffffff);text43(rect,216,3,"FLIES",0xffffff);num43(rect,264,3,s->p.count);return;}
 v->n=v->dropped=0;rect(0,0,320,240,0x684047);rect(0,35,320,205,0x51433d);int l=s->route.current_id;
 for(int z=40;z<208;z+=24)for(int x=16;x<304;x+=36){int zz=clamp41(z+24,40,208);unsigned c=((x/36+z/24)&1)?0x526c63:0x476059;c^=(unsigned)(l%5)*0x040408;quad42(v,(V42){x,0,z},(V42){x+36,0,z},(V42){x+36,0,zz},(V42){x,0,zz},c);}
 for(int i=0;i<v->n;i++)tri(v->t[i].p[0],v->t[i].p[1],v->t[i].p[2],v->t[i].c);v->n=0;
 for(int x=32;x<=288;x+=64)box42(v,x,43,0,7,6,35,0x9b8980);
 WpRange39 rr=wp_slots39[l];for(int i=0;i<rr.count;i++)if(!progress_has33(&s->p,rr.first+i)){int x,y;spot43(l,i,&x,&y);gem42(v,x,y,13,5,7,0x40eaff);face42(v,(V42){x,13,y},(V42){x-12,19,y},(V42){x-10,9,y},0xe0f0ff);face42(v,(V42){x,13,y},(V42){x+12,19,y},(V42){x+10,9,y},0xe0f0ff);}
 dragon42(v,a);for(int i=1;i<v->n;i++){T42 t=v->t[i];int j=i;while(j&&v->t[j-1].depth>t.depth){v->t[j]=v->t[j-1];j--;}v->t[j]=t;}for(int i=0;i<v->n;i++)tri(v->t[i].p[0],v->t[i].p[1],v->t[i].p[2],v->t[i].c);
 rect(0,0,320,35,0x30251e);text43(rect,8,4,names43[l],0xffffff);text43(rect,8,19,"FLIES",0xffffff);num43(rect,56,19,s->p.count);text43(rect,96,19,"ROOM",0xffffff);U8 f,t;wp_atlas39(&s->p,l,&f,&t);num43(rect,136,19,f);num43(rect,168,19,t);
 rect(0,210,320,30,0x30251e);text43(rect,8,214,names43[s->selection],eligible43(s,s->selection)?0x6070ff:0x80ef80);text43(rect,8,228,"L1 R1 SELECT   X ENTER",0xffffff);if(s->error)text43(rect,248,214,"LOCKED",0x6070ff);
}
#endif
