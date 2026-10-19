# Research-Template

Reproducible marine ecology and remote sensing research template using R,
Python, and Quarto.

Human PI edits are preserved through the workflow in
[`PI_CONTRIBUTIONS.md`](PI_CONTRIBUTIONS.md). Automated figures go to
`figures/generated/`; manually edited graphics and their editable sources go to
`figures/edited/`.

Team-wide protected work uses the machine-readable policy in
`.pi-preservation/sync-policy.json` and task-scoped receipts from
`scripts/pi-workspace pre-task`. Proposed Paperclip role amendments are listed
in [`PI_SYNC_AGENT_AMENDMENTS.md`](PI_SYNC_AGENT_AMENDMENTS.md) for PI review;
they are not applied automatically.

The PI-facing manuscript workspace is `pre-build/`. Ada imports PI edits before
team work and refreshes the workspace after accepted revisions:

```bash
./scripts/pi-workspace status
./scripts/pi-workspace import
./scripts/pi-workspace refresh
./scripts/pi-workspace preview
```

Synchronization uses Git context, SHA-256 hashes, and a three-way baseline. It
stops without changing managed files when text or binary changes cannot be
resolved safely. See `PI_CONTRIBUTIONS.md` for exit codes and conflict handling.

## Managed project environments

The repository is the isolation boundary:

- Python packages are declared in `pyproject.toml`, resolved in `uv.lock`, and
  installed into `.venv/` by the pinned `uv` release.
- R packages are resolved in `renv.lock` and installed into the project-local
  `renv/library/`.
- Quarto commands run through `scripts/project-env.sh`, which binds Python,
  reticulate, renv, and caches to this repository for one child process only.

Host prerequisites are recorded in `config/toolchain.yml`. Installing or
changing those tools is not performed by the project bootstrap and requires
separate approval.

After the prerequisites have been provisioned:

```bash
./scripts/bootstrap-env.sh
./scripts/check-env.sh
```

Add a Python dependency with `uv`:

```bash
./scripts/project-env.sh uv add <package-spec>
./scripts/check-env.sh
```

Add an R dependency from the approved CRAN registry:

```bash
./scripts/project-env.sh Rscript scripts/manage-r-dependencies.R add <package-spec>
./scripts/check-env.sh
```

Create an investigation by copying `analysis/_template/`, then render only that
investigation:

```bash
./scripts/render-analysis.sh analysis/<TASK-ID>_<concise-name>
./scripts/project-env.sh .venv/bin/python scripts/record-provenance.py \
  analysis/<TASK-ID>_<concise-name> \
  --render-command './scripts/render-analysis.sh analysis/<TASK-ID>_<concise-name>'
```

The render helper refuses `analysis/_template`, nested paths, and all root
manuscript targets. See `DEPENDENCIES.md` for governance, upgrades, recovery,
and troubleshooting.
