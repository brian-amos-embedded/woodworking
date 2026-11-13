"""Generate the R1 fabrication packet and replay its sheet cuts."""
from collections import Counter, defaultdict
from fractions import Fraction
import csv
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from pantry_joinery_views import draw_joinery
from pathlib import Path

from cabinet_model import box_edges, resolve

import sys
from project_config import load_project

ROOT = Path(sys.argv[1]).resolve()
CONFIG = load_project(ROOT)
from sheet_layout import rip_first
from hardwood_plan import draw_hardwood_plan

OUT = ROOT / 'output'
PROJECT = json.loads((ROOT / 'project.json').read_text())
SOURCE = json.loads((ROOT / CONFIG['source']).read_text())
PARTS = resolve(PROJECT)
SHOP = CONFIG['shop']
BLUE = colors.HexColor('#18364b')
TEAL = colors.HexColor('#b6d8d3')
MATERIAL = CONFIG['materials']


def inch(value):
    exact = Fraction(value).limit_denominator(64)
    if abs(float(exact) - value) > 1e-8:
        return f'{value:.5f}'.rstrip('0').rstrip('.')
    whole, numerator = divmod(exact.numerator, exact.denominator)
    return (f'{whole} ' if whole else '') + f'{numerator}/{exact.denominator}' if numerator else str(whole)


def csv_file(name, headings, rows):
    with (OUT / name).open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(headings)
        writer.writerows(rows)


def mapped_source():
    by_definition = defaultdict(list)
    for occurrence in SOURCE['occurrences']:
        by_definition[occurrence['definition_id']].append(occurrence)
    assert Counter(part['source_definition'] for part in PARTS) == {
        key: len(items) for key, items in by_definition.items()}
    assert len(PARTS) == len({part['id'] for part in PARTS})
    mapping = []
    # The source frame face is Y=-0.11 in. Align that datum with model Y=0.
    for part in PARTS:
        candidates = by_definition[part['source_definition']]
        def error(occurrence):
            low, high = occurrence['assembly_bbox_in']
            return sum(((a + b - c - d) / 2)**2 for (a, b), c, d
                       in zip(box_edges(part), [low[0], low[1] + .11, low[2]],
                              [high[0], high[1] + .11, high[2]]))
        occurrence = min(candidates, key=error)
        assert error(occurrence) < .1**2, (part['id'], occurrence, error(occurrence))
        candidates.remove(occurrence)
        mapping.append({'part': part['id'], 'definition': part['source_definition'],
                        'source_instance_path': occurrence['instance_path'],
                        'source_bounds_in': occurrence['assembly_bbox_in'],
                        'normalized_bounds_in': list(map(list, zip(*box_edges(part))))})
    return mapping


def stock_dims(part):
    size = part['size']
    axis = part['grain_axis']
    thickness_axis = min(range(3), key=size.__getitem__)
    width_axis = next(i for i in range(3) if i not in (axis, thickness_axis))
    return size[axis], size[width_axis], size[thickness_axis]


def layouts():
    blanks = {}
    for part in PARTS:
        length, width, _ = stock_dims(part)
        blanks[part['id']] = (part['id'], width, length)
    specs = CONFIG['sheet_layouts']
    result = []
    for name, material, stock, lanes in specs:
        plan = rip_first([[blanks[key] for key in lane] for lane in lanes], stock or SHOP['sheet_in'],
                         SHOP['kerf_in'], SHOP['edge_trim_in'], name)
        result.append(plan | {'name': name, 'material': material, 'lanes': lanes})
    expected = {p['id'] for p in PARTS if p['material'].startswith('plywood')}
    laid_out = [key for plan in result for key in plan['parts']]
    assert set(laid_out) == expected and len(laid_out) == len(expected)
    for plan in result:
        for key, rect in plan['parts'].items():
            assert all(abs(a-b) < 1e-8 for a, b in zip(rect[2:], blanks[key][1:]))
    return result


