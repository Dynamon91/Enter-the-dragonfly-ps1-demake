#ifndef LOADER_SAVE78_H
#define LOADER_SAVE78_H
#include <stdint.h>
#include "card77.h"
#include "volume78.h"
/* Selector-only scratch; never use with an active overlay or outstanding DMA. */
typedef struct {Session72 candidate,work;B72 sector[2048];} LoaderScratch78;
#define SCRATCH78_ADDR WORLD72_LOAD
#define SCRATCH78 ((LoaderScratch78*)SCRATCH78_ADDR)
typedef enum {L78_OK=1,L78_BUSY=-1,L78_BAD_STATE=-2,L78_CARD=-3,L78_IO=-4,L78_INCOMPATIBLE=-5,L78_DISC=-6,L78_RESTORE_IO=-7} Status78;
typedef struct {void*ctx;int(*enter)(void*);int(*leave)(void*);const Mc77Ops*card;const Disc78*disc;const Volume78*volumes;const U72*sizes;U72 profile[2];} LoaderIo78;
#define PROFILE78_MAGIC 0x38374445u
static int profile78(Mc77*m,const LoaderIo78*io){B72 p[128];if(!(io->profile[0]||io->profile[1]))return 0;for(unsigned c=0;c<2;c++)if(!mc77_xfer(m,c,2,p,0)||le72(p+24)!=PROFILE78_MAGIC||le72(p+28)!=io->profile[0]||le72(p+32)!=io->profile[1]||crc72(p,36)!=le72(p+36))return 0;return 1;}
static int compatible78(const Session72*s,const U72*sizes){if(!sizes||!j76_session_ok(s))return 0;for(U72 w=0;w<LEVEL72_COUNT;w++){U72 n=s->slot[w].size;if(sizes[w]>SLOT72_SIZE||(n&&n!=sizes[w]))return 0;}return 1;}
static int separate78(const Session72*s,const LoaderScratch78*w){uintptr_t a=(uintptr_t)s,b=(uintptr_t)w;return a<=b?b-a>=sizeof *s:a-b>=sizeof *w;}
static int gate78(int menu,const LoaderIo78*io,const Session72*s,LoaderScratch78*w){return menu&&s&&w&&io&&io->card&&io->enter&&io->leave&&separate78(s,w)&&s->magic==SESSION72_MAGIC&&!s->requested&&!s->arrival;}
static Status78 loader_save78(int menu,const LoaderIo78*io,Session72*s,LoaderScratch78*w){if(!gate78(menu,io,s,w))return L78_BUSY;if(!compatible78(s,io->sizes))return L78_BAD_STATE;if(!io->enter(io->ctx))return L78_RESTORE_IO;Mc77 m;Status78 rc=L78_CARD;if(mc77_mount(&m,io->card,1)){rc=!profile78(&m,io)?L78_INCOMPATIBLE:mc77_save(&m,s,&w->work)?L78_OK:L78_IO;if(!mc77_close(&m))rc=L78_IO;}if(!io->leave(io->ctx))return L78_RESTORE_IO;return rc;}
/* Publish saved slots only after successful read, close, lifecycle restore and
 * executable preflight. Actual transfer remains the resident loader's job. */
static Status78 loader_restore78(int menu,const LoaderIo78*io,Session72*s,LoaderScratch78*w){if(!gate78(menu,io,s,w))return L78_BUSY;if(!io->disc||!io->volumes||!io->sizes)return L78_BAD_STATE;if(!io->enter(io->ctx))return L78_RESTORE_IO;Mc77 m;Status78 rc=L78_CARD;U72 world=99;clear72(&w->candidate);if(mc77_mount(&m,io->card,0)){rc=!profile78(&m,io)?L78_INCOMPATIBLE:mc77_load(&m,&w->candidate,&w->work,&world)?L78_OK:L78_IO;if(!mc77_close(&m))rc=L78_IO;}if(!io->leave(io->ctx))return L78_RESTORE_IO;if(rc!=L78_OK)return rc;w->candidate.world=world;if(!compatible78(&w->candidate,io->sizes))return L78_INCOMPATIBLE;Extent78 e;if(!probe78(io->disc,io->volumes+world,w->sector,&e))return L78_DISC;
 for(U72 i=0;i<LEVEL72_COUNT;i++)s->slot[i]=w->candidate.slot[i];s->visited=w->candidate.visited;s->arrival=0;s->requested=world+1;return L78_OK;}
#endif
