"""Draw datum dimensions on machining faces using the model's cutter boxes."""
from math import isclose

from reportlab.lib import colors


def draw_joinery(pdf, page, line, inch, parts, output):
    by_id = {part['id']: part for part in parts}
    ink = colors.HexColor('#18364b')
    recess = colors.HexColor('#b6d8d3')

    def iso(key, x, y, width=170, height=150):
        pdf.drawImage(str(output / f'part-{key}.png'), x, y, width, height,
                      preserveAspectRatio=True, anchor='c')

    def face(part, axes, x, y, scale, cuts=(), reverse=False):
        u, v = axes
        size = part['size']
        w, h = size[u] * scale, size[v] * scale
        pdf.setStrokeColor(ink)
        pdf.setFillColor(colors.HexColor('#f8f5ed'))
        pdf.rect(x, y, w, h, fill=1)
        for cut in cuts:
            a = cut['corner'][u] - part['corner'][u]
            b = cut['corner'][v] - part['corner'][v]
            du, dv = cut['size'][u], cut['size'][v]
            if reverse:
                a = size[u] - a - du
            pdf.setFillColor(recess)
            pdf.rect(x + a * scale, y + b * scale, du * scale, dv * scale, fill=1)
        line(x, y-19, f'{inch(size[u])} x {inch(size[v])} in', 9, True)
        return w, h

    def vertical_starts(part, cuts, x, y, scale):
        line(x-66, y-10, '0 / BOTTOM', 8, True)
        for cut in cuts:
            offset = cut['corner'][2] - part['corner'][2]
            at = y + offset*scale
            pdf.setStrokeColor(ink)
            pdf.line(x-25, at, x+3, at)
            pdf.line(x-25, y, x-25, at)
            line(x-65, at-3, inch(offset), 9, True)

    def side(part_id, reverse):
        part = by_id[part_id]
        page(f'Joinery | {part_id}', 'Sides / Qty 1 each hand / 3/4 in maple plywood')
        x, y, scale = 113, 217, 11
        w, h = face(part, (1, 2), x, y, scale, part['cuts'], reverse)
        vertical_starts(part, part['cuts'][:5], x, y, scale)
        line(x, y+h+14, 'INSIDE FACE', 10, True)
        front = x+w if reverse else x
        groove = part['cuts'][5]
        offset = groove['corner'][1] - part['corner'][1]
        at = front + (-1 if reverse else 1) * offset * scale
        pdf.line(front, y+h, front, y+h+30)
        pdf.line(at, y+h, at, y+h+30)
        pdf.line(min(front,at), y+h+28, max(front,at), y+h+28)
        line(min(front,at)+34, y+h+34, f'{inch(offset)} from front to groove', 9)
        line(front-12, y-36, 'FRONT', 8, True)
        iso(part_id, 332, 391, 222, 219)
        line(332, 363, 'Shelf dados: 3/4 in wide x 1/4 in deep.', 9)
        line(332, 344, 'Back groove: 1/4 in wide x 1/4 in deep.', 9)
        line(332, 325, 'Run the dados and back groove through.', 9)
        line(332, 305, 'Rear-bottom relief: 1 1/2 in x 3 1/2 in, through.', 9)
        line(42, 108, 'Bottom is the common datum for all five shelf dado starts.')
        pdf.showPage()

    side('SIDE-L', False)
    side('SIDE-R', True)

    page('Joinery | DIV-1 and DIV-2', 'Dividers / Qty 2 / 3/4 in maple plywood')
    part = by_id['DIV-1']
    x, y, scale = 114, 258, 11
    cuts = [c for c in part['cuts'] if c['name'].startswith('dado') and isclose(c['corner'][0], part['corner'][0])]
    wire = [c for c in part['cuts'] if c['name'].endswith('channel-relief')]
    w, h = face(part, (1, 2), x, y, scale, cuts + wire)
    vertical_starts(part, cuts, x, y, scale)
    line(x, y+h+15, 'BOTH FACES', 10, True)
    iso('DIV', 328, 380, 230, 230)
    line(328, 350, 'Dados: 3/4 in wide x 1/4 in deep.', 9)
    line(328, 331, 'Run through from front to rear.', 9)
    line(328, 312, 'Repeat the pattern on the opposite face.', 9)
    line(328, 293, 'Opposing dados leave a 1/4 in web.', 9)
    line(328, 267, 'Channel reliefs: 3/4 in high, through thickness.', 9)
    line(328, 250, 'Depth from front: 7/16 in lowest, 11/16 in others.', 9)
    starts = ', '.join(inch(c['corner'][2] - part['corner'][2]) for c in wire)
    line(328, 231, 'Lower edges from divider bottom (in):', 9)
    line(328, 214, starts, 9)
    pdf.showPage()

    page('Joinery | TOP and BOT', 'Top and bottom / Qty 2 / 3/4 in maple plywood')
    part = by_id['BOT']
    x, y, scale = 107, 304, 13
    w, h = face(part, (0, 1), x, y, scale, part['cuts'])
    for i, cut in enumerate(part['cuts'][:-1]):
        offset = cut['corner'][0] - part['corner'][0]
        at = x + offset*scale
        baseline = y-42-i*26
        pdf.line(x, baseline, at, baseline)
        pdf.line(at, baseline-4, at, y+2)
        line(x+8, baseline+5, f'{inch(offset)} from left', 9)
    line(x-25, y-84, 'LEFT / FRONT DATUM', 8, True)
    offset = part['cuts'][-1]['corner'][1] - part['corner'][1]
    at = y+offset*scale
    pdf.line(x-18, y, x-18, at)
    pdf.line(x-22, at, x+2, at)
    line(34, at-3, inch(offset), 9, True)
    line(34, at-18, 'from front', 8)
    iso('TOPBOT', 409, 412, 162, 146)
    line(42, 166, 'Divider dados: 3/4 in wide x 1/4 in deep. Run front to rear.')
    line(42, 145, 'Back groove: 1/4 in wide x 1/4 in deep. Run left to right.')
    line(42, 124, 'Machine the top underside and the bottom upper face with this same pattern.')
    pdf.showPage()

    page('Joinery | Shelves and back', 'Maple plywood / Square edges seat in the carcass recesses')
    for part_id, key, title, y, axes, scale in [
        ('SH-L1','SHELF-OUT','Outer-bay shelves / SH-L1 to L3 and SH-R1 to R3 / Qty 6', 513,(1,0),9),
        ('SH-C1','SHELF-CENTER','Center-bay shelves / SH-C1 to C3 / Qty 3', 347,(1,0),9),
        ('BACK','BACK','Back / BACK / Qty 1', 75,(0,2),5.8),
    ]:
        part = by_id[part_id]
        line(82, y+part['size'][axes[1]]*scale+16, title, 10, True)
        face(part, axes, 82, y, scale)
        line(251, y+20, f'{inch(min(part["size"]))} in thick', 9)
        iso(key, 361, y-14, 185, 138)
    pdf.showPage()

    page('Joinery | Hardwood face frame', '4/4 hard maple / 3/4 in finished thickness')
    iso('FRAME', 98, 325, 415, 355)
    line(42, 303, 'Stiles / ST-1 to ST-4 / Qty 4 / 34 x 2 x 3/4 in', 10, True)
    line(42, 279, 'Rails / RA-11 to RA-53 / Qty 15 / 6 x 2 x 3/4 in', 10, True)
    iso('STILE', 63, 92, 210, 158)
    iso('RAIL', 315, 92, 210, 158)
    line(42, 76, 'Glue and pocket-screw the square-ended butt joints from the rear face.')
    line(42, 59, 'Set the hole offsets and drill depth using your jig and screw specifications.')
    pdf.showPage()
