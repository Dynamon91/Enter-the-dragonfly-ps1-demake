#include "talk60.h"
#include "voice60.h"
static Talk60 talk60;
static void glyph60(int x,int y,int c,u32 color){if(c<32||c>126)return;const U8*g=talkfont60[c-32];for(int j=0;j<10;j++){int i=0;while(i<6){if(!(g[j]&(1<<(5-i)))){i++;continue;}int start=i;while(i<6&&(g[j]&(1<<(5-i))))i++;rect(x+start,y+j,i-start,1,color);}}}
static void text60(int x,int y,const char*s,u32 color){int xx=x;for(;*s;s++){if(*s=='\n'){xx=x;y+=10;}else{glyph60(xx,y,*s,color);xx+=6;}}}
static int farmer60(const Player18*p){static const int pos[3][3]={{9871,-603,18553},{1681,-396,4208},{14394,-192,-5061}};int best=-1,dist=1000000;for(int i=0;i<3;i++){int x=ab(p->x-pos[i][0]),y=ab(p->y-pos[i][1]),z=ab(p->z-pos[i][2]);if(x<=1000&&z<=1000&&y<=180&&x*x+z*z<=1000000&&x*x+z*z<dist&&path20(&cache,p->x,p->y,p->z,pos[i][0],pos[i][1],pos[i][2],1000)){best=i;dist=x*x+z*z;}}return best;}
/* Returns 1 if conversation consumes this tick. Cross advances; Triangle starts.
 * Grounded source placement triggers only. No physics or combat during subtitle. */
static int control60(Player18*p,int btn){int edge=btn&~p->prev;if(active60(&talk60)){if(edge&(PAD_CROSS|4096)){if(advance60(&talk60))voice_play60(talk60.line);else voice_stop60();}p->prev=btn;return 1;}if(!p->grounded)return 0;int actor=farmer60(p);if(actor>=0&&(!talk60.greeted[actor]||(edge&4096))){if(begin60(&talk60,actor)){voice_play60(talk60.line);p->prev=btn;return 1;}}return 0;}
static void hud60(Player18*p){if(active60(&talk60)){rect(5,151,310,84,0x201c28);rect(5,151,310,2,0x9b73d4);rect(5,233,310,2,0x9b73d4);text60(12,155,talk60.speaker==2?"Spyro":talk60.speaker==3?"Sparx":talktext60(scripts60[talk60.script].name),0x72d8ff);text60(12,168,talktext60(talk60.line),0xffffff);text60(256,155,"X NEXT",0xcac0e0);}else if(p->grounded&&farmer60(p)>=0){rect(89,212,142,18,0x201c28);text60(100,215,"TRIANGLE: TALK",0xffffff);}}
