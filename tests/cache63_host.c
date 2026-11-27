/* Exhaustive selection sweep, and real-bank transitions with the reduced pool. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cache24.c"
static Cache18 cache;
static U8 idx[30720],*disk;static U32 len,bytes;static int bad;
static int read63(void*ctx,U32 l,U32 n,U8*p){(void)ctx;if(bad||l>bytes/2048||n>bytes/2048-l)return 0;memcpy(p,disk+l*2048,n*2048);return 1;}
static int snap63(int*x){for(int i=0;i<cache.count;i++)x[i]=cache.ids[cache.active[i]];return cache.count;}
int main(int argc,char**argv){assert(argc==3);FILE*f=fopen(argv[1],"rb");assert(f);len=fread(idx,1,sizeof idx,f);fclose(f);f=fopen(argv[2],"rb");assert(f);fseek(f,0,SEEK_END);bytes=ftell(f);rewind(f);disk=malloc(bytes);assert(disk&&fread(disk,1,bytes,f)==bytes);fclose(f);
 int xmin=200000,xmax=-200000,zmin=200000,zmax=-200000;for(int i=0;i<BLOCKS18;i++){const U8*e=idx+16+60*i;int x=(int)rd18(e+28),xx=(int)rd18(e+40),z=(int)rd18(e+36),zz=(int)rd18(e+48);if(x<xmin)xmin=x;if(xx>xmax)xmax=xx;if(z<zmin)zmin=z;if(zz>zmax)zmax=zz;}
 int occ=0,peak=0,cap=0,loads=0;cache18_init(&cache);for(int x=anchor18(xmin)-2048;x<=anchor18(xmax)+2048;x+=512)for(int z=anchor18(zmin)-2048;z<=anchor18(zmax)+2048;z+=512){int ids[CAP18];int n=cache18_select(idx,len,x,z,ids);assert(n>=0);if(!n)continue;occ++;U32 size=0;for(int j=0;j<n;j++)size+=blocksize22(idx,ids[j]);assert(size<=ARENA22);if(size>(U32)peak)peak=size;if(n>cap)cap=n;
 /* Stratified transition sample, including all peak-size windows. */
 if(occ%29==0||size==163840){assert(cache18_update(&cache,idx,len,bytes/2048,x,z,read63,0));int current[CAP18];assert(snap63(current)==n&&!memcmp(current,ids,n*sizeof(int)));assert(cache.used_bytes==size);loads++;}}
 assert(occ==8914&&peak==163840&&cap==19);assert(ARENA22==192*1024);int old[CAP18],n=snap63(old);int ax=cache.ax,az=cache.az;bad=1;assert(!cache18_update(&cache,idx,len,bytes/2048,10645,19103,read63,0));int check[CAP18];assert(snap63(check)==n&&!memcmp(check,old,n*sizeof(int))&&cache.ax==ax&&cache.az==az);bad=0;assert(cache18_update(&cache,idx,len,bytes/2048,10645,19103,read63,0));assert(cache18_floor(&cache,10645,19103,-603,110)==-603);printf("%d occupied anchors, peak %d bytes / %d blocks, %d actual cache transitions, read failure rollback and retry passed\n",occ,peak,cap,loads);free(disk);return 0;}
