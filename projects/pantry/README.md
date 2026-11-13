# Pantry side bays and soda organizer R4

The two PDFs are separate shop packets. Open output/pantry-combined.sc for the
complete fit model, output/side-bays.sc for the side bays and countertop, or
output/soda-org-2.sc for the organizer machining model. The combined model
includes lighting clearance envelopes. Peg positions are field-drilling
annotations. The side shelves are shown two per bay at sample positions.

## Open a model in SolidCraft

Click a model to open an editable copy from the current `main` branch.

| Model | Open in browser | Native file |
| --- | --- | --- |
| Complete pantry assembly | [Open in SolidCraft](https://app.solidcraft.io/?open=https%3A%2F%2Fraw.githubusercontent.com%2Fbrian-amos-embedded%2Fwoodworking%2Fmain%2Fprojects%2Fpantry%2Foutput%2Fpantry-combined.sc) | [`pantry-combined.sc`](output/pantry-combined.sc) |
| Side shelves and countertop | [Open in SolidCraft](https://app.solidcraft.io/?open=https%3A%2F%2Fraw.githubusercontent.com%2Fbrian-amos-embedded%2Fwoodworking%2Fmain%2Fprojects%2Fpantry%2Foutput%2Fside-bays.sc) | [`side-bays.sc`](output/side-bays.sc) |
| Soda organizer | [Open in SolidCraft](https://app.solidcraft.io/?open=https%3A%2F%2Fraw.githubusercontent.com%2Fbrian-amos-embedded%2Fwoodworking%2Fmain%2Fprojects%2Fpantry%2Foutput%2Fsoda-org-2.sc) | [`soda-org-2.sc`](output/soda-org-2.sc) |

[Side shelves shop pack](output/side-shelves-shop-pack.pdf) ·
[Soda organizer shop pack](output/soda-organizer-R4-shop-pack.pdf)

## Rebuild

From the repository root, with Python 3.12+, ReportLab, and SolidCraft 0.40.1:

```sh
python skills/woodworking-solidcraft/scripts/build_project.py projects/pantry --cli /absolute/path/to/solidcraft-cli
```

`project.json` defines the organizer. The other two model specifications live
in `source/`. The combined specification includes both component specifications. Keep the
organizer and side-bay interface dimensions aligned when revising the design. `overrides.json` selects models, test dimensions,
and the shop-pack template, and can override any setting in
[projects/defaults.json](../defaults.json).

The shop packs use nominal stock. Field-fit the side shelves and countertop.
Verify the pins and extrusion end caps, wiring and clips before machining.

R4 places continuous angled channels behind soda rail rows 3 and 5. The side-bay channels mount beneath the countertop rails and middle shelf aprons.

The countertop projects 1 inch in front of the rails and stiles.
