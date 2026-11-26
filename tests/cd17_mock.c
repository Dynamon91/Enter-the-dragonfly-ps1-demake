/* Register-level CD transport mock: deliberately models only the documented
 * command/event handshake, not timing, optics or emulator behavior. */
#include <stdint.h>
#include <string.h>
static const unsigned char*disc;static unsigned sectors,bank,irq,command,phase,params[3],np,ready,offset,lba,reads,fail_mode,commands,response,pending;
void mock17_setup(const unsigned char*p,unsigned n,unsigned fail){disc=p;sectors=n;bank=irq=command=phase=np=ready=offset=lba=reads=commands=response=pending=0;fail_mode=fail;}
unsigned mock17_reads(void){return reads;}unsigned mock17_commands(void){return commands;}
static unsigned dec(unsigned b){return 10*(b>>4)+(b&15);}
static void signal(unsigned t){irq=t;response=1;}
unsigned char cd17_in(unsigned r){if(r==0)return 0x10|(response?0x20:0)|(ready?0x40:0);if(r==3&&bank==1)return irq;if(r==1){response=0;return 2;}if(r==2&&ready&&lba<sectors&&offset<2048){unsigned char b=disc[lba*2352+24+offset++];if(offset==2048){reads++;ready=0;}return b;}return 0;}
void cd17_out(unsigned r,unsigned char v){if(r==0){bank=v&3;return;}if(bank==1&&r==3){if(v&0x40)np=0;if(v&0x1f){unsigned old=irq;irq=response=0;if(command==6){if(old==1){lba++;if(lba>=sectors){signal(5);return;}}if(old==3||old==1)signal(fail_mode==2?5:1);}else if(command==9){if(old==1&&pending){pending=0;signal(3);}else if(old==3)signal(2);}}return;}if(bank!=0)return;if(r==2){if(np<3)params[np++]=v;return;}if(r==3){ready=(v&128)&&irq==1&&fail_mode!=3;offset=0;return;}if(r==1){commands++;unsigned old=irq;command=v;if(fail_mode==1){irq=0;return;}if(v==2&&np==3){unsigned t=dec(params[0])*4500+dec(params[1])*75+dec(params[2]);lba=t-150;}np=0;if(v==9&&old==1){pending=1;return;}signal(3);}}
