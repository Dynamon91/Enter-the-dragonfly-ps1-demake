#ifndef SESSION_JOURNAL76_H
#define SESSION_JOURNAL76_H
#include "session72.h"
/* Logical save journal, not a memory-card filesystem driver. Caller owns two
 * 384-frame regions and a nonoverlapping 41148-byte Session72 scratch buffer.
 * Call only with gameplay paused and current overlay snapshot committed. */
#define J76_FRAME 128u
#define J76_COPY 384u
#define J76_SLOT 33u
#define J76_MAGIC 0x4a445445u
#define J76_SCHEMA 1u
#define J76_FRAMES (1u+LEVEL72_COUNT*J76_SLOT)
/* I/O: 1 success, 0 failure. A failed read is never treated as an empty card. */
typedef int (*J76Read)(void*,U72,B72*);
typedef int (*J76Write)(void*,U72,const B72*);
typedef struct {void*ctx;J76Read read;J76Write write;} Journal76;
typedef struct {U72 seq,world,visited,crc;} J76Meta;
static void j76_put(B72*p,U72 v){for(U72 i=0;i<4;i++)p[i]=(B72)(v>>(8*i));}
static void j76_zero(B72*p,U72 n){for(U72 i=0;i<n;i++)p[i]=0;}
static U72 j76_crc(U72 c,const B72*p,U72 n){while(n--){c^=*p++;for(unsigned j=0;j<8;j++)c=(c>>1)^(0xedb88320u&-(c&1u));}return c;}
static int j76_later(U72 a,U72 b){U72 d=a-b;return d&&d<0x80000000u;}
static int j76_session_ok(const Session72*s){if(s->magic!=SESSION72_MAGIC||s->world>=LEVEL72_COUNT||(s->visited>>LEVEL72_COUNT))return 0;U72 n=0;for(U72 w=0;w<LEVEL72_COUNT;w++){const Slot72*t=s->slot+w;if(t->size){if(!valid72(t))return 0;n+=t->flies;}}return n<=90;}
static void j76_pack(const Slot72*s,U72 frame,B72*p){j76_zero(p,J76_FRAME);if(!s->size)return;if(!frame){j76_put(p,s->size);j76_put(p+4,s->crc);j76_put(p+8,s->gems);j76_put(p+12,s->flies);}U72 start=frame*J76_FRAME;for(U72 i=0;i<J76_FRAME;i++){U72 k=start+i;if(k>=16&&k-16<s->size)p[i]=s->bytes[k-16];}}
/* 1 valid, 0 invalid/uncommitted, -1 I/O failure. Scratch may be modified. */
static int j76_readcopy(const Journal76*j,U72 copy,Session72*s,J76Meta*m){B72 p[J76_FRAME];U72 base=copy*J76_COPY;if(!j->read(j->ctx,base,p))return -1;if(le72(p)!=J76_MAGIC||le72(p+4)!=J76_SCHEMA||le72(p+24)!=J76_FRAMES||crc72(p,28)!=le72(p+28))return 0;
 m->seq=le72(p+8);m->world=le72(p+12);m->visited=le72(p+16);m->crc=le72(p+20);if(m->world>=LEVEL72_COUNT||(m->visited>>LEVEL72_COUNT))return 0;clear72(s);s->world=m->world;s->visited=m->visited;U72 crc=~0u;
 for(U72 w=0;w<LEVEL72_COUNT;w++){Slot72*t=s->slot+w;for(U72 f=0;f<J76_SLOT;f++){if(!j->read(j->ctx,base+1+w*J76_SLOT+f,p))return -1;crc=j76_crc(crc,p,J76_FRAME);if(!f){t->size=le72(p);t->crc=le72(p+4);t->gems=le72(p+8);t->flies=le72(p+12);if(t->size>SLOT72_SIZE||(!t->size&&(t->crc||t->gems||t->flies)))return 0;}for(U72 i=0;i<J76_FRAME;i++){U72 k=f*J76_FRAME+i;if(k>=16&&k-16<t->size)t->bytes[k-16]=p[i];else if(k>=16&&p[i])return 0;}}}
 return (~crc==m->crc&&j76_session_ok(s))?1:0;
}
/* Return newest valid copy index, -1 if none, -2 on I/O/ambiguous sequence. */
static int j76_select(const Journal76*j,Session72*scratch,J76Meta*m){J76Meta a,b;int x=j76_readcopy(j,0,scratch,&a),y=j76_readcopy(j,1,scratch,&b);if(x<0||y<0)return -2;if(!x&&!y)return -1;if(x&&y){U72 d=a.seq-b.seq;if(!d||d==0x80000000u)return -2;}if(x&&(!y||j76_later(a.seq,b.seq))){*m=a;return 0;}*m=b;return 1;}
/* Atomic live-state publication: never import CD offsets or pending requests.
 * Return saved world via outworld; loader must open it and re-establish CD base. */
static int j76_load(const Journal76*j,Session72*live,Session72*scratch,U72*outworld){if(!j||!j->read||!live||!scratch||live==scratch||!outworld||live->magic!=SESSION72_MAGIC)return 0;J76Meta m;int a=j76_select(j,scratch,&m);if(a<0)return 0;J76Meta v;if(j76_readcopy(j,(U72)a,scratch,&v)!=1||v.seq!=m.seq||v.crc!=m.crc||v.world!=m.world||v.visited!=m.visited)return 0;for(U72 w=0;w<LEVEL72_COUNT;w++)live->slot[w]=scratch->slot[w];live->visited=scratch->visited;live->requested=live->arrival=0;*outworld=v.world;return 1;}
/* Commit inactive copy: invalidate header, write payload, write header last,
 * then verify by readback. Caller must serialize access to the storage. */
static int j76_save(const Journal76*j,const Session72*live,Session72*scratch){if(!j||!j->read||!j->write||!live||!scratch||live==scratch||!j76_session_ok(live))return 0;J76Meta m;int a=j76_select(j,scratch,&m);if(a==-2)return 0;U72 copy=a<0?0u:1u-(U72)a,seq=a<0?1u:m.seq+1u,base=copy*J76_COPY;B72 p[J76_FRAME];j76_zero(p,J76_FRAME);if(!j->write(j->ctx,base,p))return 0;U72 crc=~0u;for(U72 w=0;w<LEVEL72_COUNT;w++)for(U72 f=0;f<J76_SLOT;f++){j76_pack(live->slot+w,f,p);crc=j76_crc(crc,p,J76_FRAME);if(!j->write(j->ctx,base+1+w*J76_SLOT+f,p))return 0;}j76_zero(p,J76_FRAME);j76_put(p,J76_MAGIC);j76_put(p+4,J76_SCHEMA);j76_put(p+8,seq);j76_put(p+12,live->world);j76_put(p+16,live->visited);j76_put(p+20,~crc);j76_put(p+24,J76_FRAMES);j76_put(p+28,crc72(p,28));if(!j->write(j->ctx,base,p))return 0;J76Meta v;return j76_readcopy(j,copy,scratch,&v)==1&&v.seq==seq&&v.crc==~crc&&v.world==live->world&&v.visited==live->visited;}
#endif
