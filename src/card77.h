#ifndef ETD_CARD77_H
#define ETD_CARD77_H
#include "session_journal76.h"
/* BIOS synchronous file backend. No format, erase, create or raw directory writes.
 * Provision a dedicated card offline. Caller owns SIO/BIOS scheduling. */
#define MC77_BYTES (6u*8192u)
#define MC77_RESERVED 3u
#define MC77_OWNER 0x37374445u /* ED77 */
#define MC77_SCHEMA 1u
static const char *const mc77_paths[2]={"bu00:ETDPSX77-SAVE-A","bu00:ETDPSX77-SAVE-B"};
typedef struct {char name[20];U72 attr,size,next,first,reserved;} Mc77Dir;
typedef struct {void*ctx;int(*stat)(void*,const char*,Mc77Dir*);int(*open)(void*,const char*,int);int(*seek)(void*,int,int);int(*read)(void*,int,B72*,int);int(*write)(void*,int,const B72*,int);int(*close)(void*,int);} Mc77Ops;
typedef struct {const Mc77Ops*ops;int fd[2];U72 token[2];int mounted,failed,writable;} Mc77;
static int mc77_equal(const char*a,const char*b){while(*b){if(*a++!=*b++)return 0;}return !*a;}
static int mc77_xfer(Mc77*m,unsigned copy,unsigned frame,B72*p,int writing){if(copy>=2||frame>=MC77_BYTES/128||m->fd[copy]<0)return 0;const Mc77Ops*o=m->ops;int pos=(int)(frame*128);if(o->seek(o->ctx,m->fd[copy],pos)!=pos)return 0;return (writing?o->write(o->ctx,m->fd[copy],p,128):o->read(o->ctx,m->fd[copy],p,128))==128;}
static int mc77_close(Mc77*m){int ok=1;for(unsigned i=0;i<2;i++){if(m->fd[i]>=0&&m->ops->close(m->ops->ctx,m->fd[i])!=m->fd[i])ok=0;m->fd[i]=-1;}m->mounted=0;return ok;}
static int mc77_marker(Mc77*m,unsigned c,U72*t){B72 p[128];if(!mc77_xfer(m,c,2,p,0)||le72(p)!=MC77_OWNER||le72(p+4)!=MC77_SCHEMA||le72(p+8)!=c||crc72(p,20)!=le72(p+20))return 0;t[0]=le72(p+12);t[1]=le72(p+16);return t[0]||t[1];}
static int mc77_mount(Mc77*m,const Mc77Ops*o,int writable){m->ops=o;m->fd[0]=m->fd[1]=-1;m->mounted=m->failed=0;m->writable=!!writable;if(!o||!o->stat||!o->open||!o->seek||!o->read||!o->close||(writable&&!o->write))return 0;for(unsigned c=0;c<2;c++){Mc77Dir d;B72 p[128];U72 t[2];j76_zero((B72*)&d,sizeof d);if(!o->stat(o->ctx,mc77_paths[c],&d)||d.attr!=0x50||d.size!=MC77_BYTES||!mc77_equal(d.name,mc77_paths[c]+5))goto fail;m->fd[c]=o->open(o->ctx,mc77_paths[c],writable?3:1);if(m->fd[c]<0||!mc77_xfer(m,c,0,p,0)||p[0]!='S'||p[1]!='C'||p[2]!=0x11||p[3]!=6||!mc77_marker(m,c,t))goto fail;if(c&&(t[0]!=m->token[0]||t[1]!=m->token[1]))goto fail;m->token[0]=t[0];m->token[1]=t[1];}m->mounted=1;return 1;fail:mc77_close(m);return 0;}
static int mc77_check(Mc77*m,unsigned c){U72 t[2];return mc77_marker(m,c,t)&&t[0]==m->token[0]&&t[1]==m->token[1];}
static int mc77_read(void*ctx,U72 f,B72*p){Mc77*m=ctx;if(!m->mounted||m->failed||f>=2*J76_COPY||f%J76_COPY>=J76_FRAMES)return 0;unsigned c=f/J76_COPY;if((f%J76_COPY==0&&!mc77_check(m,c))||!mc77_xfer(m,c,MC77_RESERVED+f%J76_COPY,p,0)){m->failed=1;return 0;}return 1;}
static int mc77_write(void*ctx,U72 f,const B72*p){Mc77*m=ctx;if(!m->mounted||m->failed||!m->writable||f>=2*J76_COPY||f%J76_COPY>=J76_FRAMES)return 0;unsigned c=f/J76_COPY;/* Recheck ownership before invalidation and commit. BIOS must reject card change during payload writes. */if((f%J76_COPY==0&&!mc77_check(m,c))||!mc77_xfer(m,c,MC77_RESERVED+f%J76_COPY,(B72*)p,1)){m->failed=1;return 0;}return 1;}
static Journal76 mc77_journal(Mc77*m){Journal76 j={m,mc77_read,mc77_write};return j;}
/* Do not overwrite a pair of corrupt nonempty headers without explicit recovery. */
static int mc77_save(Mc77*m,const Session72*live,Session72*scratch){if(!m->mounted||!m->writable||m->failed||!live||!scratch||live==scratch)return 0;Journal76 j=mc77_journal(m);J76Meta meta;int selected=j76_select(&j,scratch,&meta);if(selected==-2)return 0;if(selected==-1){B72 p[128];for(unsigned c=0;c<2;c++){if(!mc77_read(m,c*J76_COPY,p))return 0;for(unsigned i=0;i<128;i++)if(p[i])return 0;}}return j76_save(&j,live,scratch);}
static int mc77_load(Mc77*m,Session72*live,Session72*scratch,U72*world){if(!m->mounted||m->failed)return 0;Journal76 j=mc77_journal(m);return j76_load(&j,live,scratch,world);}
#endif
