
# Ctrl+Sea — Scientific Research Agent Rules

## Mission

Conduct rigorous, reproducible scientific research in
marine ecology, environmental science, and remote sensing.

All scientific findings must be supported by real data,
executable code, and verifiable evidence.

## Research investigations

Every Board research request must receive a unique task ID
and a dedicated directory:

analysis/<TASK-ID>_<concise-name>/

Create the directory by copying analysis/_template/.

Each investigation must contain:
- report.qmd and report.html
- task.yml
- scripts/
- figures/
- tables/
- outputs/

Never use analysis/_template/ as an active investigation.

## Data processing

- Use R or Python for reproducible computations.
- Never modify original scientific datasets.
- Preserve CRS, units, metadata, and nodata information.
- Document all exclusions and parameter choices.
- Validate numerical and spatial outputs.
- Use local SSD scratch space for intensive temporary work.
- Store permanent research products on the NAS.

## Scientific reporting

Individual investigations must produce HTML reports only.

Reports must contain:
- Research question and objectives
- Data and study area
- Methods
- Quantitative results and figures
- Scientific interpretation
- Uncertainty and limitations
- Reproducibility information
- Internal review and PI approval status

Never fabricate data, statistics, methods, or references.

## Scientific review

A reviewer independent of the analysis authors must verify:
- Reproducibility
- Data integrity
- Numerical accuracy
- Statistical assumptions and uncertainty
- Scientific interpretations
- Figure and table consistency

Internal review does not constitute PI approval.

## Manuscript protection

The root index.qmd is the FINAL MANUSCRIPT.

Research agents must not modify:
- index.qmd
- manuscript/
- docs/
- the root _quarto.yml

Only the designated manuscript integration agent may propose
changes after explicit PI authorization.

All agents must follow `PI_CONTRIBUTIONS.md` and run the PI
contribution guard before proposing a pull request. A Git author
name is not evidence that a change or decision came from the PI.
Authenticated authorization must be bound to the exact revision.

Committed PI-authored text is authoritative. Agents may propose
improvements only as reviewable diffs and must not substantively
change PI-authored manuscript text without explicit authorization.
Analysis reports must never regenerate `index.qmd`.

An analysis is not approved merely because task.yml says
"approved". Approval must be verified against an authenticated
human decision bound to the exact analysis revision.

Approval of scientific findings and authorization to integrate
them into the manuscript are separate decisions.

Merge authorization and publication authorization are also
separate from manuscript integration authorization.

## PI contribution preservation

- Inspect the latest revision and working-tree status before work.
- Use a task-specific branch or isolated worktree.
- Preserve all uncommitted modifications and untracked user files.
- Incorporate newer PI commits before proposing agent changes.
- Never force-push, hard-reset, or silently overwrite PI work.
- Stop for PI review when agent work conflicts with a PI change.
- Preserve PI-customized R and Python scripts; never replace them
  with template copies.
- Treat `.pi-preservation/registry.json` as a protection registry,
  not as self-authenticating evidence of PI approval.

Automated figures belong in `figures/generated/`. Manually edited
graphics and editable sources belong in `figures/edited/`.
Automated scripts must never write to `figures/edited/` and should
use `scripts/figure_io.py` for safe generated output.

The PI edits the synchronized `pre-build/` workspace. Before relevant team
work, the synchronization manager must run task-scoped `pre-task` and review
its Git context and SHA-256 report. After an accepted authoritative manuscript
revision, the manager must run `refresh` with external exact-commit evidence.
Both commands use the committed baseline for a three-way comparison and must
stop on an unresolved text, deletion, or binary conflict. Never alter the
baseline, copy a preferred side over a conflict, or run destructive Git commands
to make synchronization pass.

An import into `index.qmd` creates a reviewable manuscript change; it does not
prove scientific approval or grant manuscript-integration, merge, or
publication authorization. A refresh is permitted only after the corresponding
authoritative revision has been accepted through the applicable external gate.
See `PI_CONTRIBUTIONS.md` for the operator interface and conflict procedure.

### Mandatory team synchronization gate

This policy applies to every Ctrl+Sea agent. Before a task may modify final
manuscript text, the bibliography, root R or Python scripts, figures,
manuscript configuration/output, the pre-build workspace, or PI-preservation
safeguards, Charles Darwin must classify the target paths as protected and
coordinate a pre-task synchronization. Ada Lovelace must run:

```bash
./scripts/pi-workspace pre-task --task-id <TASK-ID> --agent ada-lovelace
```

The assigned agent must then verify every intended target path before editing:

```bash
./scripts/pi-workspace verify-ready \
  --task-id <TASK-ID> --agent <agent-slug> --path <repository-relative-path>
```

The command checks the task-scoped receipt, state transition, and SHA-256 of the
managed authoritative, workspace, and baseline trees. The state is recorded in
`pre-build/.pi-sync/state.json`; the machine-readable policy is
`.pi-preservation/sync-policy.json`. Neither file is evidence of scientific or
PI approval.

