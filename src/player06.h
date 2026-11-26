/* Shared fixed-point prototype movement logic. Grid heights are in Y-down units. */
#define PAD_SELECT 1
#define PAD_START 8
#define PAD_UP 16
#define PAD_RIGHT 32
#define PAD_DOWN 64
#define PAD_LEFT 128
#define PAD_L1 1024
#define PAD_R1 2048
#define PAD_CROSS 16384
#define PAD_SQUARE 32768
#define PAD_TRIANGLE 4096
#define PAD_CIRCLE 8192
typedef struct {int x,y,z,vy,heading,camera,grounded,prev;} Player;
static int ab(int a){return a<0?-a:a;}
static int floor_at(int x,int z){
 int xx=x+GRID_RADIUS,zz=z+GRID_RADIUS;if(xx<0||zz<0||xx>GRID_RADIUS*2||zz>GRID_RADIUS*2)return 32767;
 int ix=(xx+GRID_STEP/2)/GRID_STEP,iz=(zz+GRID_STEP/2)/GRID_STEP;int nearest=floorgrid[iz*GRID+ix];if(nearest==32767)return nearest;int a=xx/GRID_STEP,b=zz/GRID_STEP;if(a>=GRID-1||b>=GRID-1)return nearest;int f0=floorgrid[b*GRID+a],f1=floorgrid[b*GRID+a+1],f2=floorgrid[(b+1)*GRID+a],f3=floorgrid[(b+1)*GRID+a+1];if(f0==32767||f1==32767||f2==32767||f3==32767||ab(f0-f1)>110||ab(f0-f2)>110||ab(f0-f3)>110)return nearest;int u=xx%GRID_STEP,v=zz%GRID_STEP;return ((f0*(GRID_STEP-u)+f1*u)*(GRID_STEP-v)+(f2*(GRID_STEP-u)+f3*u)*v)/(GRID_STEP*GRID_STEP);
}
static void reset_player(Player*p){p->x=SPAWN_X;p->y=SPAWN_Y;p->z=SPAWN_Z;p->vy=0;p->heading=0;p->camera=0;p->grounded=1;p->prev=0;}
static void step_player(Player*p,int btn,int ax,int az){
 if(btn&PAD_START){reset_player(p);return;}
 if(btn&PAD_L1)p->camera=(p->camera-1)&63;
 if(btn&PAD_R1)p->camera=(p->camera+1)&63;
 if(btn&PAD_SELECT)p->camera=p->heading;
 int dx=((btn&PAD_RIGHT)!=0)-((btn&PAD_LEFT)!=0), dz=((btn&PAD_UP)!=0)-((btn&PAD_DOWN)!=0);
 if(!dx&&!dz){dx=(ax>35)-(ax<-35);dz=(az>35)-(az<-35);}
 int speed=(btn&PAD_SQUARE)?38:19;
 if(dx||dz){int dir=dz>0?(dx>0?8:dx<0?56:0):dz<0?(dx>0?24:dx<0?40:32):dx>0?16:48;
 p->heading=(p->camera+dir)&63;int nx=p->x+(sine[p->heading]*speed>>12),nz=p->z+(sine[(p->heading+16)&63]*speed>>12);
 int f=floor_at(nx,nz),old=floor_at(p->x,p->z);
 int mid=floor_at((nx+p->x)/2,(nz+p->z)/2);if(f!=32767&&old!=32767&&mid!=32767&&ab(f-old)<=110&&ab(mid-old)<=110){p->x=nx;p->z=nz;}}
 int f=floor_at(p->x,p->z);if(f==32767){reset_player(p);return;}
 if(p->grounded){p->y=f;if((btn&PAD_CROSS)&&!(p->prev&PAD_CROSS)){p->vy=-38;p->grounded=0;}}
 if(!p->grounded){p->vy+=3;if((btn&PAD_CROSS)&&p->vy>8)p->vy=8;p->y+=p->vy;if(p->y>=f){p->y=f;p->vy=0;p->grounded=1;}}
 p->prev=btn;
}
