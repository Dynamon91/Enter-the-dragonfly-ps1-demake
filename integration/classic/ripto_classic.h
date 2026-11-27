#ifndef ETD_RIPTO_CLASSIC_H
#define ETD_RIPTO_CLASSIC_H
#include <stdint.h>

/* Standalone logic-only adapter: values are provisional, not PS2-extracted.
 * Call tick once per fixed 30 Hz simulation step. Call hit only on a newly
 * intersecting breath pulse, not for each overlapping render frame. */
enum { RC_FLAME=1, RC_ICE, RC_ELECTRIC, RC_BUBBLE };
enum { RC_MOVE=1, RC_BOLT, RC_RING, RC_OPEN, RC_SHIELD_HIT,
       RC_BODY_HIT, RC_FORM_CHANGE, RC_CLEAR, RC_LOCKED };
enum { RC_RELOCATE=1, RC_ATTACK, RC_EXPOSED, RC_DONE };
typedef struct {
    uint16_t completion, timer;
    uint8_t form, state, shield, hp, bolts, rings, cycles, cooldown;
} RcBoss;

static inline void rc_form(RcBoss *b, uint8_t form) {
    b->form=form; b->state=RC_RELOCATE; b->timer=24;
    b->shield=form==1?3:form==2?3:0;
    b->hp=form==1?3:form==2?1:6;
    b->bolts=0; b->rings=0; b->cycles=0; b->cooldown=0;
}
static inline int rc_start(RcBoss *b, unsigned completion_permille) {
    *b=(RcBoss){0};
    if(completion_permille>1000 || completion_permille<700) return RC_LOCKED;
    b->completion=(uint16_t)completion_permille; rc_form(b,1); return RC_MOVE;
}
static inline int rc_tick(RcBoss *b) {
    if(!b->form || b->state==RC_DONE) return 0;
    if(b->cooldown) --b->cooldown;
    if(b->timer && --b->timer) return 0;
    if(b->state==RC_RELOCATE) {
        b->state=RC_ATTACK; b->bolts=0; b->rings=0; b->timer=20; return 0;
    }
    if(b->state==RC_EXPOSED) {
        b->state=RC_RELOCATE; b->timer=24; return RC_MOVE;
    }
    if(b->bolts < (b->form==3?3:2)) {
        ++b->bolts; b->timer=20; return RC_BOLT;
    }
    if(b->rings < (b->form==3?2:3)) {
        ++b->rings; b->timer=24; return RC_RING;
    }
    /* Deterministic alternating opportunities for giant Ripto, rather than
     * introducing an unbounded random wait. Exact retail cadence unverified. */
    if(b->form==3 && (++b->cycles & 1)==0) {
        b->state=RC_RELOCATE; b->timer=24; return RC_MOVE;
    }
    b->state=RC_EXPOSED; b->timer=60; return RC_OPEN;
}
static inline int rc_hit(RcBoss *b, unsigned breath) {
    unsigned required;
    if(!b->form || b->state==RC_DONE || b->state==RC_RELOCATE || b->cooldown) return 0;
    required=b->form==1?RC_FLAME:b->form==2?RC_ICE:RC_ELECTRIC;
    if(breath!=required || (b->form==3 && b->state!=RC_EXPOSED)) return 0;
    b->cooldown=12;
    if(b->shield) {
        --b->shield; b->state=RC_RELOCATE; b->timer=24; return RC_SHIELD_HIT;
    }
    if(--b->hp) { b->state=RC_RELOCATE; b->timer=24; return RC_BODY_HIT; }
    if((b->form==1 && b->completion>=850) || (b->form==2 && b->completion==1000)) {
        rc_form(b,(uint8_t)(b->form+1)); return RC_FORM_CHANGE;
    }
    b->state=RC_DONE; b->timer=0; return RC_CLEAR;
}
#endif
