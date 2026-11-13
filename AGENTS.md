# Working in this repository

The [root README](README.md) is the overview. Open the relevant `projects/<name>/README.md` first. For pantry, start with [the project README](projects/pantry/README.md) and [the woodworking skill](skills/woodworking-solidcraft/SKILL.md). Treat the GitHub branch and the project's own source files as the baseline.

## Start from ChatGPT.com

1. Select the private `brian-amos-embedded/woodworking` repo in a GitHub-connected ChatGPT or Codex session. Confirm the branch and read the project README, current inputs, and output checks.
2. Use a repository checkout in a coding workspace for native model generation. In a connector-only chat, use GitHub for file reads and review, or switch to a coding workspace for rebuilds.
3. On a Linux x86-64 workspace with Python 3.12+, use the pinned native runtime. From the repo root:

   ```sh
   python3 skills/woodworking-solidcraft/scripts/bootstrap.py --cache "$PWD/work/solidcraft"
   ```

   Use the CLI path printed by bootstrap. Install ReportLab in the Python environment used for the shop-pack scripts. Follow the pantry README for the build order. If the workspace lacks the required tools or download access, use a Docker-capable workstation, dev container, or GitHub Actions for the smoke test.

## Docker or dev container

From the repo root:

```sh
docker build --platform linux/amd64 -t woodworking-solidcraft:0.40.1 .
docker run --rm --platform linux/amd64 --user "$(id -u):$(id -g)" \
  --mount "type=bind,source=$PWD,target=/work" \
  --env HOME=/tmp --workdir /work/projects/pantry \
  --entrypoint /bin/bash woodworking-solidcraft:0.40.1
```

Run the pantry README commands in the container with `/usr/local/bin/solidcraft-cli`. The image includes ReportLab. For an interactive editor workspace, use the repo's dev container configuration. CI verifies the headless CAD smoke test, while the pantry rebuild runs the project-specific checks.

## Design and delivery

- Work from the project inputs. Keep native `.sc` files, part IDs, geometry checks, and shop-pack revisions aligned.
- Reopen the generated models, check dimensions and interference, then inspect the drawings. Record any assumptions about material, hardware, or installation fit.
- Link the relevant native file on the current branch and the [SolidCraft web app](https://app.solidcraft.io/) when delivering a model. The user can download from GitHub and open the model in the app tab. Use an `open` URL only for an authorized host that supports SolidCraft's browser fetch.
- Keep each new project under `projects/`. Use the shared skills for reusable practices and the project README for job-specific decisions.
