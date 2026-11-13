"""Build the native CAD, verification results and optional shop packs for a project."""
import argparse
from pathlib import Path
import subprocess
import sys
import json
import re

from cabinet_model import INCH, check_interference, resolve, solid_commands, verify
from mcp_session import Session
from project_config import load_project, read_json


def model_spec(root, filename):
    spec = read_json(root / filename)
    for include in spec.get('includes', []):
        source = model_spec(root, include['spec'])
        prefix = include['prefix']

        def expression(value):
            if isinstance(value, str):
                return re.sub(r'[A-Za-z_]\w*', lambda match: prefix + match[0], value)
            return value

        def box(item):
            return dict(item, corner=list(map(expression, item['corner'])),
                        size=list(map(expression, item['size'])))

        for field in ('parameters_in', 'derived_expressions'):
            for key, value in source[field].items():
                target = prefix + key
                if target in spec[field]:
                    raise ValueError(f'Duplicate model parameter: {target}')
                spec[field][target] = expression(value)
        spec.setdefault('shared_components', []).extend(source.get('shared_components', []))
        spec['parts'].extend(dict(box(part), cuts=[box(cut) for cut in part['cuts']])
                             for part in source['parts'])
    return spec


def assemble_components(session, spec, parts, variant, commands):
    """Promote bodies and place explicitly declared, geometrically identical copies."""
    def execute(command, **params):
        step = dict(command=command, params=params)
        commands.append(step)
        return session.json('execute', step)

    names = {p['id']: p['id'] for p in parts}
    by_id = {p['id']: p for p in parts}
    alternate = {p['id']: p for p in resolve(spec, variant)} if variant else by_id

    def signature(part):
        return (part['material'], part.get('grain_axis'), part['size'], [
            (cut['size'], [round(x-y, 8) for x,y in zip(cut['corner'],part['corner'])])
            for cut in part['cuts']])

    copies = {}
    for primary, *instances in spec.get('shared_components', []):
        for instance in instances:
            if instance in copies or instance == primary:
                raise ValueError(f'Repeated component occurrence: {instance}')
            offsets = []
            for model in (by_id, alternate):
                a, b = model[primary], model[instance]
                if signature(a) != signature(b):
                    raise ValueError(f'Component geometry differs: {primary}, {instance}')
                offsets.append([round(y-x, 8) for x,y in zip(a['corner'], b['corner'])])
            if offsets[0] != offsets[1]:
                raise ValueError(f'Occurrence translation changes with parameters: {instance}')
            copies[instance] = primary, offsets[0]

    if copies:
        execute('solid.remove', bodies=list(copies))
    definitions = execute('component.from_bodies', bodies=[key for key in names if key not in copies])
    component_ids = {row['body']: row['component'] for row in definitions['components']}
    for instance, (primary, offset) in copies.items():
        result = execute('occurrence.copy', component=component_ids[primary],
                         translate=[v*INCH for v in offset])
        tree = execute('component.list')
        component = next(c for c in tree['components'] if c['id'] == result['component'])
        occurrence = next(o for o in component['occurrences'] if o['id'] == result['occurrence'])
        names[instance] = f"{primary} ({occurrence['name']})"
    return names


def build_model(cli, root, out, model):
    name, prefix = model['name'], model['prefix']
    spec = model_spec(root, model['spec'])
    parts = resolve(spec)
    design = out / f'{name}.sc'

    def write(filename, value):
        (out / f'{prefix}{filename}.json').write_text(json.dumps(value, indent=2) + '\n')

    def shot(session, path, dimensions, camera):
        session.call('screenshot', dict(path=str(path), width=dimensions[0],
                     height=dimensions[1], grid=False, axes=False, **camera))

    def change(session, values):
        result = session.json('execute', {'command':'parameters.change','params':{
            'changes':{f'cab_{k.lower()}':f'{v} in' for k,v in values.items()}}})
        if result.get('errors'):
            raise RuntimeError(result['errors'])

    with Session(cli, out, timeout=120) as session:
        commands = solid_commands(spec)
        write('replay', commands)
        for stage, batch in commands.items():
            if not batch:
                continue
            result = session.json('batch', {'commands':batch,'verbose':False})
            if not result.get('ok') or result.get('completed') != len(batch):
                raise RuntimeError(f'{stage}: {result}')
            if stage == 'blanks':
                verify(session, parts, machined=False)
        write('measurement', verify(session, parts))
        write('checks' if prefix else 'interference', check_interference(session))
        if test := model.get('test'):
            change(session, test)
            write('revision-test', {'changed_inches':test,
                  'measurement':verify(session, resolve(spec,test)),
                  'interference':check_interference(session)})
            change(session, {k:spec['parameters_in'][k] for k in test})
            verify(session, parts)
        assembly_commands = []
        names = assemble_components(session, spec, parts, model.get('test'), assembly_commands)
        write('replay', commands | {'assembly': assembly_commands})
        write('measurement', verify(session, parts, body_names=names))
        write('checks' if prefix else 'interference', check_interference(session))
        if test:
            change(session, test)
            verify(session, resolve(spec, test), body_names=names)
            check_interference(session)
            change(session, {k:spec['parameters_in'][k] for k in test})
        session.json('save', {'path':str(design)})
        for ext in model.get('exports', []):
            session.json('export', {'path':str(out / f'{name}.{ext}')})
        for view in model.get('views', []):
            filename = name if prefix and view == 'iso' else prefix + view
            shot(session, out / f'{filename}.png', (1000,900), {'view':view})
    with Session(cli, out, design=design) as session:
        write('measurement-reopened', verify(session, parts, body_names=names))
        for label, ids in model.get('isolated', {}).items():
            session.json('execute', {'command':'browser.visibility','params':{
                'visible':True,'isolate':True,'items':[names[key] for key in ids]}})
            camera = {'view':'iso'}
            if settings := model.get('camera', {}).get(label):
                part = next(p for p in parts if p['id'] == ids[0])
                center = [(a+b/2)*INCH for a,b in zip(part['corner'],part['size'])]
                camera = {'camera':dict(settings,target=center)}
            shot(session, out / f'{prefix}part-{label}.png', (720,560), camera)
    if prefix:
        write('spec', spec)
    print(f'{name}: {len(parts)} bodies verified', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--cli', required=True, type=Path)
    args = parser.parse_args()
    root = args.project.resolve()
    cfg = load_project(root)
    out = root / 'output'
    out.mkdir(exist_ok=True)
    for model in cfg['models']:
        build_model(args.cli.resolve(), root, out, model)
    if cfg.get('report') == 'pantry-r3':
        for script in ('pantry_cutlist.py','pantry_side_pack.py'):
            subprocess.run([sys.executable, str(Path(__file__).with_name(script)), str(root)], check=True)
        (out/'soda-org-2-cutlist.pdf').replace(out/'soda-organizer-R4-shop-pack.pdf')
    elif cfg.get('report'):
        raise ValueError(f"Unknown report template: {cfg['report']}")


if __name__ == '__main__':
    main()
