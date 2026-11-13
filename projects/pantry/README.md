# Pantry side bays and soda organizer R3

The two PDFs are separate shop packets. Open output/pantry-combined.sc for the
complete fit model, output/side-bays.sc for the side bays and countertop, or
output/soda-org-2.sc for the organizer machining model. The combined model
includes lighting clearance envelopes. Peg positions are field-drilling
annotations. The side shelves are shown one per bay in a sample position.

## Open a model in SolidCraft

Click a model to open an editable copy from the current `main` branch.

| Model | Open in browser | Native file |
| --- | --- | --- |
| Complete pantry assembly | [Open in SolidCraft](https://app.solidcraft.io/?open=https%3A%2F%2Fraw.githubusercontent.com%2Fbrian-amos-embedded%2Fwoodworking%2Fmain%2Fprojects%2Fpantry%2Foutput%2Fpantry-combined.sc) | [`pantry-combined.sc`](output/pantry-combined.sc) |
| Side shelves and countertop | [Open in SolidCraft](https://app.solidcraft.io/?open=https%3A%2F%2Fraw.githubusercontent.com%2Fbrian-amos-embedded%2Fwoodworking%2Fmain%2Fprojects%2Fpantry%2Foutput%2Fside-bays.sc) | [`side-bays.sc`](output/side-bays.sc) |
| Soda organizer | [Open in SolidCraft](https://app.solidcraft.io/?open=https%3A%2F%2Fraw.githubusercontent.com%2Fbrian-amos-embedded%2Fwoodworking%2Fmain%2Fprojects%2Fpantry%2Foutput%2Fsoda-org-2.sc) | [`soda-org-2.sc`](output/soda-org-2.sc) |

[Side shelves shop pack](output/side-shelves-shop-pack.pdf) ·
[Soda organizer shop pack](output/soda-organizer-R3-shop-pack.pdf)

## Rebuild

From `projects/pantry`, rebuild with SolidCraft 0.40.1 and Python with ReportLab.
The scripts here define the pantry geometry, build order, and shop-pack presentation.
The CAD engine, MCP client, and sheet layout live in the shared woodworking skill:

    export PYTHONPATH="$(cd ../../skills/woodworking-solidcraft/scripts && pwd)${PYTHONPATH:+:$PYTHONPATH}"


    python scripts/make_project.py
    python scripts/model.py --cli /absolute/path/to/solidcraft-cli
    python scripts/side_bays.py --cli /absolute/path/to/solidcraft-cli
    python scripts/cutlist.py
    mv output/soda-org-2-cutlist.pdf output/soda-organizer-R3-shop-pack.pdf
    python scripts/side_pack.py

The shop packs use nominal stock. Field-fit the side shelves and countertop.
Verify the pins and extrusion end caps, wiring and clips before machining.
