"""Print the side-bay stock, joinery, and installation drawings."""
import json
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from cabinet_model import resolve
from pantry_cutlist import ROOT, SHOP, inch

out = ROOT / 'output'
spec = json.loads((out/'side-bays-spec.json').read_text())
parts = {p['id']:p for p in resolve(spec)}
pdf = canvas.Canvas(str(out/'side-shelves-shop-pack.pdf'), pagesize=(612,792))
ink = colors.HexColor('#18364b')
teal = colors.HexColor('#b6d8d3')
n = 0


def line(x,y,s,size=10,bold=False):
    pdf.setFillColor(ink)
    pdf.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
    pdf.drawString(x,y,s)


def page(title,sub):
    global n
    n += 1
    pdf.setFillColor(ink)
    pdf.rect(0,705,612,87,fill=1,stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont('Helvetica-Bold',23)
    pdf.drawString(42,749,title)
    pdf.setFont('Helvetica',10)
    pdf.drawString(42,725,sub)
    line(42,30,'PANTRY SIDE BAYS  /  FIELD-FIT DRAFT',8,True)
    line(550,30,str(n),8,True)


def notes(y, strings):
    for s in strings:
        line(42,y,s)
        y -= 18


page('Pantry side shelves','Left and right bays  |  Nominal opening 67 1/2 in  |  Field-fit before cutting')
pdf.drawImage(str(out/'pantry-combined.png'),44,310,524,368,preserveAspectRatio=True,anchor='c')
notes(282,[
    'Two adjustable shelves per bay are shown. The middle shelf carries a light.',
    'Use four 1/8 in pegs per shelf. The organizer supplies two rows on each outside face.',
    'The wall supplies a front stile and an independent rear pin strip on each side.',
    'A short-depth front pin backer sits behind each visible stile.',
    'The 2 in upper rails hide the lights. Pocket-screw them to the center stiles from behind.',
    'The 1 1/2 in butcher-block top bears on the organizer and hidden side cleats.',
    'Nominal wall positions follow the SketchUp opening. Scribe the counter and shelves in place.',
])
pdf.showPage()

page('Cut list','Two shelves per bay shown  |  Dimensions in inches  |  Confirm usable stock at the opening')
line(42,666,'Part IDs',9,True)
line(156,666,'Qty',9,True)
line(200,666,'Material / purpose',9,True)
line(383,666,'Finished L x W x T',9,True)
rows = [
    ('TOP-01','butcher block','Countertop',('x','y','z')),
    ('CL','hard maple','Hidden side cleat',('y','z','x')),
    ('ST','hard maple','Front stile',('z','x','y')),
    ('PB','hard maple','Front pin backer',('z','y','x')),
    ('PS','hard maple','Rear pin strip',('z','y','x')),
    ('TR','hard maple','Upper light rail',('x','z','y')),
    ('SH','maple plywood','Adjustable shelf',('x','y','z')),
    ('FR','hard maple','Shelf front apron',('x','z','y')),
]
for i,(key,material,label,axes) in enumerate(rows):
    p=parts[key if key=='TOP-01' else key+'-L']
    y=640-i*31
    dims=[p['size']['xyz'.index(axis)] for axis in axes]
    line(42,y,key if key=='TOP-01' else key+'-L / -R')
    line(156,y,'1' if key=='TOP-01' else ('4' if key in ('SH','FR') else '2'))
    line(200,y,label)
    line(383,y,' x '.join(map(inch,dims)))
    line(200,y-12,material,8)
notes(359,[
    f"4/4 stock: two {' x '.join(map(inch, SHOP['hardwood_default_board_in']))} in boards, {inch(SHOP['kerf_in'])} in kerf.",
    'Board A: rip one 2 1/8 in and two 1 5/8 in rough strips.',
    '2 1/8 in strip: two 33 3/4 in stiles + one 19 3/4 in upper rail.',
    'First 1 5/8 in strip: two 33 1/4 in front pin backers.',
    'Second 1 5/8 in strip: two 33 1/4 in rear pin strips.',
    'Board B: rip one 2 1/8 in and one 1 1/8 in rough strip.',
    '2 1/8 in strip: one 19 3/4 in upper rail + two 19 1/2 in shelf aprons.',
    '1 1/8 in strip: two 17 1/2 in cleats. Rip a 2 1/8 in strip for the two extra aprons.',
    'Plywood: four nominal 21 1/8 x 16 9/16 in blanks. Scribe each independently.',
    'Each 24 x 48 in offcut can yield two shelves, with face grain along the 48 in side.',
    'Counter: template the opening, then transfer the stopped pockets to the underside.',
])
pdf.showPage()

page('Countertop and cleats','Underside plan and end section  |  Rear-open stopped edge dados')
x,y,s=52,456,7.5
top=parts['TOP-01']
w,d=top['size'][0]*s,top['size'][1]*s
nose=(top['cuts'][0]['corner'][1]-top['corner'][1])*s
pdf.setFillColor(colors.HexColor('#f4ead9'))
pdf.rect(x,y,w,d,fill=1)
for edge in (x,x+w-.75*s):
    pdf.setFillColor(teal)
    pdf.rect(edge,y+nose,.75*s,d-nose,fill=1)
    pdf.line(edge,y+nose,edge+(.75*s if edge==x else -42),y-12)
line(52,613,'REAR / CLEAT POCKETS OPEN HERE',9,True)
line(52,426,'FRONT / 1 IN OVERHANG / KEEP 2 1/2 IN OF FULL-THICKNESS NOSE',9,True)
line(52,382,'END SECTION AT CLEAT',10,True)
pdf.setFillColor(colors.HexColor('#f4ead9'))
path=pdf.beginPath()
for i,(a,b) in enumerate([(65,350),(199,350),(199,290),(95,290),(95,310),(65,310)]):
    (path.moveTo if i==0 else path.lineTo)(a,b)
path.close()
pdf.drawPath(path,fill=1)
pdf.setFillColor(teal)
pdf.rect(65,270,30,40,fill=1)
pdf.line(65,256,65,359)
line(54,240,'WALL',8,True)
line(222,329,'Top: 1 1/2 in thick. Pocket: 3/4 in nominal width x 1/2 in deep.')
line(222,308,'Cleat: 1 in high x 3/4 in thick. The upper half seats in the pocket.')
line(222,287,'Fasten cleat into framing. Keep the top free to move front to back.')
notes(205,[
    'Grain runs left to right. Allow 1/8 in at the stopped shoulder as drawn.',
    'Fasten cleats before setting the top. Recess heads so the top can slide on the cleats.',
    'Use figure-8s or slots at accessible bearing points. Keep the cleat pocket a slip fit.',
    'Check the top can lower onto both cleats in the real opening before final routing.',
])
pdf.showPage()

page('Adjustable shelves and lights','Use the center face frame as the front datum  |  Left and right are field-fit')
notes(665,[
    '1. Install the organizer with its 1 1/2 in x 3 1/2 in baseboard reliefs.',
    '2. Fasten each front stile and pin backer, then locate the independent rear pin strip.',
    '3. Dry-fit the low shelf and its 2 in apron. Lift and remove it past the upper trim.',
    '4. Transfer one level datum to all four peg rows. Match peg bearing heights.',
    '5. Install upper decorative rails, then mount channels on their bottom faces.',
])
line(42,548,'Peg rows (from front face of center organizer)',12,True)
notes(526,[
    'Front wall-side backer: 1 7/8 in. Rear strip center: left 12 3/4 in, right 15 3/4 in.',
    'Organizer-side front: 1 7/8 in. Organizer-side rear: 15 3/4 in.',
    'Wall-side rear positions are provisional. Keep the left strip clear of plugs and cords.',
    'Use a common drilling template. A 1 in pitch is shown as a planning choice.',
    'Start the useful pin range near 6 in above floor. Set the upper limit after dry-fit.',
    'Check pin projection across the scribe gap and use a depth stop sized to actual pegs.',
    'Organizer side residual thickness can be 1/2 in at internal recesses. Avoid breakthrough.',
])
line(42,378,'Rectangular lighting channels',12,True)
notes(356,[
    'Mount channels to the bottom faces of the middle shelf aprons, aimed toward the rear.',
    'Mount fixed channels to the underside of the rails directly below the countertop.',
    'Channel blanks: two up to 18 1/2 in at the shelves and two up to 18 3/4 in above.',
    'Leave extra end clearance for caps and leads. Confirm actual extrusion and clip dimensions.',
    'The CAD envelope is 3/8 in front-to-back x 5/8 in high. Check it before machining.',
    'Use a removable low-voltage connector and strain-relieved service loop on each shelf.',
    'Allow the wire to move through the shelf adjustment range and keep it clear of peg rows.',
])
pdf.showPage()
page('Shelf blanks and peg layout','Top views  |  Shelf front is at the bottom  |  Peg positions shown at the nominal fit')
from sheet_layout import rip_first
blanks = [(key, parts[key]['size'][1], parts[key]['size'][0]) for key in ('SH-L','SH-R')]
layout = rip_first([blanks], (24,48), SHOP['kerf_in'], SHOP['edge_trim_in'], 'S1')
line(42,664,'3/4 IN MAPLE PLYWOOD / REPEAT ON TWO 24 X 48 IN OFFCUTS',10,True)
x,y,s=80,460,7.5
pdf.setStrokeColor(ink)
pdf.setFillColor(colors.HexColor('#f4ead9'))
pdf.rect(x,y,48*s,24*s,fill=1)
for key,(across,along,width,length) in layout['parts'].items():
    pdf.setFillColor(teal)
    pdf.rect(x+along*s,y+across*s,length*s,width*s,fill=1)
    line(x+along*s+10,y+45,key,10,True)
line(42,438,f"Trim {inch(SHOP['edge_trim_in'])} in per edge. Rip 16 9/16 in, then crosscut two 21 1/8 in blanks.")
line(42,420,f"Keep the {inch(SHOP['kerf_in'])} in kerf on the waste side. Template each shelf to its bay.")
for index,hand in enumerate(('L','R')):
    x,y,s=63+index*270,161,9
    shelf=parts['SH-'+hand]
    sx,sy,_=shelf['corner']
    w,d,_=shelf['size']
    pdf.setFillColor(colors.HexColor('#f4ead9'))
    pdf.rect(x,y,w*s,d*s,fill=1)
    parameters = spec['parameters_in']
    bearing = (parameters['pin_projection']-parameters['fit'])/2*s
    organizer_edge = x+w*s-bearing if hand=='L' else x+bearing
    wall_edge = x+bearing if hand=='L' else x+w*s-bearing
    rear = spec['parameters_in']['left_rear' if hand=='L' else 'right_rear']+.75
    for edge, depth in [(organizer_edge,1.875),(organizer_edge,15.75),
                        (wall_edge,1.875),(wall_edge,rear)]:
        pdf.setFillColor(ink)
        pdf.circle(edge,y+(depth-sy)*s,3,fill=1,stroke=0)
    pdf.setFillColor(teal)
    apron=parts['FR-'+hand]
    pdf.rect(x+(apron['corner'][0]-sx)*s,y-7,apron['size'][0]*s,7,fill=1)
    line(x,y-25,'SH-'+hand+' / front apron shown in teal',9,True)
    line(x,y+d*s+12,'WALL  /  ORGANIZER' if hand=='L' else 'ORGANIZER  /  WALL',8)
line(42,106,'Shelf width = carcass to wall-side pin face minus 1/8 in total.')
line(42,88,'Apron width = clear opening between stiles minus 1/4 in total.')
line(42,70,'Confirm pin projection and tilt the shelf past the stiles before drilling.')

pdf.showPage()
pdf.save()
