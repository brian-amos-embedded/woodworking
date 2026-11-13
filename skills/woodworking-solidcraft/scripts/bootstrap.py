#!/usr/bin/env python3
"""Install a pinned headless SolidCraft binary into a disposable cache."""
import argparse,hashlib,json,os,pathlib,platform,subprocess,tarfile,urllib.request
VERSION='0.40.1'
SHA256='0244019d315b37fa9506e09a4ae1cada50713f557dd6be413bd578147350966e'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);a=ap.parse_args()
 if platform.system()!='Linux' or platform.machine() not in ('x86_64','AMD64'):
  raise SystemExit('Pinned runtime supports Linux x86_64 only; select and verify an official build for this platform.')
 cache=pathlib.Path(a.cache).resolve();cache.mkdir(parents=True,exist_ok=True)
 name=f'solidcraft-{VERSION}-linux-x86_64';archive=cache/(name+'.tar.gz')
 def digest(p):
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  return h.hexdigest()
 if not archive.exists() or digest(archive)!=SHA256:
  temporary=cache/(name+'.download')
  with urllib.request.urlopen(f'https://github.com/tangency-labs/solidcraft/releases/download/v{VERSION}/{name}.tar.gz',timeout=60) as response,temporary.open('wb') as out:
   import shutil
   shutil.copyfileobj(response,out)
  if digest(temporary)!=SHA256:
   temporary.unlink();raise SystemExit('Archive checksum mismatch; installation stopped.')
  temporary.replace(archive)
 # Re-extract the verified archive to avoid trusting modified executable cache content.
 with tarfile.open(archive) as tar:tar.extractall(cache,filter='data')
 cli=cache/name/'bin/solidcraft-cli'
 subprocess.run([str(cli),'--help'],stdout=subprocess.DEVNULL,check=True,timeout=30)
 print(json.dumps({'cli':str(cli),'version':VERSION,'archive_sha256':SHA256}))
if __name__=='__main__':main()
