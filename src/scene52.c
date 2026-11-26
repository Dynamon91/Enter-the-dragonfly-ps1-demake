#include "scene52.h"
extern int sector16_load(const S52Byte*,S52Word,S52Word,S52Word,S52Word,S52Word,S52Word,S52Byte*,S52Word,S52Read,void*,S52Word*);
static S52Word r16(const S52Byte*p){return (S52Word)p[0]|(S52Word)p[1]<<8;}
static S52Word r32(const S52Byte*p){return r16(p)|r16(p+2)<<16;}
static int signed32(S52Word x){return x<=0x7fffffffu?(int)x:-1-(int)(~x);}
static int bounded(int x){return x>=-200000&&x<=200000;}
static int anchor(int x){return (x>=0?x/512:-((-x+511)/512))*512+256;}
/* Index must be immutable until the last active reference is released. */
int scene52_open(Scene52*out,const S52Byte*idx,S52Word len,S52Word sectors,S52Word materials,S52Word level){
 if(!out||!idx||len<16||len>SCENE52_INDEX||level>9||!materials||materials>65536||!sectors||r32(idx)!=0x49445445u||r16(idx+4)!=1||r16(idx+6)!=60||r32(idx+12)!=2048)return 0;
 S52Word n=r32(idx+8),lba=0,nr=0,nc=0,no=0;if(!n||n!=(len-16)/60||(len-16)%60)return 0;
 for(S52Word i=0;i<n;i++){
  const S52Byte*e=idx+16+i*60;S52Word size=r32(e+8),r=r16(e+52),c=r16(e+54),o=r16(e+56);
  if(r32(e)!=i||r32(e+4)!=lba||size<64||size>65536||size!=64+r*36+c*24+o*16||size==64||r16(e+58))return 0;
  S52Word span=(size+2047)/2048;if(lba>sectors||span>sectors-lba)return 0;lba+=span;nr+=r;nc+=c;no+=o;
  for(int j=0;j<3;j++){int org=signed32(r32(e+16+4*j)),lo=signed32(r32(e+28+4*j)),hi=signed32(r32(e+40+4*j));if(!bounded(org)||!bounded(lo)||!bounded(hi)||lo>hi||lo-org< -32768||hi-org>32767)return 0;}
 }
 if(lba!=sectors||!nr||!nc)return 0;
 out->idx=idx;out->len=len;out->sectors=sectors;out->materials=materials;out->render=nr;out->collision=nc;out->objects=no;out->blocks=n;out->level=level;return 1;
}
/* The caller supplies two distinct, nonoverlapping, 460 KiB buffers. */
int scene52_init(Cache52*c,S52Byte*a,S52Byte*b){
 if(!c||!a||!b)return 0;
 __UINTPTR_TYPE__ aa=(__UINTPTR_TYPE__)a,bb=(__UINTPTR_TYPE__)b;
 if((aa>bb?aa-bb:bb-aa)<SCENE52_BYTES)return 0;
 c->buf[0]=a;c->buf[1]=b;c->active=-1;return 1;
}
/* Preflight all neighborhood sizes before issuing a read. Failed reads cannot
 * overwrite the live page or publish a partial scene. Synchronous prototype. */
int scene52_switch(Cache52*c,const Scene52*s,int x,int z,S52Read read,void*ctx){
 if(!c||!s||!read||!bounded(x)||!bounded(z)||c->active< -1||c->active>1)return 0;
 Scene52 checked;if(!scene52_open(&checked,s->idx,s->len,s->sectors,s->materials,s->level))return 0;
 int slot=c->active==0?1:0;Page52*p=c->pages+slot;S52Word n=0,used=0;int ax=anchor(x),az=anchor(z);
 for(S52Word i=0;i<checked.blocks;i++){
  const S52Byte*e=checked.idx+16+i*60;
  if(signed32(r32(e+28))>ax+1792||signed32(r32(e+40))<ax-1792||signed32(r32(e+36))>az+1792||signed32(r32(e+48))<az-1792)continue;
  S52Word bytes=(r32(e+8)+2047)&~2047u;if(n>=SCENE52_CAP||bytes>SCENE52_BYTES-used)return 0;
  p->id[n]=i;p->offset[n++]=used;used+=bytes;
 }
 if(!n)return 0;
 for(S52Word i=0;i<n;i++){
  S52Word cap=(i+1<n?p->offset[i+1]:used)-p->offset[i];
  if(!sector16_load(checked.idx,checked.len,p->id[i],checked.sectors,checked.materials,checked.render,checked.collision,c->buf[slot]+p->offset[i],cap,read,ctx,p->meta[i]))return 0;
 }
 p->count=n;p->bytes=used;c->scene[slot]=checked;c->active=slot;return 1;
}
