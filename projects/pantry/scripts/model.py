"""Rebuild and verify the pantry soda organizer."""
import argparse
import json
from pathlib import Path

from cabinet_model import INCH, check_interference, resolve, solid_commands, verify
from mcp_session import Session

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'output')
    args = parser.parse_args()
    out = args.output.resolve()
    project = json.loads((ROOT / 'project.json').read_text())
    parts = resolve(project)
    commands = solid_commands(project)

    def write(filename, data):
        (out / filename).write_text(json.dumps(data, indent=2) + '\n')

    def change(session, **changes):
        result = session.json('execute', {'command': 'parameters.change', 'params': {
            'changes': {'cab_' + name.lower(): f'{value} in' for name, value in changes.items()}
        }})
        assert not result.get('errors'), result

    with Session(args.cli.resolve(), out, timeout=120) as session:
        session.json('skill_reference', {'skill': 'solidcraft-modeling'})
        session.json('inspect_design', {'measure': False, 'sketches': False})
        write('replay.json', commands)
        for stage, batch in commands.items():
            result = session.json('batch', {'commands': batch, 'verbose': False})
            if not result.get('ok') or result.get('completed') != len(batch):
                raise RuntimeError(f'{stage}: {str(result)[:2500]}')
            if stage == 'blanks':
                verify(session, parts, machined=False)
            print(stage, len(batch), flush=True)
        write('measurement.json', verify(session, parts))
        write('interference.json', check_interference(session))
        variant = {'W': project['parameters_in']['W'] + 2, 'T': .71875}
        change(session, **variant)
        write('revision-test.json', {'changed_inches': variant,
                                    'measurement': verify(session, resolve(project, variant)),
                                    'interference': check_interference(session)})
        change(session, **{name: project['parameters_in'][name] for name in variant})
        verify(session, parts)
        session.json('save', {'path': str(out / 'soda-org-2.sc')})
        for ext in ('step', 'glb'):
            session.json('export', {'path': str(out / f'soda-org-2.{ext}')})
        for view in ('iso', 'front', 'back'):
            session.call('screenshot', {'path': str(out / f'{view}.png'), 'view': view, 'width': 1000,
                                        'height': 900, 'grid': False, 'axes': False})
    with Session(args.cli.resolve(), out, design=out / 'soda-org-2.sc') as session:
        write('measurement-reopened.json', verify(session, parts))
        groups = {
            'SIDE-L': ['SIDE-L'], 'SIDE-R': ['SIDE-R'], 'DIV': ['DIV-1'],
            'TOPBOT': ['BOT'], 'SHELF-OUT': ['SH-L1'], 'SHELF-CENTER': ['SH-C1'],
            'BACK': ['BACK'], 'STILE': ['ST-1'], 'RAIL': ['RA-11'],
            'FRAME': [p['id'] for p in parts if p['material'] == 'maple'],
        }
        for group, ids in groups.items():
            session.json('execute', {'command': 'browser.visibility', 'params': {
                'visible': True, 'isolate': True, 'items': ids
            }})
            camera = {'view': 'iso'}
            if group == 'SIDE-R':
                box = next(p for p in parts if p['id'] == 'SIDE-R')
                center = [(a + b / 2) * INCH for a, b in zip(box['corner'], box['size'])]
                camera = {'camera': {'target': center, 'yaw': .85, 'pitch': .35, 'distance': 1350}}
            session.call('screenshot', {'path': str(out / f'part-{group}.png'),
                                        'width': 720, 'height': 560,
                                        'grid': False, 'axes': False, **camera})


if __name__ == '__main__':
    main()
