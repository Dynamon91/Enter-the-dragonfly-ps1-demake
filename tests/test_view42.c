#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "arena41.h"
#include "draw41.h"
#include "view42.h"
static unsigned char img[240][320][3];static int draws,maxdraw,paint;
static void pixel(int x,int y,unsigned c){if(x>=0&&x<320&&y>=0&&y<240){img[y][x][0]=c;img[y][x][1]=c>>8;img[y][x][2]=c>>16;}}
static void r(int x,int y,int w,int h,unsigned c){assert(w>0&&h>0);if(paint)for(int j=y;j<y+h;j++)for(int i=x;i<x+w;i++)pixel(i,j,c);}
static int cross(P42 a,P42 b,int x,int y){return (b.x-a.x)*(y-a.y)-(b.y-a.y)*(x-a.x);}
static void t(P42 a,P42 b,P42 c,unsigned col){draws++;assert(a.x>=-150&&a.x<=470&&a.y>=-100&&a.y<=340);assert(b.x>=-150&&b.x<=470&&b.y>=-100&&b.y<=340);assert(c.x>=-150&&c.x<=470&&c.y>=-100&&c.y<=340);assert(cross(a,b,c.x,c.y));if(!paint)return;int l=clamp41(a.x<b.x?(a.x<c.x?a.x:c.x):(b.x<c.x?b.x:c.x),0,319),rr=clamp41(a.x>b.x?(a.x>c.x?a.x:c.x):(b.x>c.x?b.x:c.x),0,319);int top=clamp41(a.y<b.y?(a.y<c.y?a.y:c.y):(b.y<c.y?b.y:c.y),0,239),bot=clamp41(a.y>b.y?(a.y>c.y?a.y:c.y):(b.y>c.y?b.y:c.y),0,239);for(int y=top;y<=bot;y++)for(int x=l;x<=rr;x++){int u=cross(a,b,x,y),v=cross(b,c,x,y),w=cross(c,a,x,y);if((u>=0&&v>=0&&w>=0)||(u<=0&&v<=0&&w<=0))pixel(x,y,col);}}
static View42 view;
static void check(Arena41*a){draws=0;render42(&view,a,r,t);assert(!view.dropped);assert(draws>90&&draws<=CAP42+112);for(int i=1;i<view.n;i++)assert(view.t[i-1].depth<=view.t[i].depth);if(draws>maxdraw)maxdraw=draws;}
int main(int argc,char**argv){Arena41 a;int frames=0;assert(project42((V42){160,0,200}).y>project42((V42){160,0,40}).y);assert(project42((V42){160,20,100}).y<project42((V42){160,0,100}).y);for(int id=0;id<5;id++)for(int face=0;face<4;face++)for(int edge=0;edge<4;edge++){arena_init41(&a,id,0);a.face=face;a.px=edge&1?20:300;a.py=edge&2?44:204;a.bx=edge&1?288:32;a.by=edge&2?190:56;a.cd=12;a.state=A41_ATTACK;a.timer=2;for(int i=0;i<6;i++)a.shot[i]=(Shot41){32+i*45,60+i*22,0,0,60};check(&a);frames++;}
 for(int id=0;id<5;id++){arena_init41(&a,id,0);for(int i=0;i<600;i++){step41(&a,(i/30)%2?A41_LEFT|A41_BREATH:A41_RIGHT|A41_CHARGE);if(i%7==0){check(&a);frames++;}}}
 printf("%d frames checked; peak %d triangles submitted; no overflow\n",frames,maxdraw);
 if(argc>1){arena_init41(&a,0,0);a.px=138;a.py=175;a.bx=174;a.by=86;a.state=A41_OPEN;a.timer=38;paint=1;check(&a);FILE*f=fopen(argv[1],"wb");assert(f);fputs("P6\n320 240\n255\n",f);fwrite(img,1,sizeof img,f);fclose(f);}return 0;}
