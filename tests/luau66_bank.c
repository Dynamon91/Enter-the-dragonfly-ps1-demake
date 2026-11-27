/* Run every real bank block through native readers using memory CD callbacks. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cache24.c"
#include "tex19.h"
static U8 *d,*t;static U32 ds,ts;static int uploads;
static U8 *load(const char*path,U32*n){FILE*f=fopen(path,"rb");assert(f);fseek(f,0,SEEK_END);*n=ftell(f);rewind(f);U8*p=malloc(*n);assert(p&&fread(p,1,*n,f)==*n);fclose(f);return p;}
static int read66(void*ctx,U32 l,U32 n,U8*p){U8*a=ctx? t:d;U32 bytes=ctx?ts:ds;if(l>bytes/2048||n>bytes/2048-l)return 0;memcpy(p,a+l*2048,n*2048);return 1;}
static void upload66(void*ctx,int slot,const U8*p){(void)ctx;assert(slot>=0&&slot<TEXCAP19&&p);uploads++;}
int main(int argc,char**argv){assert(argc==5);U32 il,tl;U8*ix=load(argv[1],&il),*ti=load(argv[3],&tl);d=load(argv[2],&ds);t=load(argv[4],&ts);static U8 buf[65536];U32 m[7];assert(texindex19(ti,tl,ts/2048));for(int i=0;i<BLOCKS18;i++){assert(sector16_load(ix,il,i,ds/2048,MAT18,90812,7601,buf,sizeof buf,read66,0,m));}U32 freq[GROUPCAP19]={0};Tex19 tex;texinit19(&tex);for(int i=0;i<TEXCOUNT19;i++){const U8*e=ti+12+i*12;assert(read66((void*)1,rd18(e+4),3,buf)&&texblock19(buf,e));int g=rd18(e);freq[g]=1;texrefresh19(&tex,ti,freq,read66,(void*)1,upload66,0,buf);assert(tex.map[g]>=0);freq[g]=0;}assert(uploads==82&&!tex.failed&&!tex.missing);printf("498 native terrain reads, 82 CRC-checked texture reads/uploads passed\n");free(ix);free(ti);free(d);free(t);}
