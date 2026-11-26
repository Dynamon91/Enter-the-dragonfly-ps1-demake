#include <stdint.h>
typedef int16_t s16;
typedef struct {int x,y,z;unsigned int screen;int u,v;} Point;
#include "../src/frustum07.h"
#include "../src/visibility09.h"
int visible09(const s16*b,int cx,int cy,int cz,int sn,int cs){return cluster_visible(b,cx,cy,cz,sn,cs);}
int mask09(int x,int y,int z,int cx,int cy,int cz,int sn,int cs){return clipmask(camera_space(x,y,z,cx,cy,cz,sn,cs));}
