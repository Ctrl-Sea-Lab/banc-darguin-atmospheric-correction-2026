# PI pre-build workspace

This directory is the PI-editable view of the manuscript, bibliography, R and
Python figure code, and figures. Open it in VS Code, make changes on a PI branch,
and preserve uncommitted files. The authoritative project remains at the
repository root.

Run commands from the repository root:

```bash
./scripts/pi-workspace status
./scripts/pi-workspace pre-task --task-id <TASK-ID> --agent ada-lovelace
./scripts/pi-workspace verify-ready --task-id <TASK-ID> \
  --agent <agent-slug> --path <repository-relative-path>
./scripts/pi-workspace refresh --acceptance-file /outside/repository/acceptance.json
./scripts/pi-workspace preview
```

`pre-task` is Ada's mandatory pre-work command for protected paths. It imports
PI edits, merges compatible text changes, and writes a task-scoped readiness
receipt. `verify-ready` checks the receipt and tree hash before an agent edits.
`refresh` requires external exact-commit acceptance evidence and brings the
accepted revision into this workspace while preserving pending PI edits. These
commands exit with status 3 and write
`pre-build/.pi-sync/last-report.json` when a conflict needs review.

Generate figures into `pre-build/.pi-sync/generated/`, then use
`promote-figure`. Promotion is refused if the live generated figure has been
manually changed since the last synchronization. Automated commands cannot
target `figures/edited/`.

See [`../PI_CONTRIBUTIONS.md`](../PI_CONTRIBUTIONS.md) for the complete policy
and approval boundaries.
