#ifndef TEXTURE54_H
#define TEXTURE54_H
#include "scene52.h"
/* Include progress33.h with U8/U32 typedefs before this header. */
#include "portal53.h"
#define TEX54_GROUPS 540u
#define TEX54_SLOTS 64u
#define TEX54_PAYLOAD 4608u
#define TEX54_READ 6144u
typedef struct {const U8 *idx; U32 len,sectors; const short *material_groups; U32 materials;} Texture54;
typedef struct {short slots[TEX54_SLOTS]; short map[TEX54_GROUPS]; U32 count; int level;} TextureState54;
typedef void (*Upload54)(void*,int,const U8*);
enum { TEX54_BAD_BANK=6,TEX54_BUDGET,TEX54_READ_FAILED };
/* All references/scratch must remain valid and outside both terrain buffers.
 * Caller has stopped rendering and fenced GPU. Upload must be synchronous,
 * infallible, and copy exactly 4608 bytes to the old tex19 slot layout. */
int texture54_validate(const Texture54*);
int transition54(Cache52*,Progress33*,TextureState54*,const Scene52*,const Texture54*,const Spawn53*,int,S52Read,void*,S52Read,void*,U8*,Upload54,void*,Spawn53*);
#endif
