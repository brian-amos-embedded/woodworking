# Construction and fabrication rules

Use Brian's defaults: 2 inch rails/stiles, 4/4 hard maple purchased and milled to 0.75 inch; nominal 0.75 inch maple plywood, nominal 48 × 96 inch sheets. Substitute measured stock thickness and usable sheet dimensions for manufacturing. Never treat 4/4 as finished 1 inch stock.

Carcass grooves were described as “0.25 inch grooves.” For Soda organizer 2, the extracted geometry confirmed 0.25 inch depth. A 0.25 inch deep dado receiving full-thickness plywood differs from a 0.25 inch wide groove receiving a tongue. Resolve the interpretation for each new design before cutting.

Door grooves: 0.25 inch wide × 0.5 inch deep. Separate stub-tenon joints from pocket-screwed butt joints; Brian recently uses glue and pocket screws for faster construction. Confirm which assembly uses which rule. Check screw paths against grooves, material remaining at joints, through-groove end exposure, hinge clearance and assembly access. Face frames and door frames may use different joint rules.

Distinguish shoulder length, overall finished length including tenons, and oversize rough blank length. Record panel material and fit separately. Solid panels need movement clearance and must not be glued rigidly around their perimeter; plywood panels need a suitable fit rather than an assumed identical movement rule. Do not invent exact allowances.

Sheet output: material/thickness grouping, actual sheets and reusable offcuts, edge trims, blade kerf, grain direction and permitted rotations, part labels and sequential guillotine cuts. A guillotine cut crosses the entire current sheet/offcut. Offer simpler setups/fewer cuts as a preference over absolute minimum waste. An arrangement is not executable merely because rectangles fit.

Hardwood output: distinguish rough milling blanks from final machining sizes. Use actual board widths/lengths for a board layout; otherwise provide stock/board-foot estimates with clearly stated yield assumptions. Keep grain/defect/appearance selection under human review. Track jointer/planer allowances, end trimming and rip/crosscut kerf independently where needed.

Before fabrication release: verify part count against instances, local dimensions against geometry, units, stock fit, no layout overlaps, kerf/trims/grain, joint allowances, assembly order, and selected hardware clearance. Give uncertainties and project-specific load considerations plainly, without implying geometric checks certify structural adequacy.


For the bundled rip-first replay, pass `lanes` as an ordered list of strips,
each containing `(part_id, cross_grain_width, along_grain_length)` in cutting
order, with `stock=(width, length)`, `kerf`, `trim` and a unique sheet
`prefix`. The longest part width sets the strip width. Rip the strips, then
crosscut and narrow each blank to its dimensions. Read `cuts` in emitted
order. Apply `part_labels` to display the finished part ID at its output step.
Compare the complete returned ID set and oriented sizes against the manifest,
including across multiple sheets or offcuts. Confirm table-saw handling and
cut order for each new project.

## Shop drawings

Prefer through dados and grooves when their exits will be concealed and the
joint still has adequate material, support, and registration. Use stopped
cuts where an exit would be visible or a joint requires a stop. Verify both
exits in the assembled CAD model. Depict the actual cutter path in drawings.

Label each rip width directly on the proportionally scaled sheet diagram.
Group kept part IDs and final dimensions by rip width. Explain when a blank
needs narrowing after crosscutting. Keep parent and remainder identifiers in
machine-readable replay data rather than the printed table.

Draw each unique machining pattern once, with cut-list names, instance IDs,
quantities, and a small CAD-rendered isometric view. Show handed patterns
separately and identify the machined face. Dimension starts from common
physical edges directly on the view and label cutter widths and depths
nearby. Use an assembled isometric for face frames and dimension member
positions from a common edge when the part dimensions and joinery leave
their positions undetermined.

Default to 6 × 96 inch usable 4/4 boards for preliminary hardwood planning.
Allow individual board sizes to override these defaults and account for kerf
between blanks. Use measured usable stock when producing an actual shop plan.
