#!/usr/bin/env python3
"""Exercise the real stdio MCP server; fixtures are NOT the pantry model."""
import argparse,json,os,pathlib,selectors,subprocess,math
ap=argparse.ArgumentParser();ap.add_argument('--cli',default='solidcraft-cli');ap.add_argument('--output',default='outputs');a=ap.parse_args()
out=pathlib.Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
log=open(out/'mcp-stderr.log','w'); transcript=[]
p=subprocess.Popen([a.cli,'mcp','--headless','--param-check','strict','--allow-path',str(out)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=log,text=True,env={**os.environ,'SOLIDCRAFT_GPU':'cpu'})
def rpc(method,params):
 req={'jsonrpc':'2.0','id':len(transcript)+1,'method':method,'params':params};p.stdin.write(json.dumps(req)+'\n');p.stdin.flush()
 sel=selectors.DefaultSelector();sel.register(p.stdout,selectors.EVENT_READ)
 if not sel.select(60):raise TimeoutError(method)
 sel.close();r=json.loads(p.stdout.readline());transcript.append({'request':req,'response':r})
 if 'error' in r:raise RuntimeError(r)
 v=r['result']
 if v.get('isError'):raise RuntimeError(v)
 return v

def call(name,args):
 r=rpc('tools/call',{'name':name,'arguments':args})
 text=[c['text'] for c in r.get('content',[]) if c['type']=='text']
 if text:
  try:return json.loads(text[0])
  except ValueError:return text[0]
 return r

def execute(command,params):return call('execute',{'command':command,'params':params})
try:
 init=rpc('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'woodworking-trial','version':'0.1'}})
 p.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');p.stdin.flush()
 ts=rpc('tools/list',{});json.dump(ts,open(out/'tools.json','w'),indent=2)
 for command in ['solid.box','parameters.change','doc.open']:
  json.dump(call('describe_command',{'id':command}),open(out/(command+'.schema.json'),'w'),indent=2)
 execute('parameters.change',{'name':'rail_length','expression':'24 in'})
 execute('solid.box',{'length':'rail_length','width':'2 in','height':'0.75 in','body_name':'TEST-maple-rail','name':'TEST rail blank'})
 m=call('measure',{'summary':True});json.dump(m,open(out/'rail-before.json','w'),indent=2)
 def check(m,L):
  assert len(m['bodies'])==1,m
  b=m['bodies'][0];assert b['closed'],b
  assert math.isclose(m['total']['volume_mm3'],L*50.8*19.05,rel_tol=1e-7),m
  for x,y in zip(b['bbox']['min'],[0,0,0]):assert abs(x-y)<1e-5
  for x,y in zip(b['bbox']['max'],[L,50.8,19.05]):assert abs(x-y)<1e-5
 check(m,609.6)
 execute('parameters.change',{'name':'rail_length','expression':'30 in'})
 after=call('measure',{'summary':True});check(after,762);json.dump(after,open(out/'rail-after.json','w'),indent=2)
 execute('parameters.change',{'name':'rail_length','expression':'24 in'});check(call('measure',{'summary':True}),609.6)
 call('save',{'path':str(out/'test-rail.sc')})
 for ext in ['step','glb']:call('export',{'path':str(out/('test-rail.'+ext))})
 call('screenshot',{'path':str(out/'test-rail.png'),'width':900,'height':500,'grid':False,'axes':False})
 call('open',{'path':str(out/'test-rail.sc')});check(call('measure',{'summary':True}),609.6)
 summary={'passed':True,'server':init['serverInfo'],'checks':['initialize','tools/list','create 24 x 2 x 0.75 inch solid','exact bounding box and volume','parameter change to 30 inches and restore','save/reopen','STEP export','GLB export','CPU screenshot'],'fixture':'test rail only; pantry not imported'}
 json.dump(summary,open(out/'smoke-result.json','w'),indent=2);print(json.dumps(summary,indent=2))
finally:
 # Omit embedded image bytes from the transcript, retaining text and paths.
 for row in transcript:
  for block in row['response'].get('result',{}).get('content',[]):
   if block.get('type')=='image':block['data']='<omitted; see PNG>'
 json.dump(transcript,open(out/'mcp-transcript.json','w'),indent=2)
 p.terminate();p.wait(timeout=10);log.close()
