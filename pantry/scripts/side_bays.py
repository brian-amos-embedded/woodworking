"""Build the two field-fit pantry bays in the organizer's coordinate system."""
import argparse
import json
from pathlib import Path

from model import ROOT, Session, check_interference, resolve, solid_commands, verify


def specification():
    center = json.loads((ROOT / 'project.json').read_text())
    parts = []
    def add(key, material, corner, size, cuts=()):
        parts.append(dict(id=key, name=key, material=material, corner=corner,
                          size=size, cuts=list(cuts)))
    parameters = {'bay': 20.75, 'center': 26, 'depth': 18.125, 'height': 36.25,
                  'top_t': 1.5, 'stock': .75, 'rail_h': 2, 'cleat_h': 1, 'lap': .5,
                  'nose': 1.5, 'cleat_travel': .125, 'left_rear': 12, 'right_rear': 15,
                  'shelf_z': 12, 'fit': .0625, 'pin_w': 1.5, 'pin_bottom': 3.5,
                  'side_lip': 0, 'apron_gap': .125}
    top_cuts = [
        dict(name='Left stopped underside dado', corner=['-bay+side_lip','nose','height'],
             size=['stock','depth-nose','lap']),
        dict(name='Right stopped underside dado', corner=['center+bay-side_lip-stock','nose','height'],
             size=['stock','depth-nose','lap'])]
    add('TOP-01','butcherblock',['-bay',0,'height'],['center+2*bay','depth','top_t'], top_cuts)
    for hand, wall, inner, rear in [('L','-bay',0,'left_rear'),('R','center+bay-stock','center','right_rear')]:
        cleat_x = '-bay+side_lip' if hand == 'L' else 'center+bay-side_lip-stock'
        add('CL-'+hand,'maple',[cleat_x,'nose+cleat_travel','height+lap-cleat_h'],['stock','depth-nose-cleat_travel','cleat_h'])
        stile = '-bay' if hand == 'L' else 'center+bay-rail_h'
        add('ST-'+hand,'maple',[stile,0,'pin_bottom'],['rail_h','stock','height-pin_bottom'])
        add('PB-'+hand,'maple',[wall,'stock','pin_bottom'],['stock','2*stock','height+lap-cleat_h-pin_bottom'])
        add('PS-'+hand,'maple',[wall,rear,'pin_bottom'],['stock','pin_w','height+lap-cleat_h-pin_bottom'])
        rail_x = '-bay+rail_h' if hand == 'L' else 'center'
        add('TR-'+hand,'maple',[rail_x,0,'height-rail_h'],['bay-rail_h','stock','rail_h'])
        shelf_x = '-bay+stock+fit' if hand == 'L' else 'center+fit'
        add('SH-'+hand,'plywood_3_4',[shelf_x,'2*stock','shelf_z'],
            ['bay-stock-2*fit','depth-2*stock-fit','stock'])
        apron_x = f'{rail_x}+apron_gap'
        add('FR-'+hand,'maple',[apron_x,'stock','shelf_z+stock-rail_h'],
            ['bay-rail_h-2*apron_gap','stock','rail_h'])
        # Flat-backed envelope only. The diffuser faces positive Y, toward the back.
        add('LED-SH-'+hand,'lighting',[apron_x,'2*stock','shelf_z+stock-rail_h'],
            ['bay-rail_h-2*apron_gap','led_d','led_h'])
        add('LED-TR-'+hand,'lighting',[rail_x,'stock','height-rail_h'],
            ['bay-rail_h','led_d','led_h'])
    parameters.update(led_d=.375,led_h=.625, led_end=.125, angle_leg=.625)
    return dict(name='Pantry side bays', revision='R1', parameters_in=parameters,
                derived_expressions={}, parts=parts), center


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', type=Path, required=True)
    args = parser.parse_args()
    out = ROOT / 'output'
    side, center = specification()
    combined = dict(side)
    # Center bodies share an origin, with separate parameter names to avoid collisions.
    import re
    def prefix(value):
        if not isinstance(value, str):
            return value
        return re.sub(r'[A-Za-z_]\w*', lambda match: 'org_' + match[0], value)
    def center_box(box):
        return dict(box, corner=list(map(prefix, box['corner'])), size=list(map(prefix, box['size'])))
    combined['parameters_in'] = side['parameters_in'] | {'org_'+k:v for k,v in center['parameters_in'].items()}
    combined['derived_expressions'] = {'org_'+k:prefix(v) for k,v in center['derived_expressions'].items()}
    combined['parts'] = side['parts'] + [dict(center_box(p), cuts=[center_box(c) for c in p['cuts']]) for p in center['parts']]
    for p in center['parts']:
        if p['group'] == 'RAIL' and p['id'][3] != '1':
            x, _, z = center_box(p)['corner']
            combined['parts'].append(dict(id='LED-'+p['id'], name='Angled channel envelope',
                material='lighting', corner=[f'{x}+led_end','org_FT',f'{z}-angle_leg'],
                size=['org_bay-2*led_end',.625,.625],cuts=[]))
    (out/'side-bays-spec.json').write_text(json.dumps(side,indent=2)+'\n')
    (out/'pantry-combined-spec.json').write_text(json.dumps(combined,indent=2)+'\n')
    for name, project in [('side-bays',side),('pantry-combined',combined)]:
        parts = resolve(project)
        commands = solid_commands(project)
        with Session(args.cli.resolve(),out) as session:
            for stage, batch in commands.items():
                if batch:
                    result = session.json('batch',{'commands':batch,'verbose':False})
                    assert result.get('ok') and result['completed']==len(batch), (stage,result)
            verify(session,parts)
            checks = check_interference(session)
            (out/f'{name}-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
            session.json('save',{'path':str(out/f'{name}.sc')})
            session.call('screenshot',{'view':'iso','width':1120,'height':780,'grid':False,'axes':False,
                                       'path':str(out/f'{name}.png')})
        with Session(args.cli.resolve(),out,design=out/f'{name}.sc') as session:
            verify(session,parts)
        print(f'{name}: {len(parts)} bodies; saved, reopened, verified')


if __name__ == '__main__':
    main()
