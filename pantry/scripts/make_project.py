import json,pathlib
P=pathlib.Path(__file__).resolve().parents[1]
params={'W':26,'H':36.25,'D':18.125,'T':.75,'FT':.75,'F':2,'G':.25,'B':.25,'bottom_z':3.5,'frame_bottom':2.25,'step':8,'back_clearance':.0625,'base_h':3.5,'base_d':1.5,'wire_h':.25,'wire_d':.25}
expr={'bay':'(W-4*F)/3','div1':'F+bay+F/2-T/2','div2':'2*F+2*bay+F/2-T/2','rear':'D-FT','shelf_depth':'rear-FT','panel_start':'F-G','panel_width':'W-2*F+2*G'}
parts=[]
def part(id,group,name,corner,size,source,material='plywood_3_4',grain_axis=2,cuts=None):
 parts.append({'id':id,'group':group,'name':name,'corner':corner,'size':size,'source_definition':source,'material':material,'grain_axis':grain_axis,'cuts':cuts or []})
def cut(name,corner,size):return {'name':name,'corner':corner,'size':size}
levels=['bottom_z','bottom_z+step','bottom_z+2*step','bottom_z+3*step','H-T']
for side,x,groovex in [('L','F-T','F-G'),('R','W-F','W-F')]:
 cuts=[cut('shelf-dado-'+str(j),[groovex,'FT',z],['G','D-FT','T']) for j,z in enumerate(levels)]
 cuts.append(cut('back-groove',[groovex,'rear',0],['G','B','H']))
 cuts.append(cut('baseboard-relief',[x,'D-base_d',0],['T','base_d','base_h']))
 part('SIDE-'+side,'SIDE','Outer side '+side,[x,'FT',0],['T','D-FT','H'],'86774',cuts=cuts)
for i,x in enumerate(['div1','div2']):
 cuts=[]
 for j,z in enumerate(levels[1:4]):
  for label,cx in [('left',x),('right',x+'+T-G')]:cuts.append(cut('dado-'+str(j)+'-'+label,[cx,'FT',z],['G','shelf_depth','T']))
 for level in ['bottom_z+step+T-F','bottom_z+2*step+T-F','bottom_z+3*step+T-F','H-F']:
  cuts.append(cut('light-wire-relief',[x,'FT',level+'-wire_h'],['T','wire_d','wire_h']))
 part('DIV-'+str(i+1),'DIV','Divider '+str(i+1),[x,'FT','bottom_z+T-G'],['T','shelf_depth','H-T+G-(bottom_z+T-G)'],'87277',cuts=cuts)
for label,z,cz in [('BOT','bottom_z','bottom_z+T-G'),('TOP','H-T','H-T')]:
 cuts=[cut('divider-dado-'+str(i),[x,'FT',cz],['T','D-FT','G']) for i,x in enumerate(['div1','div2'])]
 cuts.append(cut('back-groove',['panel_start','rear',cz],['panel_width','B','G']))
 part(label,'TOPBOT',label.title(),['panel_start','FT',z],['panel_width','D-FT','T'],'89912',grain_axis=0,cuts=cuts)
spans=[('L','F-G','div1+G-(F-G)','89139','SHELF-OUT'),('C','div1+T-G','div2+G-(div1+T-G)','89502','SHELF-CENTER'),('R','div2+T-G','W-F+G-(div2+T-G)','89139','SHELF-OUT')]
for j,z in enumerate(levels[1:4]):
 for label,x,w,src,group in spans:part('SH-'+label+str(j+1),group,'Shelf '+label+str(j+1),[x,'FT',z],[w,'shelf_depth','T'],src,grain_axis=1)
part('BACK','BACK','Back',['panel_start+back_clearance/2','rear','bottom_z+T-G+back_clearance/2'],['panel_width-back_clearance','B','H-T+G-(bottom_z+T-G)-back_clearance'],'90470',material='plywood_1_4',grain_axis=2)
for j,x in enumerate([0,'F+bay','2*F+2*bay','W-F']):part('ST-'+str(j+1),'STILE','Stile '+str(j+1),[x,0,'frame_bottom'],['F','FT','H-frame_bottom'],'87665',material='maple',grain_axis=2)
for j,top in enumerate(['frame_bottom+F','bottom_z+step+T','bottom_z+2*step+T','bottom_z+3*step+T','H']):
 for i,x in enumerate(['F','2*F+bay','3*F+2*bay']):part('RA-'+str(j+1)+str(i+1),'RAIL','Rail '+str(j+1)+str(i+1),[x,0,top+'-F'],['bay','FT','F'],'87913',material='maple',grain_axis=0)
project={'name':'Soda organizer 2','revision':'R3','status':'Reviewed geometry; nominal-stock fabrication draft','parameters_in':params,'derived_expressions':expr,'parts':parts,'shop':{'kerf_in':.125,'hardwood_default_board_in':[6,96],'sheet_in':[48,96],'edge_trim_in':.25,'hardwood_rough_width_allowance_in':.125,'hardwood_rough_length_allowance_in':1.0,'back_total_edge_clearance_in':.0625,'grain':'sheet grain along 96 inch; longest shelf dimension; top/bottom across cabinet width'},'confirmed':['Normalize source dimensions to practical sizes','Saw kerf 1/8 inch','Use nominal 1/4 inch plywood back'],'assumptions':['3/4 inch stock modeled exactly 0.750 inch; measure actual plywood before machining.','1/4 inch back modeled exactly 0.250 inch; test-fit grooves to actual panel.','Dado depth 1/4 inch supported by source geometry; exact-width nominal dado, no extra clearance.','Back width and height each shortened 1/16 inch for assembly clearance.','Hardwood face frame: butt joints, glue and pocket screws; screw boring not modeled.','Sheet perimeter trim 1/4 inch each edge; verify actual sheet size and edge condition.','Hardwood rough allowance: +1/8 inch width, +1 inch length.','Run side dados, side back grooves and panel divider dados through; use stopped cuts only where an exit must be hidden or a functional constraint requires them.','No doors or hardware added; source organizer has neither.']}
(P/'project.json').write_text(json.dumps(project,indent=2))
print(len(parts),'parts')
