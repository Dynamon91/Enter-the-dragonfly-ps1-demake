#include "scene52.h"
typedef S52Byte U8;typedef S52Word U32;
#include "progress33.h"
#include "texture54.h"
static U32 rd16(const U8*p){return p[0]|(U32)p[1]<<8;}
static U32 rd32(const U8*p){return rd16(p)|rd16(p+2)<<16;}
static void cp(void*d,const void*s,U32 n){volatile U8*a=d;const volatile U8*b=s;while(n--)*a++=*b++;}
static U32 crc(const U8*p,U32 n){U32 c=~0u;while(n--){c^=*p++;for(int i=0;i<8;i++)c=(c>>1)^(0xedb88320u&-(c&1));}return ~c;}
static const U8* entry(const Texture54*t,int g){U32 lo=0,hi=(t->len-12)/12;while(lo<hi){U32 m=lo+(hi-lo)/2;const U8*e=t->idx+12+12*m;U32 k=rd32(e);if(k==(U32)g)return e;if(k<(U32)g)lo=m+1;else hi=m;}return 0;}
int texture54_validate(const Texture54*t){
 if(!t||!t->idx||!t->material_groups||!t->materials||t->materials>65536||t->len<12||t->len>12+12*TEX54_GROUPS||(t->len-12)%12||rd32(t->idx)!=0x49545445u||rd16(t->idx+4)!=1||rd16(t->idx+6)!=12)return 0;
 U32 n=(t->len-12)/12;if(rd32(t->idx+8)!=n||t->sectors!=n*3)return 0;
 int last=-1;for(U32 i=0;i<n;i++){const U8*e=t->idx+12+i*12;U32 g=rd32(e);if(g>=TEX54_GROUPS||(int)g<=last||rd32(e+4)!=i*3)return 0;last=(int)g;}
 for(U32 i=0;i<t->materials;i++){int g=t->material_groups[i];if(g< -1||g>=(int)TEX54_GROUPS||(g>=0&&!entry(t,g)))return 0;}
 return 1;
}
static int block(const U8*p,const U8*e){return rd32(p)==0x54445445u&&rd16(p+4)==1&&rd16(p+6)==rd32(e)&&rd32(p+8)>0&&rd32(p+8)<=1024&&rd32(p+12)>0&&rd32(p+12)<=1024&&rd32(p+16)==TEX54_PAYLOAD&&rd32(p+20)==rd32(e+8)&&crc(p+24,TEX54_PAYLOAD)==rd32(e+8);}
/* Use the unused tail of the newly loaded terrain arena. No third arena or
 * persistent texture staging allocation. Never overwrite active scene VRAM
 * before all needed textures are verified. Group IDs are scene-local. */
int transition54(Cache52*c,Progress33*p,TextureState54*state,const Scene52*s,const Texture54*t,const Spawn53*spawn,int completion,S52Read terrain,void*tc,S52Read tex,void*xc,U8*scratch,Upload54 upload,void*uc,Spawn53*out){
 if(!c||!p||!state||!s||!t||!spawn||!terrain||!tex||!scratch||!upload||!out)return PORTAL53_BAD_STATE;
 if(!texture54_validate(t)||t->materials!=s->materials)return TEX54_BAD_BANK;
 Cache52 staged;Progress33 progress;Spawn53 arrival;cp(&staged,c,sizeof staged);cp(&progress,p,sizeof progress);
 int e=portal53_enter(&staged,&progress,s,spawn,completion,terrain,tc,&arrival);if(e)return e;
 const Page52*page=&staged.pages[staged.active];U8*arena=staged.buf[staged.active];TextureState54 next;
 next.count=0;next.level=(int)s->level;for(U32 i=0;i<TEX54_GROUPS;i++)next.map[i]=-1;for(U32 i=0;i<TEX54_SLOTS;i++)next.slots[i]=-1;
 for(U32 k=0;k<page->count;k++){
  const U8*q=arena+page->offset[k]+64;
  for(U32 j=0;j<page->meta[k][1];j++,q+=36){int g=t->material_groups[rd16(q+30)];if(g<0||next.map[g]>=0)continue;
   if(next.count==TEX54_SLOTS)return TEX54_BUDGET;
   next.map[g]=(short)next.count;next.slots[next.count++]=(short)g;
  }
 }
 if(page->bytes>SCENE52_BYTES||next.count>(SCENE52_BYTES-page->bytes)/TEX54_PAYLOAD)return TEX54_BUDGET;
 U8*payload=arena+page->bytes;
 for(U32 i=0;i<next.count;i++){
  const U8*ent=entry(t,next.slots[i]);if(!ent||!tex(xc,rd32(ent+4),3,scratch)||!block(scratch,ent))return TEX54_READ_FAILED;
  cp(payload+i*TEX54_PAYLOAD,scratch+24,TEX54_PAYLOAD);
 }
 /* Commit boundary: caller guarantees GPU stopped and synchronous upload.
  * No operation after the first upload is allowed to fail. */
 for(U32 i=0;i<next.count;i++)upload(uc,(int)i,payload+i*TEX54_PAYLOAD);
 cp(c,&staged,sizeof staged);cp(p,&progress,sizeof progress);cp(state,&next,sizeof next);cp(out,&arrival,sizeof arrival);return PORTAL53_OK;
}
