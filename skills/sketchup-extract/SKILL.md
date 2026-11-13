---
name: sketchup-extract
description: Extract named component assemblies directly from SketchUp SKP files with Python for one-time migration into SolidCraft or other CAD workflows. Preserve component definitions, instances, polygon geometry, material references and transforms without SketchUp Desktop. Use for importing existing SketchUp woodworking models or recovering part structure. No Ruby or bidirectional editing workflow.
---
# Extract SketchUp Models

## Prepare
- Preserve the user-supplied SKP unchanged. Use available attachment bytes or retrieve the current source through Library. Never assume a prior scratch path survives.
- Create a disposable Python 3.12+ virtual environment outside the skill and install `scripts/requirements.txt` with its pip. Reuse an existing environment only if its pinned packages match. No SketchUp Desktop, Ruby, Docker or hosted service is needed.
- Read `references/extraction.md` for schema, units and limitations. Use `references/migration.md` for the soda org 2 baseline.

## Extract directly
- Run `<venv>/bin/python <skill>/scripts/extract_components.py <source.skp> --target '<exact definition name>' --output <project>/extraction.json`.
- The script uses skppy 0.10.0, selects exactly one definition, recursively reads descendants, preserves definition-local polygon topology and child placements, and emits schema v2 JSON. It does not alter the SKP.
- Run `python3 <skill>/scripts/validate_extract.py <project>/extraction.json` independently. This checks structural references and loop continuity, not CAD correctness or manufacturability.
- For a visual reference or unsupported parser input, `scripts/inspect_skp.py` can recover archive metadata and an embedded thumbnail. Thumbnail names are not an assembly inventory.
- On parser errors, record the exact error and supported version; do not quietly omit missing references, replace unknown geometry with boxes, or claim conversion succeeded. Consider another verified headless reader or a user-provided browser export. Do not ask the user to install SketchUp Desktop or reintroduce Ruby.
- Do not upload private models to a third-party conversion service without authorization.

## Verify and hand off
- Preserve definition IDs, instance IDs and nested paths. The target is exported in its own definition-local frame, excluding its outer placements in the complete model.
- Keep coordinates in inches until deliberate conversion. Canonical matrices are row-major 4×4 operating on homogeneous column vectors; compose parent @ child and divide xyz by w. The retained native 13-value transform is not a 16-value flattened matrix. Convert coordinates and translation exactly once.
- Validate mirrored/scaled instances and hidden/tag filtering before counting manufacturing parts. Visibility filtering is not performed and some visibility flags are not exposed by this parser. Materials are references; inherited assignment still needs resolution.
- Compare a geometry render and representative dimensions against the source/reference before reconstruction. Do not treat world-aligned bounds as stock sizes for rotated or shaped parts.
- Use woodworking-solidcraft to rebuild editable parametric parts and joinery from the extracted evidence. Extraction alone does not create a SolidCraft design, prove watertightness, or release a cut list.
- Save original source, extraction JSON, validation evidence, source hash and unresolved questions with the project through Library. Keep evolving projects outside the skill; save reusable script/default changes with skill-creator.
