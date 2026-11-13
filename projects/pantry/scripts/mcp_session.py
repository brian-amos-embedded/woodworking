#!/usr/bin/env python3
"""Small real stdio MCP client for use by task scripts. No external packages."""
import json,os,pathlib,selectors,subprocess,time
class Session:
 def __init__(self,cli,work,design=None,timeout=60):
  self.work=pathlib.Path(work).resolve();self.work.mkdir(parents=True,exist_ok=True)
  self.log=open(self.work/'mcp-stderr.log','a');self.counter=0;self.timeout=timeout
  args=[str(cli),'mcp','--headless','--param-check','strict','--allow-path',str(self.work)]
  if design:args+=['--in',str(pathlib.Path(design).resolve())]
  self.p=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,env={**os.environ,'SOLIDCRAFT_GPU':'cpu'})
  self.pending=b''
  self.server=self.rpc('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'woodworking-solidcraft','version':'1'}})
  self.p.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n');self.p.stdin.flush()
 def rpc(self,method,params):
  self.counter+=1;ident=self.counter
  self.p.stdin.write((json.dumps({'jsonrpc':'2.0','id':ident,'method':method,'params':params})+'\n').encode());self.p.stdin.flush()
  deadline=time.monotonic()+self.timeout
  with selectors.DefaultSelector() as sel:
   sel.register(self.p.stdout,selectors.EVENT_READ)
   while True:
    while b'\n' in self.pending:
     line,self.pending=self.pending.split(b'\n',1)
     if not line.strip():continue
     result=json.loads(line)
     if result.get('id')!=ident:continue
     if 'error' in result:raise RuntimeError(result['error'])
     value=result['result']
     if value.get('isError'):raise RuntimeError(value)
     return value
    remaining=deadline-time.monotonic()
    if remaining<=0 or not sel.select(remaining):
     raise TimeoutError('MCP timeout; operation may still be running. Do not blindly resend it.')
    data=os.read(self.p.stdout.fileno(),65536)
    if not data:raise RuntimeError('MCP server exited; inspect mcp-stderr.log')
    self.pending+=data
 def call(self,name,args=None):return self.rpc('tools/call',{'name':name,'arguments':args or {}})
 def json(self,name,args=None):
  r=self.call(name,args)
  blocks=[c['text'] for c in r.get('content',[]) if c.get('type')=='text']
  if not blocks:return r
  try:return json.loads(blocks[0])
  except ValueError:return blocks[0]
 def close(self):
  if self.p.poll() is None:
   self.p.terminate()
   try:self.p.wait(timeout=10)
   except subprocess.TimeoutExpired:self.p.kill();self.p.wait()
  self.log.close()
 def __enter__(self):return self
 def __exit__(self,*args):self.close()
