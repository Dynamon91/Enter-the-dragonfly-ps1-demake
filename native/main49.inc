#include "spu49.h"
#include "sfx49_data.h"
#include "screen49.h"
extern int spu49_load(const unsigned char*,unsigned,const Sample49*,unsigned),spu49_play(unsigned,unsigned,unsigned,unsigned);
extern void spu49_stop(unsigned);
void main40(void){
 GP1=0;GP1=0x03000001;GP1=0x05000000;GP1=0x06c60260;GP1=0x07042018;GP1=0x08000001;
 gp(0xe1000400);gp(0xe3000000);gp(0xe4000000|319|(239<<10));gp(0xe5000000);gp(0xe6000000);GP1=0x03000000;
 int ok=spu49_load(sfx49,sizeof sfx49,entries49,2),prev=0,selected=0;
 for(;;){vblank();int keys=pad(),edge=keys&~prev;prev=keys;
 if(ok){if(edge&4096){spu49_stop(0);selected^=1;}if(edge&16384)spu49_play(0,selected,0x2000,0x2000);if(edge&8192)spu49_stop(0);}
 screen49(rect,ok,selected,sizeof sfx49);}
}
