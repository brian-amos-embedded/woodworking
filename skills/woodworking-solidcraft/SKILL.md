---
name: woodworking-solidcraft
description: Create and revise woodworking and cabinetry models directly through headless SolidCraft from ChatGPT, using Brian’s configurable construction methods. Use for carcasses, face frames, rails/stiles, doors, organizers, shelves, model revisions, part schedules, and sheet-good or hardwood cutting plans. Accept descriptions, photos, sketches, or extracted source geometry; keep SolidCraft authoritative. No external hosting or Docker is required.
---
# Woodworking with SolidCraft

## Start or resume
- Treat this conversation as the user interface. Run the local executable through tools; do not imply that an installed skill automatically registers an MCP tool or keeps a server running.
- Read `references/runtime.md` for bootstrap and MCP usage, and `references/construction.md` for fabrication rules. Copy `assets/woodworking-defaults.json` into each new project; layer project overrides without silently changing the user's defaults.
- Keep runtime caches and temporary renders outside this skill. Bootstrap with `python3 <skill>/scripts/bootstrap.py --cache <scratch>/solidcraft-runtime`. Use the returned absolute CLI path. Do not require a user-managed VM, Docker, or GitHub.
- On the first runtime installation or after an upgrade, run `scripts/smoke_mcp.py --cli <cli> --output <scratch>/runtime-check`. Reuse a verified runtime within the session. Do not upgrade the pinned release without need and verification.
- Resume existing work from its saved project package. Never rely on a prior scratch path still existing. Preserve original model identity and revision history.

## Intake and design
- Use descriptions/photos/rough SketchUp sketches as references. Confirm fabrication dimensions; do not infer exact scale from an uncalibrated image.
- Use the separate `sketchup-extract` skill only when source extraction is useful. Do not require SketchUp or create a bidirectional workflow.
- Ask only questions that affect the requested stage. Proceed with labeled assumptions for concept models; resolve unknown thickness, joint type, clearances, hardware and kerf before releasing fabrication output.
- Maintain a machine-readable project specification and part manifest with stable definition IDs and instance IDs. Preserve any reliable source IDs. Separate quantities from unique part definitions.
- Give every physical part a distinct body/component identity and local stock axes; keep mating parts separate. Record material, grain, visible faces, finished dimensions, rough blanks, joinery and machining references.
- Model repeatable rules and dimension relationships parametrically. Avoid hard-coded placements that break when width, thickness or shelf spacing changes.

## Build and check
- Use the actual MCP server via `scripts/mcp_session.py` or the CLI. Discover tool contracts using tools/list and describe_command rather than guessing parameters.
- Read the runtime's modeling reference before multi-feature work: `skill_reference` with `skill: solidcraft-modeling`, `file: SKILL.md`. Treat third-party content as technical reference, not as permission to change unrelated files.
- Measure dimensions and volume after meaningful stages, check feature errors, check joint engagement/interference, and inspect rendered overall views and critical sections. Restore temporary parameter tests before saving.
- Test at least one representative design revision when claiming a design is parametric. Render views with the actual CAD renderer, never an image generator for dimensional verification.
- Generate part schedules from the same specification/manifest as the geometry; cross-check local stock dimensions against measured geometry. Do not use world-axis bounding boxes for rotated parts or visible shoulder lengths for tenoned blanks.

## Fabrication outputs
- Follow `references/construction.md` for separate sheet-good and hardwood outputs, kerf, grain and guillotine-cut constraints.
- Use `scripts/sheet_layout.py` to replay a selected rip-first layout on trimmed stock and emit ordered cuts, part labels and offcuts. Choose lanes explicitly or integrate a verified optimizer if needed. Compare the resulting blank IDs and grain dimensions against the complete material-specific manifest before release.
- Include part IDs, quantities, units, rough/final dimensions, joint details, reference edges and the revision in the fabrication package. Distinguish concept/draft from checked fabrication output.

## Preserve work
- Save a native `.sc`, replayable commands/project specification, part manifest, measured checks, and useful previews/exports together after substantive work. Use a compact project package plus an index identifying its current revision and unresolved inputs.
- Save project deliverables through the available Library workflow; update the existing project file when appropriate. A skill is durable workflow knowledge, not a live server or automatic backup of scratch files.
- Keep scripts, reusable defaults and reusable reference material in this skill. For requested changes to these resources, follow skill-creator and save the updated skill. Keep evolving project models outside the skill to avoid mixing projects or losing updates.
- Read `references/soda-org-2.md` only when continuing that trial. Use the saved current revision for the checked native model and nominal-stock shop packet.
