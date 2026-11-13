"""Replay the cabinet specification in SolidCraft and verify the resulting solids."""
import argparse
import ast
import itertools
import json
import math
import operator
from pathlib import Path
import re

from mcp_session import Session

ROOT = Path(__file__).resolve().parents[1]
INCH = 25.4
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def evaluate(expression, values):
    if isinstance(expression, (int, float)):
        return expression

    def visit(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            return values[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -visit(node.operand)
        if isinstance(node, ast.BinOp):
            return OPS[type(node.op)](visit(node.left), visit(node.right))
        raise ValueError(ast.dump(node))

    return visit(ast.parse(expression, mode='eval').body)


def resolve(project, overrides=None):
    values = project['parameters_in'] | (overrides or {})
    for name, expression in project['derived_expressions'].items():
        values[name] = evaluate(expression, values)

    def resolve_box(box):
        return box | {field: [evaluate(item, values) for item in box[field]]
                      for field in ('corner', 'size')}

    return [resolve_box(part) | {'cuts': [resolve_box(cut) for cut in part['cuts']]}
            for part in project['parts']]


def box_edges(box):
    return list(zip(box['corner'], map(operator.add, box['corner'], box['size'])))


def net_volume(part):
    """Partition the blank on cutter boundaries and count the remaining cells."""
    blank = box_edges(part)
    cuts = [box_edges(cut) for cut in part['cuts']]
    planes = [sorted({low, high} | {v for cut in cuts for v in cut[axis] if low < v < high})
              for axis, (low, high) in enumerate(blank)]
    cells = itertools.product(*(zip(p, p[1:]) for p in planes))
    volume = 0
    for cell in cells:
        center = [(a + b) / 2 for a, b in cell]
        if not any(all(lo < v < hi for v, (lo, hi) in zip(center, cut)) for cut in cuts):
            volume += math.prod(b - a for a, b in cell)
    return volume


def solid_commands(project):
    def length(value):
        if isinstance(value, (int, float)):
            return f'{value} in'
        return re.sub(r'[A-Za-z_]\w*', lambda match: 'cab_' + match[0].lower(), value)

    def command(command_id, **params):
        return {'command': command_id, 'params': params}

    def box(item, **extra):
        x, y, z = map(length, item['size'])
        return command('solid.box', name=item['name'], length=x, width=y, height=z,
                       corner=list(map(length, item['corner'])), **extra)

    params = [command('parameters.change', name='cab_' + name.lower(), expression=length(value))
              for name, value in (project['parameters_in'] | project['derived_expressions']).items()]
    solids = [box(part, body_name=part['id']) for part in project['parts']]
    cuts = [box(cut, operation='cut', targets=[part['id']])
            for part in project['parts'] for cut in part['cuts']]
    colors = {'plywood_3_4': '#d7b688', 'plywood_1_4': '#af8961', 'maple': '#ebc391', 'butcherblock': '#c49255', 'lighting': '#63768b'}
    finish = [command('appearance.assign', bodies=[p['id'] for p in project['parts'] if p['material'] == material],
                      color=color) for material, color in colors.items() if any(p['material'] == material for p in project['parts'])]
    return {'parameters': params, 'blanks': solids, 'joinery': cuts, 'appearance': finish}


def verify(session, parts, machined=True):
    data = session.json('measure', {'summary': True})
    bodies = {body['name']: body for body in data['bodies']}
    assert set(bodies) == {part['id'] for part in parts}, list(bodies)
    for part in parts:
        body = bodies[part['id']]
        expected_volume = net_volume(part) if machined else math.prod(part['size'])
        assert body['closed'], part['id']
        assert math.isclose(body['volume_mm3'], expected_volume * INCH**3, abs_tol=0.3), (part['id'], body, expected_volume)
        for (low, high), actual_low, actual_high in zip(box_edges(part), body['bbox']['min'], body['bbox']['max']):
            assert math.isclose(low * INCH, actual_low, abs_tol=.002), (part['id'], low, actual_low)
            assert math.isclose(high * INCH, actual_high, abs_tol=.002), (part['id'], high, actual_high)
    return data


def check_interference(session):
    result = session.json('execute', {'command': 'inspect.interference', 'params': {'budget_s': 90}})
    assert not result.get('unchecked') and not result.get('truncated') and not result.get('budget_exceeded'), result
    assert result['interferences'] == [], result['interferences']
    return result


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
