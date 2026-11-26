/* Session ledger: slots 0..89 shared, 90..119 expansion-only. Project IDs. */
#define CLASSIC33 90
#define EXPANDED33 120
#define LEVELCAP33 32
#define BOSSCAP33 5
typedef struct {U8 caught[15];U8 mode,count,bosses;U32 visited;} Progress33;
static void progress_reset33(Progress33*p,int mode){for(int i=0;i<15;i++)p->caught[i]=0;p->mode=!!mode;p->count=p->bosses=0;p->visited=0;}
static int progress_has33(const Progress33*p,int slot){return slot>=0&&slot<EXPANDED33&&(p->caught[slot>>3]&(1u<<(slot&7)));}
static int progress_take33(Progress33*p,int slot){if(slot<0||slot>=(p->mode?EXPANDED33:CLASSIC33)||progress_has33(p,slot))return 0;p->caught[slot>>3]|=1u<<(slot&7);p->count++;return 1;}
static int progress_visit33(Progress33*p,int level){if(level<0||level>=LEVELCAP33||(!p->mode&&level>8))return 0;p->visited|=1u<<level;return 1;}
/* Boss IDs are separate from level IDs. Classic permits only released Ripto. */
static int progress_boss33(Progress33*p,int boss){if(boss<0||boss>=BOSSCAP33||(!p->mode&&boss!=2)||(p->bosses&(1u<<boss)))return 0;p->bosses|=1u<<boss;return 1;}
