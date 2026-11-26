#include <assert.h>
#include <stdio.h>
typedef unsigned char U8;typedef unsigned int U32;
#include "progress33.h"
#include "workprint38.h"
static void fill(Progress33*p,int n){while(p->count<n)assert(progress_take33(p,p->count));}
int main(void){
 Progress33 p;WpRoute38 r;WpReady38 a={3,0};int n=0;
 progress_reset33(&p,0);assert(!wp_init38(&r,&p,&a,0));assert(p.visited==1);n++;
 assert(wp_check38(&p,&a,WP38_LEVEL,9)==WP38_MODE);assert(wp_check38(&p,&a,WP38_BOSS,0)==WP38_MODE);n++;
 assert(wp_check38(&p,&a,0,30)==WP38_INVALID);assert(wp_check38(&p,&a,0,-1)==WP38_INVALID);assert(wp_check38(&p,&a,1,5)==WP38_INVALID);assert(wp_check38(&p,&a,2,0)==WP38_INVALID);n++;
 assert(wp_request38(&r,&p,&a,0,2)==WP38_MISSING);assert(!r.pending);n++;
 assert(!wp_request38(&r,&p,&a,0,1));assert(wp_request38(&r,&p,&a,0,0)==WP38_BUSY);assert(p.visited==1);n++;
 assert(wp_finish38(&r,&p,&a,0)==WP38_LOAD_FAILED);assert(r.current_id==0&&p.visited==1);assert(wp_finish38(&r,&p,&a,1)==WP38_NO_PENDING);n++;
 assert(!wp_request38(&r,&p,&a,0,1));a.levels=1;assert(wp_finish38(&r,&p,&a,1)==WP38_MISSING);assert(r.current_id==0);n++;
 a.levels=3;assert(!wp_request38(&r,&p,&a,0,1));assert(!wp_finish38(&r,&p,&a,1));assert(r.current_id==1&&p.visited==3);n++;
 assert(wp_defeat38(&r,&p)==WP38_NOT_IN_BOSS);a.bosses=4;assert(!wp_request38(&r,&p,&a,1,2));assert(!wp_finish38(&r,&p,&a,1));assert(!p.bosses);n++;
 assert(!wp_defeat38(&r,&p));assert(p.bosses==4);assert(wp_defeat38(&r,&p)==WP38_ALREADY_WON);assert(!wp_return38(&r,&p,&a));assert(!wp_finish38(&r,&p,&a,1));assert(r.current_id==1);n++;
 progress_reset33(&p,1);a.levels=0x3fffffff;a.bosses=31;assert(!wp_init38(&r,&p,&a,0));assert(wp_check38(&p,&a,0,9)==WP38_GATE);fill(&p,12);assert(!wp_check38(&p,&a,0,9));n++;
 for(int i=0;i<5;i++){int gate=wp_boss_gates38[i].flies;fill(&p,gate-1);assert(wp_check38(&p,&a,1,i)==WP38_GATE);fill(&p,gate);assert(!wp_request38(&r,&p,&a,1,i));assert(!wp_finish38(&r,&p,&a,1));assert(!(p.bosses&(1u<<i)));assert(!wp_defeat38(&r,&p));assert(!wp_return38(&r,&p,&a));assert(!wp_finish38(&r,&p,&a,1));}assert(p.bosses==31);n++;
 fill(&p,120);for(int i=0;i<30;i++)assert(!wp_check38(&p,&a,0,i));assert(!progress_take33(&p,120));n++;
 printf("%d scenario groups passed\n",n);return 0;
}
