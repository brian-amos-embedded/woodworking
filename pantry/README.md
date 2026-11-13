# Pantry side bays and soda organizer R3

The two PDFs are separate shop packets. Open output/pantry-combined.sc for the
complete fit model, output/side-bays.sc for the side bays and countertop, or
output/soda-org-2.sc for the organizer machining model. The combined model
includes lighting clearance envelopes. Peg positions are field-drilling
annotations. The side shelves are shown one per bay in a sample position.

To rebuild with the SolidCraft 0.40.1 CLI and Python with ReportLab:

    python scripts/make_project.py
    python scripts/model.py --cli /absolute/path/to/solidcraft-cli
    python scripts/side_bays.py --cli /absolute/path/to/solidcraft-cli
    python scripts/cutlist.py
    mv output/soda-org-2-cutlist.pdf output/soda-organizer-R3-shop-pack.pdf
    python scripts/side_pack.py

The shop packs use nominal stock. Field-fit the side shelves and countertop.
Verify the pins and extrusion end caps, wiring and clips before machining.
