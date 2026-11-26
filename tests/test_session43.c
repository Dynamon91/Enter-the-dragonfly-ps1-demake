#define main arena41_test_main
#include "test_arena41.c"
#undef main
#include "session43.h"
#include "screen43.h"
static void tap(Session43*s,int k){step43(s,0);step43(s,k);step43(s,0);}
static void select43(Session43*s,int n){while(s->selection!=n)tap(s,S43_NEXT);}
static void move43(Session43*s,int x,int y){int t=0;while(abs41(s->a.px-x)>2||abs41(s->a.py-y)>2){int dx=x-s->a.px,dy=y-s->a.py,k=0;if(abs41(dx)>2)k|=dx>0?A41_RIGHT:A41_LEFT;if(abs41(dy)>2)k|=dy>0?A41_DOWN:A41_UP;step43(s,k);assert(++t<200);}step43(s,0);}
static void gather43(Session43*s){int l=s->route.current_id;WpRange39 r=wp_slots39[l];for(int i=0;i<r.count;i++)if(!progress_has33(&s->p,r.first+i)){int x,y;spot43(l,i,&x,&y);move43(s,x,y+36);step43(s,A41_UP);for(int j=0;j<25;j++)step43(s,A41_BREATH);assert(progress_has33(&s->p,r.first+i));}int n=s->p.count;for(int i=0;i<30;i++)step43(s,A41_BREATH);assert(s->p.count==n);}
static void fight43(Session43*s,int b){int from=s->route.current_id;select43(s,30+b);tap(s,S43_ENTER);assert(s->route.current_kind==WP38_BOSS);assert(!(s->p.bosses&(1<<b)));tap(s,S43_EXIT);assert(s->route.current_kind==WP38_LEVEL&&s->route.current_id==from&&!(s->p.bosses&(1<<b)));tap(s,S43_ENTER);int ticks=0;while(s->a.state<A41_WIN&&ticks++<12000)step43(s,bot(&s->a));assert(s->a.state==A41_WIN);assert(s->p.bosses&(1<<b));printf("Boss %d defeated at %u flies in %d ticks\n",b,s->p.count,ticks);tap(s,S43_ENTER);assert(s->route.current_kind==WP38_LEVEL&&s->route.current_id==from);}
static View42 view;static int triangles;
static void tr(P42 a,P42 b,P42 c,unsigned col){(void)a;(void)b;(void)c;(void)col;triangles++;}
int main(void){Session43 s;init43(&s);tap(&s,S43_ENTER);assert(s.error==WP38_GATE&&s.route.current_id==0);select43(&s,30);tap(&s,S43_ENTER);assert(s.error==WP38_GATE);screen43(&view,&s,recthost,tr);assert(!view.dropped&&triangles>100);int pass=0,old;do{old=s.p.count;for(int l=0;l<30;l++)if(!eligible43(&s,l)){select43(&s,l);tap(&s,S43_ENTER);assert(!s.error&&s.route.current_id==l);gather43(&s);for(int b=0;b<5;b++)if(!(s.p.bosses&(1<<b))&&!eligible43(&s,30+b))fight43(&s,b);}assert(++pass<8);}while(s.p.count!=old);assert(s.p.count==120&&s.p.bosses==31&&s.p.visited==0x3fffffff);printf("Full input-driven lab: %u flies, %u boss mask, %d passes\n",s.p.count,s.p.bosses,pass);return 0;}
