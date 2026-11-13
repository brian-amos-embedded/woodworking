"""Render a checked rip-first stock plan for 4/4 hardwood."""
from collections import Counter

from reportlab.lib import colors

from sheet_layout import rip_first


def draw_hardwood_plan(pdf, page, line, inch, shop, blanks, board_lanes):
    stock = shop['hardwood_default_board_in']
    kerf = shop['kerf_in']
    assigned = Counter(key for lanes in board_lanes for lane in lanes for key in lane)
    if assigned != Counter(blanks.keys()):
        raise ValueError('Hardwood board plan must cover each blank exactly once.')

    page('4/4 hardwood cut plan',
         f'Hard maple  |  {len(board_lanes)} boards at {inch(stock[0])} x {inch(stock[1])} in usable')
    line(42, 668, f'Kerf: {inch(kerf)} in. Square one end and straighten one edge before measuring usable stock.')
    line(42, 650, 'Rip the strips first, then crosscut left to right. Dimensions shown are rough blanks.')
    scale = min(480 / stock[1], 48 / stock[0])
    for index, lanes in enumerate(board_lanes, 1):
        label = f'B{index}'
        plan = rip_first([[blanks[key] for key in lane] for lane in lanes], stock, kerf, 0, label)
        x, y = 64, 558 - (index - 1) * 215
        line(42, y + stock[0] * scale + 12, f'Board {label}', 12, True)
        pdf.setStrokeColor(colors.HexColor('#18364b'))
        pdf.setFillColor(colors.HexColor('#eeeae0'))
        pdf.rect(x, y, stock[1] * scale, stock[0] * scale, fill=1)
        for key, (across, along, width, length) in plan['parts'].items():
            px, py = x + along * scale, y + across * scale
            pdf.setFillColor(colors.HexColor('#b6d8d3'))
            pdf.rect(px, py, length * scale, width * scale, fill=1)
            line(px + 3, py + 1, key, min(6.5, width * scale * 0.72), True)
        for n, lane in enumerate(lanes, 1):
            row = y - 24 - (n - 1) * 36
            rip = max(blanks[key][1] for key in lane)
            line(42, row, f'Strip {n}  |  Rip {inch(rip)} in', 9, True)
            line(176, row, '  /  '.join(lane), 9)
            cuts = ' + '.join(inch(blanks[key][2]) for key in lane)
            line(176, row - 15, f'Crosscut lengths (in)  {cuts}', 8)
    pdf.showPage()
