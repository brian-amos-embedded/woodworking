"""Replay grain-locked rip-first layouts with independent kerf and fit checks."""


def rip_first(lanes, stock, kerf, trim, prefix):
    """Lanes contain (part ID, cross-grain width, along-grain length) triples."""
    width, length = stock
    if kerf <= 0 or trim < 0 or (trim and trim < kerf) or min(stock) <= 2 * trim:
        raise ValueError('Invalid stock, kerf or perimeter trim')
    cuts, parts, offcuts, labels = [], {}, [], {}

    def split(rect, axis, keep, parent):
        span = rect[axis + 2]
        if not 0 < keep <= span + 1e-8:
            raise ValueError(f'{parent} cannot yield {keep} inches from {span}')
        if abs(keep - span) < 1e-8:
            return (parent, rect), None
        a, b = list(rect), list(rect)
        a[axis + 2] = keep
        b[axis] += keep + kerf
        b[axis + 2] -= keep + kerf
        first, second = parent + 'A', parent + 'B'
        cuts.append(dict(parent=parent, parent_rect=rect, first=first,
                         second=second if b[axis + 2] > 1e-8 else '',
                         action=('Rip' if axis == 0 else 'Crosscut'), keep=keep))
        return (first, tuple(a)), (second, tuple(b)) if b[axis + 2] > 1e-8 else None

    def remainder(piece, label):
        if piece:
            offcuts.append((label, piece[0], piece[1]))

    remaining = (prefix, (trim, trim, width - 2 * trim, length - 2 * trim))
    stripped = []
    for lane in lanes:
        if not lane or remaining is None:
            raise ValueError('A lane is empty or exceeds the available sheet width')
        name, rect = remaining
        strip, remaining = split(rect, 0, max(blank[1] for blank in lane), name)
        stripped.append((lane, strip))
    remainder(remaining, 'Sheet offcut')

    for lane, strip in stripped:
        for part_id, across, along in lane:
            if strip is None or part_id in parts:
                raise ValueError(f'Missing stock or duplicate ID for {part_id}')
            name, rect = strip
            blank, strip = split(rect, 1, along, name)
            name, rect = blank
            finished, waste = split(rect, 0, across, name)
            parts[part_id] = finished[1]
            labels[finished[0]] = part_id
            remainder(waste, f'{part_id} side offcut')
        remainder(strip, 'Strip offcut')

    all_rects = list(parts.values()) + [rect for _, _, rect in offcuts]
    for index, (x, y, w, l) in enumerate(all_rects):
        if min(w, l) <= 0 or x < trim or y < trim or x + w > width - trim + 1e-8 or y + l > length - trim + 1e-8:
            raise ValueError('Part or offcut falls outside trimmed stock')
        for a, b, c, d in all_rects[:index]:
            if min(x + w, a + c) - max(x, a) > 1e-8 and min(y + l, b + d) - max(y, b) > 1e-8:
                raise ValueError('Overlapping parts or offcuts')
    return {'stock': stock, 'trim': trim, 'kerf': kerf, 'cuts': cuts, 'parts': parts, 'part_labels': labels, 'offcuts': offcuts}
