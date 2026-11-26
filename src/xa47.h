#ifndef XA47_H
#define XA47_H
/* Transport owns CD exclusively until stopped. All LBAs are physical sectors. */
typedef struct {unsigned first,last,loop_first,loop_last;unsigned char file,channel,loop;} Track47;
typedef struct {int (*start)(unsigned,unsigned,unsigned);int (*position)(unsigned*);int (*stop)(void);} Bus47;
enum { XA47_IDLE,XA47_PLAY,XA47_FAULT };
typedef struct {Track47 track;unsigned state,pos,loops,stale;int waiting;} Player47;
static int valid47(const Track47*t){return t&&t->file&&t->channel<32&&t->first<=t->last&&t->last<=449800u&&(t->last-t->first)%8==0&&(!t->loop||(t->loop_first>=t->first&&t->loop_last<=t->last&&t->loop_first<=t->loop_last&&(t->loop_first-t->first)%8==0&&(t->loop_last-t->first)%8==0));}
static int fault47(Player47*p,const Bus47*b){b->stop();p->state=XA47_FAULT;return 0;}
static int stop47(Player47*p,const Bus47*b){if(p->state==XA47_FAULT)return 0;if(p->state==XA47_IDLE)return 1;if(!b->stop())return fault47(p,b);p->state=XA47_IDLE;return 1;}
static int begin47(Player47*p,const Bus47*b,const Track47*t){if(p->state==XA47_FAULT||!valid47(t))return 0;if(!stop47(p,b))return 0;p->track=*t;p->pos=t->first;p->loops=p->stale=0;p->waiting=1;if(!b->start(t->first,t->file,t->channel))return fault47(p,b);p->state=XA47_PLAY;return 1;}
/* Poll at <= 4 vblanks. Seek/read startup may report old SubQ positions.
 * Bounded stale polling; no claim of seamless seek or exact audible endpoint. */
static int poll47(Player47*p,const Bus47*b){if(p->state!=XA47_PLAY)return p->state==XA47_IDLE;unsigned pos,first=p->loops?p->track.loop_first:p->track.first,end=(p->track.loop?p->track.loop_last:p->track.last)+8;
 if(!b->position(&pos))return fault47(p,b);
 if(p->waiting&&(pos<first||pos>end+24)){if(++p->stale>120)return fault47(p,b);return 1;}
 if(!p->waiting&&pos<p->pos){if(++p->stale>120)return fault47(p,b);return 1;}
 if(!p->waiting&&pos==p->pos){if(++p->stale>120)return fault47(p,b);return 1;}
 p->waiting=0;p->pos=pos;p->stale=0;
 if(pos>=end){if(!stop47(p,b))return 0;if(!p->track.loop)return 1;p->loops++;p->waiting=1;if(!b->start(p->track.loop_first,p->track.file,p->track.channel))return fault47(p,b);p->state=XA47_PLAY;}
 return 1;
}
#endif
