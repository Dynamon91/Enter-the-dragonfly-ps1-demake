#ifndef ETD_SCENE_SFX_H
#define ETD_SCENE_SFX_H
#include <stdint.h>
enum { FX_HURT, FX_FIRE, FX_JUMP, FX_BASKET, FX_DEATH, FX_COUNT };
typedef struct {uint32_t addr,cap;uint16_t id,volume;} EtSceneFx;
static const EtSceneFx scene_fx[FX_COUNT]={
 {0x50000u,10752u,127u,9216u},
 {0x52a00u,15424u,23u,5069u},
 {0x56640u,6272u,129u,9216u},
 {0x57ec0u,36544u,1080u,8294u},
 {0x60d80u,25408u,79u,7373u},
};
static int scene_fx_layout_ok(void){uint32_t end=0x50000u;for(unsigned i=0;i<FX_COUNT;i++){const EtSceneFx*f=scene_fx+i;if(f->addr!=end||!f->cap||f->cap%64||f->addr>0x68000u-f->cap||f->volume>0x3fffu)return 0;end=f->addr+f->cap;}return 1;}
#endif