A missing, stale, mismatched, or conflicted receipt blocks only work that
touches protected paths. Independent investigations confined to `analysis/`
must pass their actual paths to `verify-ready`; they may proceed even while PI
synchronization is conflicted. They must not use that exemption to write any
protected path.

On a synchronization conflict, preserve all authoritative, PI-workspace, and
baseline versions and the hash report. Do not edit around the gate. Charles
keeps affected Paperclip tasks blocked on the synchronization task; unrelated
investigations have no such blocker. Ada requests an authenticated PI decision
for the exact paths and hashes. After the accepted authoritative revision is
committed, Ada refreshes the PI workspace with evidence exported outside this
repository and bound to the exact current commit:

```bash
./scripts/pi-workspace refresh --acceptance-file <outside-repository.json>
```

The refresh must finish before the next protected task is prepared. Acceptance
for refresh does not authorize manuscript integration, merge, or publication.

### Team responsibilities

- Charles Darwin scopes target paths, creates the Paperclip synchronization
  task, adds it as a blocker only to affected tasks, and verifies that an
  authenticated PI decision is bound to the exact revision when required.
- Ada Lovelace owns `pre-task`, conflict preservation, synchronization reports,
  and the post-acceptance `refresh`; she never chooses a side of a conflict.
- Johannes Gutenberg verifies readiness before manuscript integration, Quarto
  manuscript builds, or changes to final-manuscript files and preserves PI text
  as authoritative.
- Rachel Carson preserves PI-edited ecological text and records scientific
  disagreements for PI review instead of rewriting them silently.
- Edward Tufte preserves manually edited figures and editable sources, stages
  automated candidates separately, and uses the guarded promotion command.
- Roger Tomlinson preserves PI-edited geospatial scripts and figures together
  with their CRS, units, nodata, and provenance metadata.
- Thomas Bayes preserves PI-edited statistical scripts, model specifications,
  priors, seeds, and parameters and escalates conflicting implementations.
- Karl Popper independently reviews synchronization evidence, failure tests,
  and separation of scientific, integration, merge, and publication gates.
- Alan Turing maintains the synchronization implementation, machine-readable
  policy/state, automated tests, and reproducibility documentation; he cannot
  approve his own safeguards or authorize publication.

Paperclip-managed agent instruction files are changed only after PI review.
Proposed amendments are maintained in `PI_SYNC_AGENT_AMENDMENTS.md`; repository
policy must not be used to rewrite those managed files automatically.

## Quarto

Final manuscript:
- Source: index.qmd
- Configuration: root _quarto.yml
- Output: docs/ (HTML and DOCX)

Scientific investigations:
- Source: analysis/<TASK-ID>_<name>/report.qmd
- Configuration: investigation-specific _quarto.yml
- Output: report.html in the same investigation directory

Never render an investigation using the root manuscript
configuration.

## GitHub

- Use task-specific branches and pull requests.
- Never push directly to protected main.
- Never commit credentials or confidential raw datasets.
- Never merge or publish without appropriate authorization.
- Record the task ID in relevant commits and pull requests.

## Project dependency environments

Each research repository owns exactly one Python environment and one R
environment. Agents assigned to this repository may manage ordinary packages
from the approved PyPI and CRAN registries without per-package approval when
all of the following are true:

- work occurs on a task-specific branch or worktree;
- Python changes use `uv` and update both `pyproject.toml` and `uv.lock`;
- R changes use `renv` and update `renv.lock`;
- packages install only into this repository's `.venv/` or `renv/library/`;
- validation, tests, Quarto smoke renders, and provenance checks are run;
- the dependency change is submitted through a pull request.

Agents may recreate repository-local environments and caches, restore locked
packages, and deliberately add, remove, or update project dependencies.

The standing authorization does not permit:

- `sudo`, OS package managers, or system package installation;
- installing or changing R, Python, Quarto, GDAL, compilers, shared libraries,
  or `uv`;
- system Python installs, user/global R libraries, or shell/startup changes;
- automatic Python downloads;
- new registries, custom indexes, credentials, VCS dependencies, or local
  dependencies outside this repository;
- changes to another repository, GitHub administration, merge, or publication.

Use `scripts/bootstrap-env.sh` to restore environments,
`scripts/check-env.sh` to detect drift, and `scripts/render-analysis.sh` for
investigation reports. Never invoke direct `pip install` for routine project
management. If a package requires a missing native/system dependency, record
the package, error, and requirement, then stop for PI/infrastructure approval.

## Completion

An investigation is complete only when its computations,
figures, tables, HTML report, and internal scientific review
have passed the required checks.

Manuscript integration and public publication are separate
activities requiring explicit PI authorization.

Dependency work is complete only when both lockfiles are current, a cold
restore is reproducible, tests and language-specific Quarto smoke reports pass,
and an independent reviewer has examined the implementation. A YAML approval
field is never evidence of an authenticated approval.
