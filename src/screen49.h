#ifndef SCREEN49_H
#define SCREEN49_H
#include "xa47.h"
#include "xa47_view.h"
static void screen49(Rect47 rect,int ok,int selected,unsigned bytes){rect(0,0,320,240,0x251c18);label47(rect,12,10,"ETD 049 SPU AUDIO LAB",0xffffff);label47(rect,12,35,ok?"BANK LOADED":"BANK FAULT",ok?0x70ce83:0x5050ef);label47(rect,12,65,selected?"SAMPLE 02 LOOP":"SAMPLE 01 ONE SHOT",0xffffff);label47(rect,12,96,"BANK BYTES",0xffffff);number47(rect,120,96,bytes);label47(rect,12,126,"X PLAY  CIRCLE STOP",0xffffff);label47(rect,12,145,"TRIANGLE SELECT",0xffffff);label47(rect,12,200,"TEST TONES ONLY",0xc5bcb2);}
#endif
