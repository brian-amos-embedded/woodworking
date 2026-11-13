#!/usr/bin/env python3
"""Read SKP locally with pinned skppy; export component geometry without changing source."""
import argparse,collections,hashlib,importlib.metadata,json,pathlib
import numpy as np
import skppy

def point(p):return [p.x,p.y,p.z]
def extract(source,target):
 if importlib.metadata.version('skppy')!='0.10.0':raise ValueError('Use pinned skppy 0.10.0')
 model=skppy.load(str(source));lookup={d.id:d for d in model.definitions}
 matches=[d for d in model.definitions if d.name==target]
 if len(matches)!=1:raise ValueError(f'Expected one exact target definition, found {len(matches)}')
 definitions={}
 def visit(d,stack):
  key=str(d.id)
  if key in stack:raise ValueError('Component cycle')
  if key in definitions:return
  e=d.entities
  if e.images:raise ValueError(f'Unsupported image entities in {d.name}; extraction stopped')
  vertices={str(v.id):point(v.position) for v in e.vertices}
  edges={str(x.id):{'id':str(x.id),'vertices':[str(x.start_vertex_id),str(x.end_vertex_id)],'flags':x.flags,'layer_id':x.layer_id} for x in e.edges}
  faces=[]
  for f in e.faces:
   loops=[]
   for outer,loop in [(True,f.outer_loop)]+[(False,l) for l in f.inner_loops]:
    uses=[{'edge_id':str(u.edge_id),'reversed':u.reversed} for u in loop.edge_uses]
    ids=[]
    ends=[]
    for u in uses:
     a,b=edges[u['edge_id']]['vertices']
     if u['reversed']:a,b=b,a
     ids.append(a);ends.append(b)
    if not ids or any(ends[i]!=ids[(i+1)%len(ids)] for i in range(len(ids))):raise ValueError(f'Broken face loop {f.id}')
    loops.append({'outer':outer,'vertex_ids':ids,'edge_uses':uses})
   faces.append({'id':str(f.id),'plane':list(f.plane),'front_material_id':f.front_material_id,'back_material_id':f.back_material_id,'layer_id':f.layer_id,'loops':loops})
  children=[]
  for kind,items in [('component',e.component_instances),('group',e.groups)]:
   for i in items:
    if i.definition_id not in lookup:raise ValueError('Unresolved component reference')
    if len(i.transform)!=13:raise ValueError('Unexpected transform encoding')
    matrix=skppy.Transform(i.transform).matrix
    children.append({'id':str(i.id),'name':i.name,'kind':kind,'definition_id':str(i.definition_id),'raw_transform13':list(i.transform),'matrix4x4':matrix.tolist(),'material_id':i.material_id,'layer_id':i.layer_id})
    visit(lookup[i.definition_id],stack|{key})
  definitions[key]={'id':key,'name':d.name,'guid_hex':d.guid.hex() if isinstance(d.guid,bytes) else str(d.guid),'vertices_in':vertices,'edges':edges,'faces':faces,'children':children}
 visit(matches[0],set())
 occurrences=[]
 def expand(key,matrix,path):
  row=definitions[key]
  if row['faces']:
   verts=np.array(list(row['vertices_in'].values()),dtype=float)
   v=np.c_[verts,np.ones(len(verts))]@matrix.T
   if np.any(np.abs(v[:,3])<1e-12):raise ValueError('Invalid homogeneous transform')
   xyz=v[:,:3]/v[:,3,None]
   occurrences.append({'instance_path':path,'definition_id':key,'name':row['name'],'matrix4x4':matrix.tolist(),'assembly_bbox_in':[xyz.min(0).tolist(),xyz.max(0).tolist()]})
  for i in row['children']:expand(i['definition_id'],matrix@np.array(i['matrix4x4']),path+[i['id']])
 root=str(matches[0].id);expand(root,np.eye(4),[])
 counts=collections.Counter(o['definition_id'] for o in occurrences)
 return {'schema_version':2,'source':{'filename':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'header_version':model.header.version_string,'parser':'skppy','parser_version':'0.10.0'},'units':'inches','transform_convention':'matrix4x4 is row-major; multiply homogeneous column vectors; divide xyz by w; child world=parent@local. raw_transform13 is skppy native, NOT Ruby column-major16.','target_definition':root,'definitions':definitions,'materials':[{'id':m.id,'name':m.name} for m in model.materials],'occurrences':occurrences,'part_counts':[{'definition_id':key,'name':definitions[key]['name'],'quantity':n} for key,n in counts.items()],'limitations':['Independent parser; compare dimensions and render against source before fabrication.','Target is in its definition-local frame; outer pantry placements excluded.','Hidden/tag visibility filtering is not applied; parser may not expose all face/instance visibility.','Textures, UVs, attributes, curves, guides, annotations and design constraints are not exported. Polygon boundaries and edge flags are retained.','A geometry-bearing definition is an occurrence, not automatically a confirmed manufacturing part.','Extraction is not a SolidCraft import or a fabrication release.']}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--target',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 source=pathlib.Path(a.input).resolve();out=pathlib.Path(a.output).resolve()
 if source==out:raise ValueError('Cannot overwrite source')
 result=extract(source,a.target)
 from validate_extract import validate
 report=validate(result)
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,allow_nan=False))
 print(json.dumps(report,indent=2))
