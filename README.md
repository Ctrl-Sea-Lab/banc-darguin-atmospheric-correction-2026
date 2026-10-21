# Atmopheric correction of the Banc D'arguin 2026

Reproducible project infrastructure for a future comparison of atmospheric
correction approaches for satellite products in Banc d’Arguin, Mauritania.
This repository contains infrastructure only: no scientific dataset,
hypothesis, analysis method, result, or publication decision has been supplied
or authorized yet.

## Project resources

- Private repository: <https://github.com/Ctrl-Sea-Lab/banc-darguin-atmospheric-correction-2026>
- Research-worker checkout: `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026/`
- Authoritative raw-data directory: `/mnt/PaperClip_Projects/data/raw/banc-darguin-atmospheric-correction-2026/`
- Processed-data directory: `/mnt/PaperClip_Projects/data/processed/banc-darguin-atmospheric-correction-2026/`
- Machine-readable project metadata: [`config/project.yml`](config/project.yml)

The repository was generated from the approved `main` revision of
`Ctrl-Sea-Lab/Research-Template`. Exact source and generated revision evidence
is recorded in `config/project.yml`. Development branches of the template were
not incorporated.

## Data inventory and manual upload

The initial inventory is empty: zero supplied datasets and zero authorized
datasets. Do not download, move, rename, transform, or otherwise alter
scientific data until a dataset and task are explicitly authorized.

The raw-data directory is locked by default with POSIX mode `2550`, owned by
`paperclip-worker` and grouped to `research`. This prevents the research worker
and the research group from creating, deleting, or renaming raw files during
normal operation. The project repository also ignores raw and processed data,
so datasets cannot be committed accidentally.

For a PI manual upload, an authorized project operator must:

1. Confirm that `/mnt/PaperClip_Projects` is the expected NFS mount and that the
   uploader is an authorized member of the `research` group.
2. Open a bounded upload window by changing only the project raw directory to
   mode `2570`. Existing raw files must remain read-only.
3. Have the PI copy files directly into the raw-data directory; do not route
   them through the Git checkout.
4. Record filenames, byte sizes, checksums, source, acquisition time, uploader,
   units, format, and any CRS in the authorized investigation provenance.
5. Remove write permission from uploaded files and subdirectories, then return
   the project raw directory to mode `2550` and verify that
   `paperclip-worker` cannot write to it.

This is an accidental-write safeguard, not an immutable archive. The directory
owner or a NAS administrator can change the mode, and protection of files
uploaded under a different owner requires that uploader or an administrator to
remove their write bits. No raw file is present yet, so no dataset checksum has
been recorded.

## Managed computing environments

Host prerequisites and exact versions are declared in
[`config/toolchain.yml`](config/toolchain.yml). Python dependencies are declared
in `pyproject.toml`, locked in `uv.lock`, and restored into repository-local
`.venv/`. R dependencies are locked in `renv.lock` and restored into the
project-local `renv/library/`. Quarto commands run through
`scripts/project-env.sh`, which binds both environments for one child process.

From the repository root:

```bash
./scripts/bootstrap-env.sh
./scripts/check-env.sh
```

Do not install or modify system-wide software as part of project work.

## New investigations

Each authorized scientific question receives a unique directory copied from
`analysis/_template/`:

```text
analysis/<TASK-ID>_<concise-name>/
```

Keep its scripts, `task.yml`, provenance, figures, tables, outputs,
`report.qmd`, and standalone `report.html` together. Render only the
investigation directory:

```bash
./scripts/render-analysis.sh analysis/<TASK-ID>_<concise-name>
./scripts/project-env.sh .venv/bin/python scripts/record-provenance.py \
  analysis/<TASK-ID>_<concise-name> \
  --render-command './scripts/render-analysis.sh analysis/<TASK-ID>_<concise-name>'
```

Ordinary investigations must not modify the root manuscript. Hypotheses and
analysis methods remain pending the first research question and scientific
review.

## PI workspace and synchronization

The approved PI synchronization implementation is present in `pre-build/`,
`scripts/pi_sync.py`, and `scripts/pi-workspace`. Its current machine-readable
state is `requires_pre_task_sync`: the workspace is initialized and protected
content remains blocked until Ada Lovelace performs the task-scoped pre-task
reconciliation.

```bash
./scripts/pi-workspace status
./scripts/pi-workspace pre-task --task-id <TASK-ID> --agent ada-lovelace
./scripts/pi-workspace verify-ready --task-id <TASK-ID> \
  --agent <agent-slug> --path <repository-relative-path>
```

Conflicts stop affected protected work; unrelated `analysis/` investigations
may continue. A successful synchronization check does not authorize scientific
approval, manuscript integration, merge, publication, or public release.
