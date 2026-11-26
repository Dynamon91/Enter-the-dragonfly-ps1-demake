/* Additive campaign allocation/Atlas over the v0.38 route and v0.33 ledger.
 * Include after progress33.h and workprint38.h. No dynamic allocations or I/O. */
#ifndef CAMPAIGN39_H
#define CAMPAIGN39_H
#define WP39_WRONG_SCENE 10
#define WP39_DUPLICATE 11
#define WP39_RIPTO_GATE 12
/* Project IDs; reserve Dojo 0..9 to retain the active IDs 0,1,2,3. */
typedef struct { U8 first, count; } WpRange39;
static const WpRange39 wp_slots39[30]={
 {10,10},{0,10},{20,10},{30,10},{40,10},{50,10},{60,10},{70,10},{80,10},
 {90,2},{92,2},{94,2},{96,2},{98,2},{100,2},{102,1},{103,2},{105,1},
 {106,1},{107,1},{108,1},{109,1},{110,2},{112,1},{113,1},{114,1},{115,2},
 {117,1},{118,1},{119,1}
};
static const U8 wp_original_gates39[9]={0,1,6,15,25,35,45,55,65};
static int wp_owner39(int slot){
 if(slot<0||slot>=EXPANDED33)return -1;
 for(int i=0;i<WP38_LEVELS;i++)if(slot>=wp_slots39[i].first&&slot<wp_slots39[i].first+wp_slots39[i].count)return i;
 return -1;
}
/* Atlas returns 0 for unavailable mode or invalid ID; no ownership duplication. */
static int wp_atlas39(const Progress33*p,int level,U8*found,U8*total){
 *found=*total=0;
 if(level<0||level>=WP38_LEVELS||(!p->mode&&level>8))return 0;
 WpRange39 a=wp_slots39[level];*total=a.count;
 for(int i=0;i<a.count;i++)if(progress_has33(p,a.first+i))++*found;
 return 1;
}
/* ripto_ready is supplied by the future Classic completion/phase controller.
 * Never infer the released fight's completion requirement from dragonflies alone. */
static int wp_check39(const Progress33*p,const WpReady38*a,int kind,int id,int ripto_ready){
 int e=wp_check38(p,a,kind,id);if(e!=WP38_OK&&e!=WP38_MISSING)return e;
 if(kind==WP38_LEVEL&&id<9&&p->count<wp_original_gates39[id])return WP38_GATE;
 if(!p->mode&&kind==WP38_BOSS&&id==2&&!ripto_ready)return WP39_RIPTO_GATE;
 return e;
}
static int wp_init39(WpRoute38*r,Progress33*p,const WpReady38*a,int level){
 int e=wp_check39(p,a,WP38_LEVEL,level,0);return e?e:wp_init38(r,p,a,level);
}
static int wp_request39(WpRoute38*r,const Progress33*p,const WpReady38*a,int kind,int id,int ripto_ready){
 if(r->pending)return WP38_BUSY;
 int e=wp_check39(p,a,kind,id,ripto_ready);return e?e:wp_request38(r,p,a,kind,id);
}
static int wp_finish39(WpRoute38*r,Progress33*p,const WpReady38*a,int loaded,int ripto_ready){
 if(!r->pending)return WP38_NO_PENDING;
 if(!loaded)return wp_finish38(r,p,a,0);
 int e=wp_check39(p,a,r->pending_kind,r->pending_id,ripto_ready);
 if(e){r->pending=0;return e;}
 return wp_finish38(r,p,a,1);
}
/* Caller must verify a genuine bubble hit / quest reward / minigame completion.
 * Does not replace old v0.37 call sites until integrated with the scene loader. */
static int wp_collect39(const WpRoute38*r,Progress33*p,int slot){
 int owner=wp_owner39(slot);if(owner<0)return WP38_INVALID;
 if(!p->mode&&slot>=CLASSIC33)return WP38_MODE;
 if(r->pending)return WP38_BUSY;
 if(r->current_kind!=WP38_LEVEL||r->current_id!=owner)return WP39_WRONG_SCENE;
 if(progress_has33(p,slot))return WP39_DUPLICATE;
 return progress_take33(p,slot)?WP38_OK:WP38_INVALID;
}
#endif
