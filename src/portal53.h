#ifndef PORTAL53_H
#define PORTAL53_H
#include "scene52.h"
/* Include progress33.h before this header. Classic scene 9 = Ripto arena. */
enum { PORTAL53_OK, PORTAL53_BAD_STATE, PORTAL53_LOCKED, PORTAL53_BAD_ROUTE, PORTAL53_LOAD_FAILED, PORTAL53_NO_FLOOR };
typedef struct {int x,y,z,heading;} Spawn53;
int portal53_gate(const Progress33*,int current,int target,int completion);
int portal53_enter(Cache52*,Progress33*,const Scene52*,const Spawn53*,int completion,S52Read,void*,Spawn53*);
#endif
