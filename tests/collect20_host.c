#include "../src/cache18.c"
#include "../src/collect20.h"
static const short sn[64]={0,401,799,1189,1567,1931,2276,2598,2896,3166,3406,3612,3784,3920,4017,4076,4096,4076,4017,3920,3784,3612,3406,3166,2896,2598,2276,1931,1567,1189,799,401,0,-401,-799,-1189,-1567,-1931,-2276,-2598,-2896,-3166,-3406,-3612,-3784,-3920,-4017,-4076,-4096,-4076,-4017,-3920,-3784,-3612,-3406,-3166,-2896,-2598,-2276,-1931,-1567,-1189,-799,-401};
void reset20(Collect20*c,int x,int y,int z){collectreset20(c,x,y,z);}
void step20(Collect20*c,const Cache18*w,int x,int y,int z,int heading){collectstep20(c,w,x,y,z,heading,sn);}
int id20(U32 i){return gemid20(i);}
void award20(Collect20*c,int i,int value){take20(c,i,value,0);}
