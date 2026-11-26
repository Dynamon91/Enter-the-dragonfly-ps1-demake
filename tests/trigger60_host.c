#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cache24.c"
#include "collect21.h"
typedef unsigned int u32;typedef unsigned short u16;typedef signed short s16;
typedef struct {int x,y,z,ground,vy,grounded,heading,camera,prev;} Player18;
#define PAD_CROSS 16384
static int ab(int x){return x<0?-x:x;}
static Cache18 cache;static U8 idx[30720],*disk,tbuf[6144];static U32 len,bytes,voice_extent60[2];static int sfx_ready=0;
#define SPU_KON 0x188
#define SPU_KOF 0x18c
#define SPU_ATTR 0x1aa
#define SPU_WRITE(a,b) ((void)0)
#define SPU_DELAY() ((void)0)
static int spu_mode(int x){return 0;}static int spu_wait(int a,int b){return 0;}
static int cd17_read(void*c,U32 l,U32 n,U8*p){if(l+n>bytes/2048)return 0;memcpy(p,disk+l*2048,n*2048);return 1;}
static void rect(int x,int y,int w,int h,u32 color){assert(x>=0&&y>=0&&x+w<=320&&y+h<=240);}
#include "talk_ui60.h"
int main(int argc,char**argv){assert(argc==3);FILE*f=fopen(argv[1],"rb");assert(f);len=fread(idx,1,sizeof idx,f);fclose(f);f=fopen(argv[2],"rb");assert(f);fseek(f,0,SEEK_END);bytes=ftell(f);rewind(f);disk=malloc(bytes);assert(disk&&fread(disk,1,bytes,f)==bytes);fclose(f);cache18_init(&cache);reset60(&talk60);Player18 p={10645,-603,19103,-603,0,1,0,0,0};assert(cache18_update(&cache,idx,len,bytes/2048,p.x,p.z,cd17_read,0));printf("Spawn farmer candidate %d\n",farmer60(&p));assert(farmer60(&p)==0);assert(control60(&p,0)&&talk60.line==4101);hud60(&p);assert(control60(&p,PAD_CROSS)&&talk60.line==4102);assert(control60(&p,PAD_CROSS)&&talk60.line==4102);assert(control60(&p,0));assert(control60(&p,PAD_CROSS)&&talk60.line==4103);assert(control60(&p,0));assert(control60(&p,PAD_CROSS)&&!active60(&talk60));p.prev=0;assert(!control60(&p,0));assert(control60(&p,4096)&&talk60.line==4104);reset60(&talk60);p.grounded=0;assert(!control60(&p,0));printf("Actual original spawn conversation trigger, held button suppression, text bounds and repeat prompt passed\n");free(disk);}
