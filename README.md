# Woodworking

- [Pantry](pantry/README.md) contains the editable SolidCraft models, project inputs, rebuild scripts, and shop packs.
- [Woodworking SolidCraft](skills/woodworking-solidcraft/SKILL.md) documents the CAD and shop-pack workflow.
- [SketchUp extraction](skills/sketchup-extract/SKILL.md) documents the direct Python extraction workflow.

## Headless CAD

The Dockerfile downloads and verifies the pinned SolidCraft 0.40.1 release for Linux x86-64. Run `docker build --platform linux/amd64 -t woodworking-solidcraft:0.40.1 .` from this directory. Compose and the dev container configuration use the same image build. The GitHub Actions workflow runs the headless CAD smoke test.
