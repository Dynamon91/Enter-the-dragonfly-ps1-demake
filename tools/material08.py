"""Use source executable's folded MD4 lookup, not visual guesses. Keep old geometry."""
import json,re,struct
from pathlib import Path
import numpy as np
from PIL import Image
from recover import records,pxt_groups,nodes,u32,shape_metadata
from hash08 import fold

def material_map(r,registry):
 H={int(e['hash'],16):e for e in registry['entries']}; M=registry['materials']; references=[]
 for k,ts in M.items():
  for t in ts:
   e=H.get(fold(t['filename'].lower().encode('ascii')));assert e is not None,t
   assert e['size']==t['size'],(t,e)
   exact=e['dimensions']==[t['width'],t['height']]
   assert exact or (e['dimensions'] is None and e['palette']==4096),(t,e)
   references.append(dict(material=k,filename=t['filename'],group=e['group'],hash=e['hash'],dimensions_match=exact))
 return H,M,references

def palette(pal,ix,mask):
 rgb=pal.astype(np.uint16);c=np.maximum((rgb[:,0]>>3)|((rgb[:,1]>>3)<<5)|((rgb[:,2]>>3)<<10),1)
 if mask and np.ptp(rgb[ix,3])>0:c=np.where(rgb[:,3]<32,0,c)
 return c.astype('<u2')
def upload(words,colors,ix,rect,clut):
 x,y,w,h=rect;cx,cy,cw,ch=clut;assert ix.shape==(h,w*2) and len(colors)==256 and x+w<=768 and y+h<=512
 words.extend([0xa0000000,cx|(cy<<16),(ch<<16)|cw]);words.extend(np.frombuffer(colors.tobytes(),'<u4').tolist());words.extend([0xa0000000,x|(y<<16),(h<<16)|w]);words.extend(np.frombuffer(ix.tobytes(),'<u4').tolist())
def apply(iso,out):
 r=records(iso);groups=list(pxt_groups(r[772][1]));registry=json.loads((out/'texture_registry.json').read_text()); H,M,refs=material_map(r,registry);registry['resolved_references']=refs;registry['limitation']='Folded MD4 filename keys validated against size and (where present) dimensions. Five multi-CLUT references have no image payload here.';(out/'texture_registry.json').write_text(json.dumps(registry,indent=2));rep=json.loads((out/'report.json').read_text());z=np.load(out/'farm06.npz');data={k:z[k] for k in z.files};old_groups={x['name']:x.get('group') for x in rep['bindings']};tex=[];words=[]
 for b in rep['bindings']:
  ts=M[b['material']];ts=[t for t in ts if t['texture_node'].startswith('the_hub_'+b['region']+'_')] if 'region' in b else ts;assert ts;es=[H[fold(t['filename'].lower().encode())] for t in ts];assert len(set(e['group'] for e in es))==1,b; e=es[0];i=e['group'];_,pal,imgs=groups[i];w,h,ix=imgs[0];assert len(pal)==256 and [w,h]==e['dimensions'];ix=np.asarray(Image.fromarray(ix).resize((64,64),Image.Resampling.NEAREST));# Alpha approximation: retain cutouts on foliage and hay overlay; recovered base ground is opaque.
  mask=b['name'] in ('largeivy','wheat','yellow_T','treeygrass_tr','sdgrass_T','onlyhay');c=palette(pal,ix,mask);upload(words,c,ix,b['vram'],b['clut']);tex.append(c[ix]);b.update(group=i,previous_group=old_groups[b['name']],source_refs=ts,binding='verified folded MD4 filename, dimensions and payload length',hash=e['hash'],alpha_policy='cutout approximation' if mask and np.ptp(pal[ix,3]) else 'opaque diagnostic',transparent_pixels_after=int((c[ix]==0).sum()))
 data['textures']=np.array(tex);np.savez_compressed(out/'farm06.npz',**data);p=out/'world.h';s=p.read_text();s=re.sub(r'#define WORLD_UPLOAD_WORDS \d+',f'#define WORLD_UPLOAD_WORDS {len(words)}',s);s=re.sub(r'(static const u32 worldupload\[WORLD_UPLOAD_WORDS\]=\{)[^}]+(\};)',lambda m:m[1]+','.join(str(x)+'u' for x in words)+m[2],s);p.write_text(s)
 # Actor: map source material names to texture nodes, exact filename lookup. Body is multi-stage; its base is explicitly named in the MRB.
 b=r[1130][1];actor=[];words=[];names=['spyro_spyro_body_lambert_spyro_tex_AlphaFactor127','spyro_spyro_wing_lambert_spyro_wing_tex_AlphaFactor127','spyro_spyro_R_eye_blinn_spyro_R_eye_texSrcAlpha_127_AlphaFactor127'];nd={n:q for _,n,q in nodes(b,0xdad78930)}
 for k,name in enumerate(names):
  q=nd[name];m=re.search(rb'[0-9A-F]{8}\.PXT',b[q:q+150]);filename=m.group().decode();e=H[fold(filename.lower().encode())];w,h,_,size=struct.unpack_from('<HHHI',b,q+m.end());assert e['dimensions']==[w,h] and e['size']==size;_,pal,imgs=groups[e['group']];ix=imgs[0][2];c=palette(pal,ix,False);upload(words,c,ix,[[320,0,128,256],[448,0,32,64],[512,0,32,64]][k],[768,k,256,1]); rgb=np.stack([(c[ix]&31)*8,((c[ix]>>5)&31)*8,((c[ix]>>10)&31)*8],axis=-1).astype(np.uint8);Image.fromarray(rgb).save(out/f'actor_tex_{k}.png');actor.append(dict(texture_node=name,filename=filename,group=e['group'],hash=e['hash'],size=size,dimensions=[w,h],previous_group=[303,411,429][k]))
 p=out/'scene.h';s=p.read_text();s=re.sub(r'#define UPLOAD_WORDS \d+',f'#define UPLOAD_WORDS {len(words)}',s);s=re.sub(r'(static const u32 upload\[UPLOAD_WORDS\]=\{)[^}]+(\};)',lambda m:m[1]+','.join(str(x)+'u' for x in words)+m[2],s);p.write_text(s)
 rep.update(material_candidates=len(tex),texture_vram_bytes=len(tex)*4608,texture_references=len(refs),unique_filenames=len({t['filename'] for t in refs}),validated_dimension_references=sum(x['dimensions_match'] for x in refs),actor_bindings=actor,verified_world_bindings=len(tex),material_changes=sum(b['group']!=b['previous_group'] for b in rep['bindings']),limitations='Exact base texture filename associations; PS2 multilayer blending, texture alpha/CLUT semantics, lighting and original animation still unresolved. Sparse collision, no streaming.');(out/'report.json').write_text(json.dumps(rep,indent=2));print('Bindings',len(tex),'changes',rep['material_changes'],'actor',actor,'references',len(refs))
