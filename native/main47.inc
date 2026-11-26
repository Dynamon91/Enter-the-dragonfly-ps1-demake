#include "xa47.h"
#include "xa47_view.h"
#include "tracks47.h"
extern int cd_start47(unsigned,unsigned,unsigned),cd_position47(unsigned*),cd_stop47(void);
static const Bus47 bus={cd_start47,cd_position47,cd_stop47};
void main40(void){
 GP1=0;GP1=0x03000001;GP1=0x05000000;GP1=0x06c60260;GP1=0x07042018;GP1=0x08000001;
 gp(0xe1000400);gp(0xe3000000);gp(0xe4000000|319|(239<<10));gp(0xe5000000);gp(0xe6000000);GP1=0x03000000;
 Player47 p={0};int prev=0,selected=0,tick=0;
 for(;;){vblank();int k=pad(),edge=k&~prev;prev=k;
 if(edge&4096){if(stop47(&p,&bus))selected^=1;}
 if(edge&16384)begin47(&p,&bus,&tracks47[selected]);if(edge&8192)stop47(&p,&bus);
 if(++tick==4){tick=0;poll47(&p,&bus);screen47(rect,&p,selected);}
 }
}
