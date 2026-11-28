#ifndef ETD_KITE_ANIM_H
#define ETD_KITE_ANIM_H
#include <stdint.h>
#include "kite_anim_data.h"
/* Eight source-derived samples across 60 nominal simulation ticks.
 * Generate kite_anim_data.h locally from the user-owned PS2 source. */
static inline int ka_coord(unsigned tick,unsigned vertex,unsigned component){
 unsigned p=(tick%60u)*8u,a=p/60u,b=(a+1u)&7u;
 int x=kite_delta[a][vertex][component],y=kite_delta[b][vertex][component];
 return kite_bias[component]+x+(y-x)*(int)(p%60u)/60;
}
static inline unsigned ka_scale(unsigned age){return age<5?kite_shrink[age]:0;}
static inline int ka_apply_scale(int value,unsigned scale){return value*(int)scale/4096;}
#endif
