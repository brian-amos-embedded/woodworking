# Direct Python extraction contract

Install dependencies in a disposable environment:

```sh
python3 -m venv <scratch>/skp-env
<scratch>/skp-env/bin/python -m pip install -r <skill>/scripts/requirements.txt
<scratch>/skp-env/bin/python <skill>/scripts/extract_components.py <input.skp> --target 'soda org 2' --output <project>/extraction.json
python3 <skill>/scripts/validate_extract.py <project>/extraction.json
```

Pin skppy 0.10.0 and numpy 2.5.4. Linux/Python 3.12 was tested. The dependency installer requires network access to the package registry; parsing stays local. Do not upgrade automatically without repeating a real-file extraction check.

Schema v2 includes source filename/hash/header version/parser version, target definition, reachable definition graph, vertex coordinates, edges/flags, face planes, boundary and hole loops with oriented edge uses, child definition references, source IDs, material/layer references, native transforms and normalized matrices. Materials contain IDs and names, not textures. Definition IDs are parser/source entity IDs; do not claim they equal Ruby persistent_id values or survive arbitrary save/rebuild operations.

`vertices_in` is definition-local inches. `matrix4x4` is a nested row-major matrix; multiply a column [x,y,z,1], then divide xyz by resulting w. Compose nested placements parent @ local. `raw_transform13` preserves skppy's 3×3 basis + translation + homogeneous scale convention. It is never a Ruby column-major16 transform. `occurrences` expands geometry-bearing definitions into target-local coordinates; `assembly_bbox_in` is an axis-aligned assembly-space bounding box, not necessarily cutting dimensions. `part_counts` counts geometry occurrences by definition, subject to manufacturing interpretation.

Unsupported placed image entities stop extraction. Textures/UVs, attributes, true curves/arcs, guides, annotations, external placement and original design constraints are not exported. Polygon boundaries remain. Hidden/tag filtering is not applied; all parsed descendants are included. Some face/instance visibility may be absent from skppy's public model. Keep the original SKP authoritative for source evidence.

The validator checks finite coordinates, references, edge/loop continuity, single outer loop flags, graph cycles and consistency of count summary with occurrences. It does NOT independently reconstruct every placement, verify solid closure, test coplanarity/self-intersection, prove exact parser fidelity, or approve manufacturing dimensions. Compare representative measurements and a rendered model before using geometry for fabrication.

Evidence: pantry.skp format 27.0.0 successfully parsed with 83 total definitions; selected soda org 2 yielded 9 reachable definitions (assembly + 8 geometry definitions), 35 geometry occurrences. This is a tested file, not universal compatibility.

References:
- https://pypi.org/project/skppy/
- https://github.com/dantedex/skppy
