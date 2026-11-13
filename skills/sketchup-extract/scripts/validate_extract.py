#!/usr/bin/env python3
"""Validate v2 extraction references and topology structure; not watertight CAD."""
import argparse,json,math,pathlib

def need(ok,msg):
 if not ok:raise ValueError(msg)
def vector(v,n):need(isinstance(v,list) and len(v)==n and all(isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x) for x in v),'Invalid numeric vector')
def matrix(m):
 need(isinstance(m,list) and len(m)==4,'Invalid matrix')
 for row in m:vector(row,4)
def validate(d):
 need(d['schema_version']==2 and d['units']=='inches','Unsupported schema or units')
 defs=d['definitions'];need(d['target_definition'] in defs,'Missing target')
 for key,row in defs.items():
  need(row['id']==key and isinstance(row['name'],str),'Invalid definition')
  vs=row['vertices_in'];es=row['edges']
  for v in vs.values():vector(v,3)
  for eid,e in es.items():
   need(eid==e['id'] and len(e['vertices'])==2,'Invalid edge')
   need(all(v in vs for v in e['vertices']),'Dangling vertex')
  ids=set(es)|set(vs)
  for f in row['faces']:
   need(f['id'] not in ids,'Duplicate entity id');ids.add(f['id']);vector(f['plane'],4)
   need(bool(f['loops']) and all(isinstance(l['outer'],bool) for l in f['loops']),'Invalid outer flag')
   need(sum(l['outer'] for l in f['loops'])==1,'Expected one outer loop')
   for loop in f['loops']:
    vertices=loop['vertex_ids'];uses=loop['edge_uses'];need(len(vertices)>=3 and len(vertices)==len(uses),'Invalid loop')
    for j,u in enumerate(uses):
     need(isinstance(u['reversed'],bool) and u['edge_id'] in es,'Invalid edge use')
     ends=es[u['edge_id']]['vertices'][::-1] if u['reversed'] else es[u['edge_id']]['vertices']
     need(ends==[vertices[j],vertices[(j+1)%len(vertices)]],'Broken loop topology')
  for c in row['children']:
   need(c['id'] not in ids,'Duplicate entity id');ids.add(c['id'])
   need(c['definition_id'] in defs,'Dangling definition');vector(c['raw_transform13'],13);matrix(c['matrix4x4'])
 states={}
 def walk(k):
  need(states.get(k)!=1,'Cycle')
  if states.get(k)==2:return
  states[k]=1
  for c in defs[k]['children']:walk(c['definition_id'])
  states[k]=2
 for k in defs:walk(k)
 from collections import Counter
 counts=Counter()
 for o in d['occurrences']:
  need(o['definition_id'] in defs,'Unknown occurrence definition');matrix(o['matrix4x4'])
  need(len(o['assembly_bbox_in'])==2,'Invalid bounds')
  for v in o['assembly_bbox_in']:vector(v,3)
  counts[o['definition_id']]+=1
 need(counts=={p['definition_id']:p['quantity'] for p in d['part_counts']},'Count mismatch')
 return {'structure_valid':True,'target':defs[d['target_definition']]['name'],'definitions':len(defs),'geometry_occurrences':sum(counts.values()),'unique_geometry_definitions':len(counts),'geometry_validated':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('input');a=ap.parse_args();print(json.dumps(validate(json.loads(pathlib.Path(a.input).read_text())),indent=2))
