#ifndef SESSION43_H
#define SESSION43_H
/* Expanded-only campaign lab: all ready bits refer to synthetic rooms, not recovered assets. */
#include "arena41.h"
typedef unsigned char U8;typedef unsigned int U32;
#include "progress33.h"
#include "workprint38.h"
#include "campaign39.h"
enum { S43_NEXT=128,S43_PREV=256,S43_ENTER=512,S43_RETRY=1024,S43_EXIT=2048 };
typedef struct {Progress33 p;WpRoute38 route;Arena41 a;int selection,error,prev,delay;} Session43;
static const WpReady38 ready43={0x3fffffffu,31};
static void spot43(int l,int i,int*x,int*y){*x=40+((i*3+l)%5)*60;*y=74+((i/5+l)%2)*66;}
static void room43(Session43*s){arena_init41(&s->a,0,s->p.bosses);s->a.bx=s->a.by=0;s->delay=0;}
static void init43(Session43*s){*s=(Session43){0};progress_reset33(&s->p,1);wp_init39(&s->route,&s->p,&ready43,0);room43(s);s->selection=1;}
static int eligible43(const Session43*s,int n){if(n<0||n>=35)return WP38_INVALID;return wp_check39(&s->p,&ready43,n>=30,n>=30?n-30:n,0);}
static void enter43(Session43*s){int n=s->selection,k=n>=30,id=k?n-30:n;s->error=wp_request39(&s->route,&s->p,&ready43,k,id,0);if(s->error)return;s->error=wp_finish39(&s->route,&s->p,&ready43,1,0);if(s->error)return;if(k)arena_init41(&s->a,id,s->p.bosses);else room43(s);}
static void step43(Session43*s,int keys){int edge=keys&~s->prev;s->prev=keys;Arena41*a=&s->a;
 if(s->route.current_kind==WP38_BOSS){if(edge&S43_RETRY)arena_init41(a,s->route.current_id,s->p.bosses);else if((edge&S43_EXIT)||((edge&S43_ENTER)&&a->state==A41_WIN)){s->error=wp_return38(&s->route,&s->p,&ready43);if(!s->error)s->error=wp_finish39(&s->route,&s->p,&ready43,1,0);if(!s->error)room43(s);return;}step41(a,keys&127);if(a->state==A41_WIN&&!(s->p.bosses&(1u<<a->id)))s->error=wp_defeat38(&s->route,&s->p);return;}
 if(edge&S43_NEXT){s->selection=(s->selection+1)%35;s->error=0;}if(edge&S43_PREV){s->selection=(s->selection+34)%35;s->error=0;}
 if(edge&S43_ENTER){enter43(s);return;}
 int dx=!!(keys&A41_RIGHT)-!!(keys&A41_LEFT),dy=!!(keys&A41_DOWN)-!!(keys&A41_UP),speed=(keys&A41_CHARGE)?5:3;
 if(dx||dy)a->face=abs41(dx)>abs41(dy)?(dx>0?1:3):(dy>0?2:0);
 a->px=clamp41(a->px+dx*speed,20,300);a->py=clamp41(a->py+dy*speed,44,204);
 if(a->cd)a->cd--;if((keys&A41_BREATH)&&!a->cd){a->cd=12;int l=s->route.current_id;WpRange39 r=wp_slots39[l];for(int i=0;i<r.count;i++){int x,y;spot43(l,i,&x,&y);int vx=x-a->px,vy=y-a->py;int along=a->face==0?-vy:a->face==1?vx:a->face==2?vy:-vx,cross=(a->face&1)?vy:vx;if(along>0&&along<=82&&abs41(cross)<=18&&!progress_has33(&s->p,r.first+i)){wp_collect39(&s->route,&s->p,r.first+i);break;}}}
}
#endif
