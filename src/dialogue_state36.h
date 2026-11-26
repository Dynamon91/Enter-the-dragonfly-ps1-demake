/* Conversation presentation adapted from original Say IDs. Quest flags remain authoritative. */
typedef struct {int actor,at,count,ids[3],dooie_seen;} Dialog36;
static void dialog_reset36(Dialog36*d){d->actor=-1;d->at=d->count=d->dooie_seen=0;}
static void dialog_add36(Dialog36*d,int id){if(id&&d->count<3)d->ids[d->count++]=id;}
static void dialog_open36(Dialog36*d,int actor,int before,int seen,int event,int reward){
 static const int ids[3][6]={{430,431,432,467,468,468},{420,421,428,423,422,422},{426,427,422,0,466,465}};
 if(actor<0||actor>=3||!(event&2))return;
 d->actor=actor;d->at=d->count=0;
 if(before<Q34_ARRIVED){if(!seen)dialog_add36(d,ids[actor][0]);dialog_add36(d,ids[actor][1]);}
 else if(before==Q34_ARRIVED){dialog_add36(d,ids[actor][2]);dialog_add36(d,(event&8)?418:ids[actor][3]);}
 else if(actor==2){dialog_add36(d,ids[actor][d->dooie_seen?5:4]);d->dooie_seen=1;}
 else dialog_add36(d,ids[actor][reward?4:3]);
 if(!d->count)d->actor=-1;
}
static int dialog_active36(const Dialog36*d){return d->actor>=0&&d->at<d->count;}
static int dialog_id36(const Dialog36*d){return dialog_active36(d)?d->ids[d->at]:0;}
static void dialog_next36(Dialog36*d){if(dialog_active36(d)&&++d->at>=d->count)d->actor=-1;}
static int pose_index36(int tick,int talk,int period){return (talk?6:0)+((tick%period)*6/period);}
