#ifndef COMBAT65_H
#define COMBAT65_H
/* Source EDF vulnerability subset: 1 fire, 2 charge, 4 lightning. */
static int vulnerable65(int model,int hit){static const unsigned char mask[]={0,0,7,5,7,2,0};return model>=0&&model<7&&(mask[model]&hit)!=0;}
static int reward65(int model){return model==5?5:(model==3||model==4?1:0);}
typedef struct {unsigned char state,aim,cool;int yaw;} Enemy65;
static int defeat65(Enemy65*e,int model,int hit){if(e->state||!vulnerable65(model,hit))return 0;e->state=1;e->aim=e->cool=0;return 1;}
#endif
