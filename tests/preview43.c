#define main view42_test_main
#include "test_view42.c"
#undef main
#include "session43.h"
#include "screen43.h"
int main(int argc,char**argv){if(argc!=2)return 1;Session43 s;init43(&s);paint=1;screen43(&view,&s,r,t);FILE*f=fopen(argv[1],"wb");if(!f)return 2;fputs("P6\n320 240\n255\n",f);fwrite(img,1,sizeof img,f);fclose(f);return 0;}
