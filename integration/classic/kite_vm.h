#ifndef ETD_KITE_VM_H
#define ETD_KITE_VM_H
#include "kite_source.h"
/* Source flag/branch interpreter, diagnostic state separate from game saves. */
typedef struct {uint32_t flags;uint16_t pc,line;uint8_t visits[3],actor,active,awarded,error;uint16_t presentation;} KiteVm;
static inline int kite_key(unsigned group,unsigned n){for(unsigned i=0;i<sizeof(kite_keys)/sizeof(*kite_keys);i++)if(kite_keys[i]==group*1024u+n)return (int)i;return -1;}
static inline int kite_flag(const KiteVm*v,unsigned g,unsigned n){int k=kite_key(g,n);return k>=0&&((v->flags>>k)&1u);}
static inline void kite_set(KiteVm*v,unsigned g,unsigned n){int k=kite_key(g,n);if(k>=0)v->flags|=1u<<k;}
static inline void kite_arrive(KiteVm*v,unsigned actor){static const unsigned arrival[]={22,28,34};if(actor<3&&!v->active)kite_set(v,1,arrival[actor]);}
static inline int kite_begin(KiteVm*v,unsigned actor){if(v->active||actor>=3)return 0;v->actor=actor;v->pc=0;v->line=0;v->active=1;v->error=0;return 1;}
/* Run until Say or end. One-shot reward guard independent of repeat/shortcut branch.
 * Presentation commands counted, not performed: actual animation/camera/SFX integration pending. */
static inline unsigned kite_next(KiteVm*v){if(!v->active)return 0;v->line=0;for(unsigned steps=0;steps<128;steps++){
 if(v->actor>=3||v->pc>=kite_size[v->actor])break;
 KiteOp o=kite_program[v->actor][v->pc++];
 switch(o.op){
 case 0:v->active=0;if(v->visits[v->actor]<255)v->visits[v->actor]++;return 0;
 case 1:v->flags|=1u<<o.a;break;
 case 2:v->flags&=~(1u<<o.a);break;
 case 3:v->pc=((v->flags>>o.a)&1u)?o.c:o.b;break;
 case 4:v->pc=v->visits[v->actor]>=o.a?o.c:o.b;break;
 case 5:v->pc=o.a;break;
 case 6:v->line=o.a;return o.a;
 case 7:if(o.a==1&&!v->awarded&&!kite_flag(v,1,204))v->awarded=1;break;
 case 8:if(v->presentation<65535)v->presentation++;break;
 default:goto error;
 }}
 error:v->active=0;v->error=1;return 0;
}
#endif
