#!/usr/bin/env python3
"""Inspect container metadata and thumbnails without pretending to decode SKP geometry."""
import argparse,hashlib,json,pathlib,re,zipfile
ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--output',required=True);ap.add_argument('--target',default='soda org 2');a=ap.parse_args()
p=pathlib.Path(a.input);out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=True)
b=p.read_bytes();header=b[:100].decode('utf-16le',errors='ignore');v=re.search(r'\{([0-9.]+)\}',header)
r={'input_name':p.name,'sha256':hashlib.sha256(b).hexdigest(),'header_version':v.group(1) if v else None,'target':a.target,'geometry_decoded':False,'limitations':['Thumbnail names do not establish hierarchy, dimensions, or instance quantities.']}
if zipfile.is_zipfile(p):
 with zipfile.ZipFile(p) as z:
  if sum(i.file_size for i in z.infolist())>512*1024*1024:raise SystemExit('Archive too large for lightweight inspection')
  r['thumbnail_names']=[pathlib.PurePosixPath(n).stem for n in z.namelist() if n.startswith('thumbnails/')]
  r['target_name_bytes_present']=a.target.encode() in z.read('model.dat') if 'model.dat' in z.namelist() else False
  candidates=[n for n in z.namelist() if n.startswith('thumbnails/') and pathlib.PurePosixPath(n).stem==a.target]
  if len(candidates)==1:
   name=candidates[0];suffix=pathlib.PurePosixPath(name).suffix.lower()
   if suffix in ('.jpg','.jpeg','.png'):
    dst=out/('target-preview'+suffix);dst.write_bytes(z.read(name));r['preview_file']=dst.name
else:r['limitations'].append('Legacy/non-ZIP SKP; no embedded archive read.')
(out/'inspection.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
