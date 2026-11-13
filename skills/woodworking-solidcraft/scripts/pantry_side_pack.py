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
    line(42,30,'PANTRY SIDE BAYS  /  R3 / FIELD-FIT DRAFT',8,True)
    line(550,30,str(n),8,True)


def notes(y, strings):
    for s in strings:
        line(42,y,s)
        y -= 18


page('Pantry side shelves','Left and right bays  |  Nominal opening 67 1/2 in  |  Field-fit before cutting')
pdf.drawImage(str(out/'pantry-combined.png'),44,310,524,368,preserveAspectRatio=True,anchor='c')
notes(282,[
    'One adjustable shelf and one fixed bottom shelf per bay.',
    'Use four 1/8 in pegs per shelf. The organizer supplies two rows on each outside face.',
    'The wall supplies a front stile and an independent rear pin strip on each side.',
    'A short-depth front pin backer sits behind each visible stile.',
    'The 2 in upper rails hide the lights. Pocket-screw them to the center stiles from behind.',
    'The 1 1/2 in butcher-block top bears on the organizer and hidden side cleats.',
    'Scribe the countertop and fixed bottom shelves. Leave clearance at adjustable shelves.',
])
pdf.showPage()

page('Cut list','One movable shelf per bay  |  Dimensions in inches  |  Confirm usable stock at the opening')
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
    line(156,y,'1' if key=='TOP-01' else '2')
    line(200,y,label)
    line(383,y,' x '.join(map(inch,dims)))
    line(200,y-12,material,8)
