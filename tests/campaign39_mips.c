typedef unsigned char U8;typedef unsigned int U32;
#include "progress33.h"
#include "workprint38.h"
#include "campaign39.h"
int camp_init(WpRoute38*r,Progress33*p,WpReady38*a,int l){return wp_init39(r,p,a,l);}
int camp_enter(WpRoute38*r,Progress33*p,WpReady38*a,int k,int l,int ready){return wp_request39(r,p,a,k,l,ready);}
int camp_commit(WpRoute38*r,Progress33*p,WpReady38*a,int loaded,int ready){return wp_finish39(r,p,a,loaded,ready);}
int camp_take(WpRoute38*r,Progress33*p,int slot){return wp_collect39(r,p,slot);}
int camp_atlas(Progress33*p,int l,U8*f,U8*t){return wp_atlas39(p,l,f,t);}
