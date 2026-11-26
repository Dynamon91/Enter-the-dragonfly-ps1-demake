#include <assert.h>
#include <stdio.h>
typedef unsigned char U8;typedef unsigned int U32;
#include "progress33.h"
#include "workprint38.h"
#include "campaign39.h"
static const WpReady38 all={0x3fffffffu,31};
static void move(WpRoute38*r,Progress33*p,int kind,int id){assert(!wp_request39(r,p,&all,kind,id,0));assert(!wp_finish39(r,p,&all,1,0));}
static void collect(WpRoute38*r,Progress33*p,int cap){WpRange39 a=wp_slots39[r->current_id];for(int i=0;i<a.count&&i<cap;i++)if(!progress_has33(p,a.first+i))assert(!wp_collect39(r,p,a.first+i));}
static void layout(void){int seen[120]={0};Progress33 p;U8 f,t;progress_reset33(&p,1);for(int l=0;l<30;l++){assert(wp_atlas39(&p,l,&f,&t));assert(!f&&t==wp_slots39[l].count&&t>0);assert(t==10||l>8);for(int s=wp_slots39[l].first;s<wp_slots39[l].first+t;s++){assert(s<120&&s>=0);assert(wp_owner39(s)==l);seen[s]++;assert((s>=90)==(l>=9));}}for(int s=0;s<120;s++)assert(seen[s]==1);for(int s=0;s<4;s++)assert(wp_owner39(s)==1);assert(wp_owner39(-1)==-1&&wp_owner39(120)==-1);}
static void original(void){Progress33 p;WpRoute38 r;U8 f,t;progress_reset33(&p,0);assert(!wp_init39(&r,&p,&all,0));assert(wp_request39(&r,&p,&all,0,1,0)==WP38_GATE);collect(&r,&p,3);move(&r,&p,0,1);collect(&r,&p,10);move(&r,&p,0,0);collect(&r,&p,6);for(int l=2;l<=8;l++){move(&r,&p,0,l);collect(&r,&p,10);if(l==4){move(&r,&p,0,0);collect(&r,&p,10);}}assert(p.count==90);assert(!wp_atlas39(&p,9,&f,&t)&&!f&&!t);assert(wp_collect39(&r,&p,90)==WP38_MODE);assert(wp_request39(&r,&p,&all,1,2,0)==WP39_RIPTO_GATE);assert(!wp_request39(&r,&p,&all,1,2,1));assert(wp_finish39(&r,&p,&all,1,0)==WP39_RIPTO_GATE);assert(r.current_kind==0&&r.current_id==8);}
static void safeguards(void){Progress33 p;WpRoute38 r;WpReady38 ready={1,0};progress_reset33(&p,1);assert(!wp_init39(&r,&p,&all,0));assert(wp_collect39(&r,&p,0)==WP39_WRONG_SCENE);assert(wp_collect39(&r,&p,-1)==WP38_INVALID);assert(!wp_collect39(&r,&p,10));assert(wp_collect39(&r,&p,10)==WP39_DUPLICATE);assert(wp_request39(&r,&p,&ready,0,1,0)==WP38_MISSING);assert(!wp_request39(&r,&p,&all,0,1,0));assert(wp_collect39(&r,&p,11)==WP38_BUSY);assert(wp_finish39(&r,&p,&all,0,0)==WP38_LOAD_FAILED);assert(p.count==1&&r.current_id==0&&p.visited==1);}
/* Reachability under an abstract all-packs-ready model. Hub rewards staged
 * 3 at start, 3 after Dojo, and 4 after Cloud 9, per original walkthrough. */
static void fight_if_ready(WpRoute38*r,Progress33*p){
 for(int b=0;b<5;b++)if(!(p->bosses&(1u<<b))&&!wp_check39(p,&all,1,b,0)){
  assert(p->count==wp_boss_gates38[b].flies);int home=r->current_id;
  move(r,p,1,b);assert(!wp_defeat38(r,p));printf("Boss %d reachable at %u dragonflies\n",b,p->count);
  assert(!wp_return38(r,p,&all));assert(!wp_finish39(r,p,&all,1,0));assert(r->current_id==home);
 }
}
static void expanded(void){Progress33 p;WpRoute38 r;U8 f,t;int changes,passes=0;progress_reset33(&p,1);assert(!wp_init39(&r,&p,&all,0));do{int old=p.count,oldb=p.bosses;for(int l=0;l<30;l++)if(!wp_check39(&p,&all,0,l,0)){move(&r,&p,0,l);int cap=l==0?((p.visited&(1u<<4))?10:(p.visited&(1u<<1))?6:3):10;WpRange39 a=wp_slots39[l];for(int i=0;i<a.count&&i<cap;i++)if(!progress_has33(&p,a.first+i)){assert(!wp_collect39(&r,&p,a.first+i));fight_if_ready(&r,&p);}}changes=old!=p.count||oldb!=p.bosses;assert(++passes<=35);}while(changes);assert(p.count==120&&p.bosses==31&&p.visited==0x3fffffff);for(int l=0;l<30;l++){assert(wp_atlas39(&p,l,&f,&t));assert(f==t);}printf("Expanded fixed point: %u flies, 30 locations, 5 bosses; %d passes\n",p.count,passes);}
int main(void){layout();original();safeguards();expanded();puts("4 campaign scenario groups passed");return 0;}
