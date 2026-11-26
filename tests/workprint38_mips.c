typedef unsigned char U8;typedef unsigned int U32;
#include "progress33.h"
#include "workprint38.h"
int wp_start(WpRoute38*r,Progress33*p,WpReady38*a,int id){return wp_init38(r,p,a,id);}
int wp_enter(WpRoute38*r,Progress33*p,WpReady38*a,int k,int id){return wp_request38(r,p,a,k,id);}
int wp_commit(WpRoute38*r,Progress33*p,WpReady38*a,int loaded){return wp_finish38(r,p,a,loaded);}
int wp_win(WpRoute38*r,Progress33*p){return wp_defeat38(r,p);}
int wp_back(WpRoute38*r,Progress33*p,WpReady38*a){return wp_return38(r,p,a);}
