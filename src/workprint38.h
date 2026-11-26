/* Workprint routing, project IDs from campaign33.json. Include after progress33.h.
 * No hardware I/O: caller stages/validates a bank, then commits or cancels.
 * Expanded gates are provisional fan design; Classic thresholds are not reconstructed. */
#ifndef WORKPRINT38_H
#define WORKPRINT38_H
#define WP38_LEVELS 30
#define WP38_BOSSES 5
#define WP38_LEVEL 0
#define WP38_BOSS 1
#define WP38_OK 0
#define WP38_INVALID 1
#define WP38_MODE 2
#define WP38_GATE 3
#define WP38_MISSING 4
#define WP38_BUSY 5
#define WP38_NO_PENDING 6
#define WP38_LOAD_FAILED 7
#define WP38_NOT_IN_BOSS 8
#define WP38_ALREADY_WON 9
/* A readiness bit must represent a validated loadable pack, not a registry entry. */
typedef struct {U32 levels; U8 bosses;} WpReady38;
typedef struct {U8 current_kind,current_id,return_level,pending_kind,pending_id,pending;} WpRoute38;
typedef struct {U8 flies,bosses;} WpGate38;
static const WpGate38 wp_level_gates38[WP38_LEVELS]={
 {0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},
 {12,0},{36,1},{64,3},{12,0},{12,0},{12,0},{12,0},
 {36,1},{36,1},{36,1},{64,3},{64,3},{64,3},
 {90,7},{90,7},{90,7},{90,7},{100,15},{12,0},{36,1},{64,3}
};
static const WpGate38 wp_boss_gates38[WP38_BOSSES]={{30,0},{60,1},{80,3},{95,7},{110,15}};
static int wp_check38(const Progress33*p,const WpReady38*a,int kind,int id){
 WpGate38 g;
 if(kind==WP38_LEVEL){if(id<0||id>=WP38_LEVELS)return WP38_INVALID;if(!p->mode&&id>8)return WP38_MODE;g=wp_level_gates38[id];}
 else if(kind==WP38_BOSS){if(id<0||id>=WP38_BOSSES)return WP38_INVALID;if(!p->mode&&id!=2)return WP38_MODE;g=wp_boss_gates38[id];}
 else return WP38_INVALID;
 if(p->mode&&(p->count<g.flies||(p->bosses&g.bosses)!=g.bosses))return WP38_GATE;
 if(kind==WP38_LEVEL?!(a->levels&(1u<<id)):!(a->bosses&(1u<<id)))return WP38_MISSING;
 return WP38_OK;
}
static int wp_init38(WpRoute38*r,Progress33*p,const WpReady38*a,int level){
 int e=wp_check38(p,a,WP38_LEVEL,level);if(e)return e;
 *r=(WpRoute38){WP38_LEVEL,(U8)level,(U8)level,0,0,0};progress_visit33(p,level);return WP38_OK;
}
static int wp_request38(WpRoute38*r,const Progress33*p,const WpReady38*a,int kind,int id){
 if(r->pending)return WP38_BUSY;
 int e=wp_check38(p,a,kind,id);if(e)return e;
 r->pending_kind=(U8)kind;r->pending_id=(U8)id;r->pending=1;return WP38_OK;
}
static int wp_finish38(WpRoute38*r,Progress33*p,const WpReady38*a,int loaded){
 if(!r->pending)return WP38_NO_PENDING;
 int kind=r->pending_kind,id=r->pending_id;r->pending=0;
 if(!loaded)return WP38_LOAD_FAILED;
 int e=wp_check38(p,a,kind,id);if(e)return e;
 if(r->current_kind==WP38_LEVEL)r->return_level=r->current_id;
 r->current_kind=(U8)kind;r->current_id=(U8)id;
 if(kind==WP38_LEVEL)progress_visit33(p,id);
 return WP38_OK;
}
/* Call only after combat reports a genuine defeat; entering an arena never awards it. */
static int wp_defeat38(WpRoute38*r,Progress33*p){
 if(r->pending)return WP38_BUSY;
 if(r->current_kind!=WP38_BOSS)return WP38_NOT_IN_BOSS;
 return progress_boss33(p,r->current_id)?WP38_OK:WP38_ALREADY_WON;
}
static int wp_return38(WpRoute38*r,const Progress33*p,const WpReady38*a){
 if(r->current_kind!=WP38_BOSS)return WP38_NOT_IN_BOSS;
 return wp_request38(r,p,a,WP38_LEVEL,r->return_level);
}
#endif
