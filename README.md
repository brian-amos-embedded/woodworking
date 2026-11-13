# Woodworking

This repository keeps each woodworking design with its editable CAD, build inputs, and shop drawings. It gives a fresh ChatGPT session enough context to revise a design, reproduce the outputs, and pick up where the last session ended.

## Start here

- [Pantry](projects/pantry/README.md) contains the soda organizer, adjustable side shelves, and countertop assembly.
- [Agent handoff](AGENTS.md) explains how to find the current design, run SolidCraft from ChatGPT, and verify a revision.
- [SolidCraft web app](https://app.solidcraft.io/) opens native `.sc` models for interactive viewing and editing.

To start in a new chat, connect GitHub with access to this repo and paste:

> Work in `brian-amos-embedded/woodworking`. Read `AGENTS.md` and `projects/pantry/README.md` first. Use the pantry project on `main` as the baseline. My task is …

## Repository layout

| Path | Purpose |
| --- | --- |
| `projects/<project>/` | A project's README, design inputs, scripts, and deliverables |
| `projects/pantry/project.json` and `scripts/` within that project | Soda organizer specification, SolidCraft commands, side-bay generator, and PDF generators |
| `projects/pantry/source/` | Extracted SketchUp reference geometry |
| `projects/pantry/output/` | Native SolidCraft models, renders, shop packs, cut lists, and verification results |
| `skills/` | Woodworking modeling, drawing, and stock-planning guidance, plus SketchUp extraction |
| `config/` and root `scripts/` | Shared defaults, MCP configuration example, and CAD smoke test |
| `Dockerfile`, `compose.yaml`, `.devcontainer/`, `.github/workflows/` | Reproducible headless CAD setup and CI smoke test |

## Tools and workflow

SolidCraft 0.40.1 is pinned for headless CAD. The Python scripts drive its local MCP server, build and reopen native models, and check dimensions and interference. ReportLab produces the PDF shop packs. The optional SketchUp extraction skill recovers source geometry for reference.

1. Read the project README and inspect the current model, assumptions, and part IDs.
2. Edit the source specification or generator and rebuild the affected native models.
3. Check the geometry and review the renders. Regenerate any affected shop packs and cut lists from the same revision.
4. Commit the design inputs, scripts, and revised deliverables together. Record dimensions or hardware still requiring a field fit.

## Open a model in a browser

The [pantry model list](projects/pantry/#open-a-model-in-solidcraft) has one-click links that open the editable models in the SolidCraft web app. Each link loads an unsaved copy from `main`. Use your browser's open-in-new-tab action to keep the repository or chat alongside the model.

The links use the public GitHub raw file URL with SolidCraft's [design link format](https://docs.solidcraft.io/guide/getting-started.html#design-links-and-embeds).
