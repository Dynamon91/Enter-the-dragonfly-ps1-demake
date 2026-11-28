#include "loader_save78.h"
Status78 save_campaign78(int selector,const LoaderIo78*io){return loader_save78(selector,io,SESSION72,SCRATCH78);}
Status78 restore_campaign78(int selector,const LoaderIo78*io){return loader_restore78(selector,io,SESSION72,SCRATCH78);}
_Static_assert(sizeof(Session72)==41148,"snapshot ABI changed");
_Static_assert(SCRATCH78_ADDR+sizeof(LoaderScratch78)<WORLD72_LIMIT,"scratch overlaps resident loader");