def generate():
    plans = layouts()
    source_map = mapped_source()
    manifest = [p | {'blank_lwt_in': stock_dims(p)} | {'source': src}
                for p, src in zip(PARTS, source_map)]
    (OUT / 'part-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (OUT / 'sheet-layouts.json').write_text(json.dumps(plans, indent=2) + '\n')
    groups = defaultdict(list)
    for part in PARTS:
        groups[(part['material'], part['group'], stock_dims(part))].append(part['id'])
    rough = {}
    for (material, group, (length, width, thickness)), ids in groups.items():
        if material == 'maple':
            rough[group] = (len(ids), length, width, thickness, length + SHOP['hardwood_rough_length_allowance_in'],
                            width + SHOP['hardwood_rough_width_allowance_in'], ids)
    bf = sum(qty * rough_l * rough_w / 144 for qty, _, _, _, rough_l, rough_w, _ in rough.values())
    demand = [{'name': group.title(), 'length': data[4], 'width': data[5], 'ids': data[6]}
              for group, data in rough.items()]
    template = Path(__file__).with_name('hardwood-board-planner.template.html')
    (OUT / 'hardwood-board-planner.html').write_text(
        template.read_text().replace('__DEMAND__', json.dumps(demand))
        .replace('__BOARD_DEFAULT__', json.dumps(SHOP['hardwood_default_board_in']))
        .replace('__KERF_DEFAULT__', inch(SHOP['kerf_in'])))
    csv_file('plywood-cut-list.csv', ['material', 'group', 'quantity', 'grain_length_in', 'cross_width_in', 'thickness_in', 'part_ids'],
             [(MATERIAL[m], g, len(ids), *dims, ' '.join(ids)) for (m, g, dims), ids in groups.items() if m != 'maple'])
    csv_file('hardwood-cut-list.csv', ['group', 'quantity', 'final_length_in', 'final_width_in', 'final_thickness_in',
             'rough_length_in', 'rough_width_in', 'nominal_rough_thickness_in', 'part_ids'],
             [(group, *data[:-1], 1, ' '.join(data[-1])) for group, data in rough.items()])

    machining = [(p['id'], cut['name'], *[round(c - d, 8) for c, d in zip(cut['corner'], p['corner'])], *cut['size'])
                 for p in PARTS for cut in p['cuts']]
    csv_file('machining.csv', ['part_id', 'feature', 'start_x_in', 'start_y_in', 'start_z_in',
                              'span_x_in', 'span_y_in', 'span_z_in'], machining)
    csv_file('cut-sequence.csv', ['sheet', 'step', 'action', 'parent', 'parent_width_in', 'parent_length_in',
                                 'keep_in', 'kept_piece', 'remainder_piece'],
             [(plan['name'], n, cut['action'], cut['parent'], *cut['parent_rect'][2:], cut['keep'],
               plan['part_labels'].get(cut['first'], cut['first']),
               plan['part_labels'].get(cut['second'], cut['second'])) for plan in plans for n, cut in enumerate(plan['cuts'], 1)])

    pdf = canvas.Canvas(str(OUT / 'soda-org-2-cutlist.pdf'), pagesize=letter)
    pdf.setTitle(f'Soda organizer 2 | {PROJECT["revision"]} cut list')
    pdf.setAuthor('Woodworking project')
    page_number = 0

    def line(x, y, value, size=10, bold=False):
        pdf.setFillColor(BLUE)
        pdf.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
        pdf.drawString(x, y, value)

    def page(title, subheading):
        nonlocal page_number
        page_number += 1
        pdf.setFillColor(BLUE)
        pdf.rect(0, 697, 612, 95, fill=1, stroke=0)
        pdf.setFillColor(colors.white)
        pdf.setFont('Helvetica-Bold', 23)
        pdf.drawString(42, 744, title)
        pdf.setFont('Helvetica', 11)
        pdf.drawString(42, 721, subheading)
        line(42, 32, f'SODA ORGANIZER 2   /   {PROJECT["revision"]}   /   NOMINAL-STOCK DRAFT', 8, True)
        line(553, 32, str(page_number), 9, True)

    page('Soda organizer 2', 'Cut list and table-saw plan  |  26 W x 18 1/8 D x 36 1/4 H in')
    pdf.drawImage(str(OUT / 'iso.png'), 53, 354, width=300, height=310, preserveAspectRatio=True, anchor='c')
    line(355, 629, 'Stock for this layout', 12, True)
    for y, value in enumerate(['3/4 in maple plywood', '1 full 48 x 96 in sheet', '+ 1 offcut, 16 x 36 in', '', '1/4 in maple plywood',
                               '1 offcut, 24 x 36 in', '', '4/4 hard maple', f'{bf:.2f} board ft in rough blanks',
                               'Before defect and yield loss']):
        line(355, 606-y*17, value, 10, y in (0, 4, 7))
    line(42, 326, 'Plywood blanks', 14, True)
    line(42, 306, 'Part', 9, True)
    line(214, 306, 'Qty', 9, True)
    line(260, 306, 'Along grain x across grain x thickness (in)', 9, True)
    names = {'SIDE':'Sides', 'DIV':'Dividers', 'TOPBOT':'Top and bottom', 'SHELF-OUT':'Outer-bay shelves',
             'SHELF-CENTER':'Center-bay shelves', 'BACK':'Back'}
    y = 283
    for (material, group, dims), ids in groups.items():
        if material == 'maple':
            continue
        line(42, y, names[group])
        line(214, y, str(len(ids)))
        line(260, y, ' x '.join(map(inch, dims)))
        y -= 21
    line(42, 139, 'Measure stock before machining', 11, True)
    line(42, 120, 'The drawings use 0.750 in carcass stock and 0.250 in back stock.')
    line(42, 104, 'Test-fit scrap in the dados and grooves. Regenerate if measured thickness changes.')
    line(42, 79, 'The grain direction is marked on each sheet. A second full 3/4 in sheet can supply S2.')
    pdf.showPage()

    for plan in plans:
        name = plan['name']
        width, length = plan['stock']
        page(f'{name}  |  {MATERIAL[plan["material"]]}', f'{inch(width)} x {inch(length)} in stock  |  Grain along {inch(length)} in')
        line(42, 672, f"Trim {inch(plan['trim'])} in per edge. Keep the {inch(plan['kerf'])} in kerf on the waste side.", 9)
        line(42, 655, "Rip the strips at the widths shown, then crosscut along each strip as drawn.", 9)
        scale = 5  # points per inch, identical on all stock diagrams
        ox, oy = 91, 610 - width*scale
        pdf.setStrokeColor(BLUE)
        pdf.setFillColor(colors.HexColor('#eeeae0'))
        pdf.rect(ox, oy, length*scale, width*scale, stroke=1, fill=1)
        for part_id, (x, y, w, l) in plan['parts'].items():
            px, py, pw, ph = ox+y*scale, oy+x*scale, l*scale, w*scale
            pdf.setFillColor(TEAL)
            pdf.rect(px, py, pw, ph, stroke=1, fill=1)
            line(px+4, py+ph/2-2, part_id, 8, True)
        pdf.setStrokeColor(BLUE)
        top = oy + width * scale
        right = ox + length * scale
        pdf.line(ox, top + 8, right, top + 8)
        for x in (ox, right):
            pdf.line(x, top + 4, x, top + 12)
        line((ox + right) / 2 - 12, top + 13, f'{inch(length)} in', 8, True)
        pdf.line(ox - 49, oy, ox - 49, top)
        for y_edge in (oy, top):
            pdf.line(ox - 53, y_edge, ox - 45, y_edge)
        line(20, (oy + top) / 2, f'{inch(width)} in', 8, True)
        pdf.line(ox, oy-11, ox+55, oy-11)
        pdf.line(ox+55, oy-11, ox+49, oy-8)
        pdf.line(ox+55, oy-11, ox+49, oy-14)
        line(ox+62, oy-14, 'GRAIN / LONG DIMENSION', 7, True)
        cursor = plan['trim']
        for lane in plan['lanes']:
            rip = max(plan['parts'][key][2] for key in lane)
            y0, y1 = oy + cursor * scale, oy + (cursor + rip) * scale
            pdf.line(ox - 7, y0, ox - 7, y1)
            for edge in (y0, y1):
                pdf.line(ox - 10, edge, ox - 4, edge)
            line(52, (y0 + y1) / 2 - 3, inch(rip), 8, True)
            cursor += rip + plan['kerf']
        y = oy - 44
        for x, heading in [(42, 'Rip width'), (148, 'Kept pieces'), (367, 'Final width x length (in)')]:
            line(x, y, heading, 9, True)
        for lane in sorted(plan['lanes'], key=lambda keys: -max(plan['parts'][k][2] for k in keys)):
            rip = max(plan['parts'][key][2] for key in lane)
            grouped = defaultdict(list)
            for key in lane:
                grouped[tuple(plan['parts'][key][2:])].append(key)
            for n, ((w, l), ids) in enumerate(grouped.items()):
                y -= 19
                line(42, y, inch(rip) if n == 0 else '')
                line(148, y, ', '.join(ids))
                line(367, y, f'{inch(w)} x {inch(l)}')
        line(42, y-28, 'If final width is smaller than the rip width, crosscut the blank first, then narrow it.', 8)
        pdf.showPage()

    page('Hard maple and joinery', '4/4 rough stock  |  Mill to 3/4 in finished thickness')
    for x, value in [(42,'Part'),(138,'Qty'),(185,'Finished L x W (in)'),(359,'Rough L x W (in)')]:
        line(x, 657, value, 10, True)
    for y, (group, data) in zip((631, 606), rough.items()):
        qty, length, width, _, rl, rw, ids = data
        for x, val in [(42,group.title()),(138,str(qty)),(185,f'{inch(length)} x {inch(width)}'),
                       (359,f'{inch(rl)} x {inch(rw)}')]:
            line(x, y, val)
    line(42, 574, f'{bf:.2f} board ft of rough blanks at 1 in nominal thickness. Board yield depends on your stock.')
    line(42, 553, 'See the next page for the default board layout. Use the HTML planner for measured stock.')
    line(42, 533, 'Face frame uses glued, pocket-screwed butt joints. Check screw placement on scrap.')
    line(42, 493, 'Joinery drawings', 14, True)
    line(42, 470, 'See the following pages for machining faces, edge references and cut depths.')
    line(42, 450, 'Dry-fit the shelf-and-divider core on the bottom, seat the back, then fit the top.')
    line(42, 430, 'Bring in the outer sides and check square before fitting the face frame.')
    pdf.showPage()
    blanks = {key: (key, width, length)
              for _, _, _, _, length, width, ids in rough.values() for key in ids}
    stiles, rails = rough['STILE'][-1], rough['RAIL'][-1]
    lanes = [[stiles[:2] + rails[:3], stiles[2:] + rails[3:6]], [rails[6:]]]
    draw_hardwood_plan(pdf, page, line, inch, SHOP, blanks, lanes)
    draw_joinery(pdf, page, line, inch, PARTS, OUT)
    page('Soda organizer lighting', f"{PROJECT['revision']}  |  Four rear-mounted continuous channels")
    line(42, 656, 'Cut three 21 3/4 in angled runs (65 1/4 in total) from the 72 in stock.')
    line(42, 636, 'Mount angled runs behind rows 3, 4 and 5, counted from the bottom.')
    line(42, 616, 'Cut one 21 3/4 in rectangular run for row 2, with its light facing the back.')
    line(42, 596, 'Each run spans all three columns. Mount 1/8 in above the rail lower edge.')
    line(42, 566, 'Cut four front-edge reliefs through each inner divider.', 10, True)
    line(42, 546, 'Test the 11/16 in angled and 7/16 in rectangular relief depths with actual profiles.')
    line(42, 526, 'Feed each row from the side or rear with accessible connections.')
    line(42, 496, 'Outside-face shelf pins', 12, True)
    line(42, 474, 'Transfer the shared level datum from the side bays. Use two rows per organizer side.')
    line(42, 454, 'Check 1/8 in pins and insertion depth against the actual hardware.')
    line(42, 434, 'At dado and groove crossings, nominal wall thickness remaining is 1/2 in.')
    line(42, 414, 'See the side-bay packet for provisional pin locations and drilling limits.')
    pdf.showPage()
    pdf.save()


if __name__ == '__main__':
    generate()
