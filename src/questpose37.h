#include "bitpack37.h"
#include "questpack37.h"
#define Q37_MAX_VALUES 1539
/* Adjacent poses always have opposite parity (including wrap 5->0/11->6).
   Keep two samples per NPC so interpolated rendering decodes only on changes. */
static signed char qcache37[3][2][Q37_MAX_VALUES];
static int qframe37[3][2]={{-1,-1},{-1,-1},{-1,-1}};
static const signed char *qpose37(int id,int frame,int nv){
 if(id<0||id>=3||frame<0||frame>=12||nv!=qnv37[id]||nv>Q37_MAX_VALUES/3)return 0;
 int slot=frame&1; signed char*p=qcache37[id][slot];
 if(qframe37[id][slot]!=frame){const unsigned int*o=qoffs37[id];const unsigned char*b=qbits37[id];qframe37[id][slot]=-1;if(!decode37_s8(b+o[frame],b+o[frame+1],p,nv*3))return 0;qframe37[id][slot]=frame;}
 return p;
}