notes(359,[
    f"4/4 stock: two {' x '.join(map(inch, SHOP['hardwood_default_board_in']))} in boards, {inch(SHOP['kerf_in'])} in kerf.",
    'Board A: rip one 2 1/8 in and two 1 5/8 in rough strips.',
    '2 1/8 in strip: two 35 in stiles + one 19 3/4 in upper rail.',
    'First 1 5/8 in strip: two 33 1/4 in front pin backers.',
    'Second 1 5/8 in strip: two 33 1/4 in rear pin strips.',
    'Board B: rip two 2 1/8 in strips and one 1 1/8 in strip.',
    '2 1/8 in strip: one 19 3/4 in upper rail + two 19 1/2 in shelf aprons.',
    'Second 2 1/8 in strip: two 19 3/4 in fixed bottom rail blanks.',
    'Plywood: two nominal 21 1/8 x 17 5/16 in blanks. Maintain clearance for pin adjustment.',
    'One 24 x 48 in offcut yields both movable shelves. Grain runs along the 48 in side.',
    '1 1/8 in strip: two 17 1/2 in cleats.',
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
    '5. Install upper decorative rails, then mount channels to their rear faces.',
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
    'Mount channels to the rear faces of the movable shelf aprons, aimed toward the rear.',
    'Mount fixed channels to the rear faces of the rails directly below the countertop.',
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
line(42,664,'3/4 IN MAPLE PLYWOOD / ONE 24 X 48 IN OFFCUT',10,True)
x,y,s=80,460,7.5
pdf.setStrokeColor(ink)
pdf.setFillColor(colors.HexColor('#f4ead9'))
pdf.rect(x,y,48*s,24*s,fill=1)
for key,(across,along,width,length) in layout['parts'].items():
    pdf.setFillColor(teal)
    pdf.rect(x+along*s,y+across*s,length*s,width*s,fill=1)
    line(x+along*s+10,y+45,key,10,True)
line(42,438,f"Trim {inch(SHOP['edge_trim_in'])} in per edge. Rip 17 5/16 in, then crosscut two 21 1/8 in blanks.")
line(42,420,f"Keep the {inch(SHOP['kerf_in'])} in kerf on the waste side. Keep the adjustable shelf clearance.")
for index,hand in enumerate(('L','R')):
    x,y,s=63+index*270,161,9
    shelf=parts['SH-'+hand]
    sx,sy,_=shelf['corner']
    w,d,_=shelf['size']
    pdf.setFillColor(colors.HexColor('#f4ead9'))
    pdf.rect(x,y,w*s,d*s,fill=1)
    for cut in shelf['cuts']:
        pdf.setFillColor(colors.white)
        pdf.rect(x+(cut['corner'][0]-sx)*s,y+(cut['corner'][1]-sy)*s,
                 cut['size'][0]*s,cut['size'][1]*s,fill=1,stroke=0)

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
line(42,70,'Front reliefs: 1 1/4 in wide x 13/16 in deep at both corners. Mirror left and right.',9)

pdf.showPage()
page('Fixed bottom shelves','One per bay  |  Install after the face frame  |  Field-fit at the opening')
rail, shelf = parts['BR-L'], parts['BS-L']
line(42,666,'Finished blank sizes before fitting',12,True)
notes(641,[
    f"BR-L / BR-R: {inch(rail['size'][0])} x {inch(rail['size'][2])} x {inch(rail['size'][1])} in maple.",
    f"BS-L / BS-R: {inch(shelf['size'][0])} x {inch(shelf['size'][1])} x {inch(shelf['size'][2])} in plywood.",
    'Allow one additional 24 x 48 in offcut for the two bottom blanks.',
    'Fit each rail tight between the stiles and pocket-screw from behind.',
])
line(42,545,'Section through bottom rail and shelf',12,True)
scale=52
x,y=75,382
w,h=rail['size'][1]*scale,rail['size'][2]*scale
cut=rail['cuts'][0]
rabbet,thickness=cut['size'][1]*scale,cut['size'][2]*scale
pdf.setStrokeColor(ink)
pdf.setFillColor(colors.HexColor('#f4ead9'))
pdf.rect(x,y,w,h-thickness,fill=1)
pdf.rect(x,y+h-thickness,w-rabbet,thickness,fill=1)
pdf.setFillColor(teal)
pdf.rect(x+w-rabbet,y+h-thickness,230,thickness,fill=1)
line(x+53,y+h+12,'FLUSH TOPS / 4 1/4 IN ABOVE NOMINAL FLOOR',9,True)
line(x,y-19,'FRONT',8,True)
line(x+89,y+h-17,'FIXED SHELF',9,True)
line(42,329,'Rabbet: 1/4 in into rear face, down by actual shelf thickness.',10,True)
notes(300,[
    'Dry-fit shelf thickness. The open rabbet lets the shelf drop in from above.',
    'Pocket-screw the rails before seating the shelves. Keep screw bores below the rabbet.',
    'Scribe each fixed shelf to the actual opening and baseboard.',
    'Cut the two front shoulders so only the tongue between the stiles enters the rabbet.',
    'Mirror the wall-side notch: left front corner on BS-L, right front corner on BS-R.',
    f"Stile relief: {inch(shelf['cuts'][0]['size'][0])} in wide x "
    f"{inch(shelf['cuts'][0]['size'][1])} in back from the tongue front, through thickness.",
    'This adds 1/16 in at the stile. Transfer the actual stile outline before cutting.',
    'Add rear and side bearing cleats as needed in the field. The rail supports the front.',
    'Secure the bottom shelf after fitting. The shelf pins serve the adjustable shelves.',
])
line(42,147,'PLAN AT FRONT EDGE / BS-L SHOWN, MIRROR FOR BS-R',9,True)
x,y=65,89
pdf.setFillColor(teal)
path=pdf.beginPath()
for i,(u,v) in enumerate([(0,13),(25,13),(25,0),(260,0),(260,10),(282,10),(282,42),(0,42)]):
    (path.moveTo if i==0 else path.lineTo)(x+u,y+v)
path.close()
pdf.drawPath(path,fill=1)
line(x+74,y-14,'Tongue seats in the rail rabbet',8)
line(365,112,'Wall-side relief clears the stile.',8)
line(365,95,'Opposite shoulder clears the center stile.',8)
pdf.showPage()
pdf.save()
