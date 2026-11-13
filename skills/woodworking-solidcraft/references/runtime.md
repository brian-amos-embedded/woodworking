# Runtime and MCP

Pinned release: SolidCraft 0.40.1, official Linux x86_64 tarball, SHA256 `0244019d315b37fa9506e09a4ae1cada50713f557dd6be413bd578147350966e`.
Bootstrap downloads vendor binaries and verifies the pinned checksum. Python 3.12+ with tar extraction filters and a compatible Linux/glibc environment is required. Report network/platform failures accurately; do not silently replace this engine with another.

Use a task script with the skill's scripts directory on PYTHONPATH:

```python
from mcp_session import Session
with Session(cli_path, project_dir, design=saved_design_or_none) as s:
    tools = s.rpc('tools/list', {})
    info = s.json('inspect_design', {'measure': False, 'sketches': False})
    contract = s.json('describe_command', {'id': 'solid.box'})
    result = s.json('execute', {'command': 'solid.box', 'params': {
        'length': '24 in', 'width': '2 in', 'height': '0.75 in',
        'body_name': 'rail-001', 'name': 'Rail blank'}})
    measurement = s.json('measure', {'summary': True})
    s.json('save', {'path': str(project_dir / 'design.sc')})
```

Each Session owns an independent in-process design. Keep it open for related commands in one task script; save then reopen across separate tool calls. Session termination does not save automatically. The client has a bounded timeout; a timeout is not proof that a command failed. Use runtime pending/running inspection where available before retrying a live operation; otherwise restore a known saved checkpoint.

The server speaks newline-delimited JSON-RPC over stdio. Do not print human messages to its stdin. A tool returns MCP content blocks; `Session.json` decodes the first text block, while `Session.call` preserves images and full blocks. Use `screenshot` with an explicit path to save a CPU-rendered PNG, then inspect it. Do not dump base64 image payloads into conversation.

Geometry measurements use mm/mm³; explicit expressions such as `0.75 in` avoid display-unit ambiguity. Use `parameters.change` for named expressions and `solid.box` expression fields to preserve dependencies. Inspect exact schemas for new commands.

For multi-part carcasses, create named bodies with expression-based `solid.box`
sizes and `corner` coordinates. Use a second `solid.box` with `operation: cut`
and explicit `targets` for rectangular dadoes and grooves. Prefix parameter
identifiers to avoid ambiguous short names. With 0.40.1, successful batches
report `ok: true` and `completed`; do not require an `applied` array on success.
Check each closed body’s bounds and net volume and use `inspect.interference`.
Check both the reported overlaps and whether any pairs were skipped or unchecked.
Use independent parameters for measured plywood and milled hardwood thickness.

The smoke test proves one simple parametric rail, save/reopen, STEP/GLB exports and CPU screenshot, not arbitrary joinery or cut-list accuracy. Native execution was tested; Docker is unnecessary for this skill. No browser/GPU is needed for the tested path. No persistent network service or external hosting is configured.

Official references:
- https://github.com/tangency-labs/solidcraft/releases/tag/v0.40.1
- https://github.com/tangency-labs/solidcraft/blob/v0.40.1/docs/mcp.md
