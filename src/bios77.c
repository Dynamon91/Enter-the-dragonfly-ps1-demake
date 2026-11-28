#include "card77.h"
extern int bios77_open(const char*,int),bios77_seek(int,int,int),bios77_read(int,B72*,int),bios77_write(int,const B72*,int),bios77_close(int);
extern Mc77Dir*bios77_first(const char*,Mc77Dir*);
extern void bios77_init(int),bios77_start(void),bios77_bu(void),bios77_auto(int),bios77_stop(void);
/* Run only in a loader mode with BIOS interrupts enabled, manual pad polling
 * stopped, no outstanding CD or SPU DMA; restore engine IRQ/SIO afterward. */
void mc77_bios_start(void){bios77_init(0);bios77_start();bios77_bu();bios77_auto(0);}
void mc77_bios_stop(void){bios77_stop();}
static int st(void*c,const char*p,Mc77Dir*d){(void)c;return bios77_first(p,d)!=0;}
static int op(void*c,const char*p,int f){(void)c;return bios77_open(p,f);}
static int sk(void*c,int f,int p){(void)c;return bios77_seek(f,p,0);}
static int rd(void*c,int f,B72*p,int n){(void)c;return bios77_read(f,p,n);}
static int wr(void*c,int f,const B72*p,int n){(void)c;return bios77_write(f,p,n);}
static int cl(void*c,int f){(void)c;return bios77_close(f);}
const Mc77Ops mc77_bios={0,st,op,sk,rd,wr,cl};
int mc77_native_save(Mc77*m,const Session72*l,Session72*s){return mc77_save(m,l,s);}
int mc77_native_load(Mc77*m,Session72*l,Session72*s,U72*w){return mc77_load(m,l,s,w);}
int mc77_native_mount(Mc77*m,int write){return mc77_mount(m,&mc77_bios,write);}
int mc77_native_close(Mc77*m){return mc77_close(m);}
