#ifndef SCENE52_H
#define SCENE52_H
/* Scene-specific ETDI metadata; original v0.37 RAM ceilings, no extra content. */
#define SCENE52_CAP 28u
#define SCENE52_BYTES (460u*1024u)
#define SCENE52_INDEX 28672u
typedef unsigned char S52Byte;
typedef unsigned int S52Word;
typedef int (*S52Read)(void*,S52Word,S52Word,S52Byte*);
typedef struct {const S52Byte *idx; S52Word len,sectors,materials,render,collision,objects,blocks,level;} Scene52;
typedef struct {S52Word count,bytes,id[SCENE52_CAP],offset[SCENE52_CAP],meta[SCENE52_CAP][7];} Page52;
typedef struct {Page52 pages[2];S52Byte *buf[2];Scene52 scene[2];int active;} Cache52;
int scene52_open(Scene52*,const S52Byte*,S52Word,S52Word,S52Word,S52Word);
int scene52_init(Cache52*,S52Byte*,S52Byte*);
int scene52_switch(Cache52*,const Scene52*,int,int,S52Read,void*);
#endif
