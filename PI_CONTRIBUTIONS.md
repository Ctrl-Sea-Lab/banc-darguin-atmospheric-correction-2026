# Preserving PI contributions

This repository treats committed Principal Investigator (PI) contributions as
authoritative project work. Agents must preserve them, their provenance, and the
approval gates in `AGENTS.md`.

Git author names are not identity evidence. A contribution is identified as a
PI decision only when an authenticated system (for example, a Paperclip human
decision, an approved GitHub review, or a SHA-bound GitHub comment from a
configured PI account) binds that decision to an exact commit. The registry
described below records what to
protect; it does not authenticate its own entries.

## PI workflow in VS Code

1. Open a project clone or worktree dedicated to your branch. Do not edit in an
   agent's active worktree.
2. Before editing, run `git fetch --prune origin`, `git status --short --branch`,
   and `git log --oneline --decorate -5`. Resolve unexpected local changes
   before continuing; never discard them.
3. Create a PI branch from the current `origin/main` and make the desired edits.
4. Put automatic figures in `figures/generated/`. Put manually edited graphics
   and their editable sources (such as PSD, SVG, or XCF files) in
   `figures/edited/`. Manuscript source may reference an edited asset directly;
   rendering must not write into that directory.
5. Commit the files. For a contribution that future agent work must treat as
   protected, add or update its entry in `.pi-preservation/registry.json` with
   its SHA-256 and the authenticated decision reference. The authenticated
   decision must be bound to the exact commit; the registry is provenance, not
   proof of approval.
6. Push the branch and open a pull request. Review the complete diff before
   merge. Scientific approval, manuscript-integration authorization, merge
   authorization, and publication authorization remain separate decisions.

## Agent workflow

Agents work on a dedicated branch or isolated worktree and run:

```bash
git fetch --prune origin
python3 scripts/pi_guard.py preflight --base-ref origin/main
```

`preflight` refuses the default branch, a dirty working tree, or a branch that
does not contain the fetched base. It never cleans, resets, stashes, or changes
files.

Before a pull request, agents run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/pi_guard.py check --base-ref origin/main
```

The guard blocks the following changes for explicit review:

- the final manuscript (`index.qmd`, `_quarto.yml`, `manuscript/`, and `docs/`);
- any manuscript, script, or figure represented in the synchronized pre-build
  baseline, even when it is not separately registered;
- modifications or deletions of existing files in `figures/edited/`;
- any path registered at the base or head revision; and
- changes to the policy and guard files after their initial introduction.

Adding a new file to `figures/edited/` is allowed so the PI can contribute a new
asset. Once committed, later modification or deletion requires review. All
automated writers must use `scripts/figure_io.py`, which only writes below
`figures/generated/`.

When the guard reports a protected conflict, stop. Do not resolve it by copying
a template, choosing an agent version, deleting the registry entry, changing a
Git author name, or creating an approval file inside the repository. Present the
diff to the PI. Conflicting scientific implementations require PI review.

## Approval evidence

The guard accepts an authorization document only from outside the repository
and only when it is bound to the exact merge base, head commit, protected paths,
and decision types. Agents do not create this document. The enforcement workflow
runs the guard scripts from the protected base revision, treats the proposed
revision only as data, and derives authorization from authenticated GitHub APIs.
This prevents a proposed change to the guard itself from changing the check that
reviews that proposal.

The GitHub workflow accepts actions only from accounts listed in the repository
variable `PI_GITHUB_LOGINS` (a comma-separated list). The normal channel is an
approved review targeting the current head commit. When the PI also authored
the pull request and GitHub therefore prohibits self-approval, the PI instead
posts one exact authorization line per required token:

```text
PI-CONTRIBUTION-CHANGE-AUTHORIZED HEAD=<full-40-character-head-SHA>
```

The workflow reads the authenticated comment author through the GitHub API and
requires the full current head SHA. Embedded prose, a comment by an unconfigured
account, or a line for an earlier commit fails closed. Creating or editing the
comment triggers the check; every new head commit invalidates the prior line.
The required review tokens or SHA-bound comment tokens are:

- `PI-CONTRIBUTION-CHANGE-AUTHORIZED` for registered code, edited figures, or
  safeguard changes; and
- `PI-MANUSCRIPT-INTEGRATION-AUTHORIZED` for final-manuscript changes.

The second statement authorizes only manuscript integration for that exact
revision. Neither channel authorizes merge or publication. Configure the
`tests` job from `pi-contribution-tests` and the `preservation` job from
`pi-contribution-guard` as required checks on the protected default branch. The
workflows become enforceable after this bootstrap change is reviewed and merged
into the default branch.

## Registry format

`.pi-preservation/registry.json` contains a version and contribution records:

```json
{
  "version": 1,
  "contributions": [
    {
      "path": "R/model.R",
      "sha256": "<sha256 of the committed file>",
      "evidence": {
        "kind": "github_review",
        "decision_id": "review-123",
        "verified_commit": "<full commit SHA>"
      }
    }
  ]
}
```

Paths are repository-relative files. A change to a registered file requires an
exact-revision authorization and an updated hash. Do not register raw datasets,
credentials, or transient outputs.

## Synchronization and conflicts

### Pre-build operator interface

`pre-build/` is a complete PI-editable view for VS Code. It contains the
manuscript (`index.qmd`), bibliography, R and Python figure code, graphical
assets, a separate Quarto configuration, and the last synchronized baseline in
`pre-build/.pi-sync/baseline/`. The baseline is machine-managed evidence for the
three-way comparison; do not edit it.

Ada's command sequence before the team starts protected work is:

```bash
git status --short --branch
./scripts/pi-workspace status
./scripts/pi-workspace pre-task --task-id <TASK-ID> --agent ada-lovelace
git diff -- index.qmd library.bib R python figures pre-build
```

`pre-task` compares the authoritative root files, baseline, and PI workspace by
SHA-256. PI-only edits are imported, authoritative-only edits are safely
refreshed, and compatible text changes are merged with Git's three-way merge.
On success it records a task-scoped `ready` receipt. Each assigned agent checks
the exact paths it expects to modify before editing:

```bash
./scripts/pi-workspace verify-ready \
  --task-id <TASK-ID> --agent <agent-slug> --path <path>
```

The receipt becomes stale when any managed manuscript, R/Python script, or
figure differs from the recorded tree. A bare `import` remains available for
diagnosis, but produces `synchronized_unscoped` and does not authorize protected
task work. The commands do not switch branches, reset, clean, stash, commit, or
modify paths outside the declared manuscript, bibliography, code, figure,
baseline, state, and report paths.

The state machine is in `pre-build/.pi-sync/state.json` and its stable policy is
in `.pi-preservation/sync-policy.json`. `ready` is the only state that permits a
matching protected task. `requires_pre_task_sync`, `synchronized_unscoped`,
`conflict`, and `refreshed` block protected tasks. Paths confined to `analysis/`
are explicitly unaffected, so independent investigations can continue during a
conflict as long as they do not write protected paths.

After a new authoritative manuscript revision has passed its applicable
acceptance gate, Ada runs:

```bash
git status --short --branch
./scripts/pi-workspace refresh --acceptance-file /outside/repository/acceptance.json
./scripts/pi-workspace preview
```

The acceptance document must be exported by an authenticated Paperclip human
decision or configured GitHub review, live outside the repository, name every
authoritative path being refreshed, and bind to the exact current `HEAD`:

```json
{
  "version": 1,
  "operation": "post_acceptance_refresh",
  "accepted_head": "<full commit SHA>",
  "accepted_paths": ["index.qmd"],
  "evidence": {
    "kind": "paperclip_human_decision",
    "decision_id": "<server identifier>",
    "verified_by": "<authenticated user identifier>",
    "decided_at": "<server timestamp>"
  }
}
```

The synchronizer rejects repository-local evidence, a mismatched commit,
uncommitted authoritative content, incomplete path coverage, and missing
authenticated metadata. This document authorizes only the post-acceptance
workspace refresh; it does not confer scientific approval, manuscript
integration authorization, merge authorization, or publication authorization.

`refresh` updates an unchanged workspace file from the authoritative revision.
Pending PI-only edits stay untouched. If both sides changed a text file, a clean
three-way merge is written to the workspace and the authoritative revision
becomes the new baseline; a later `import` proposes the combined text to the
authoritative file. Binary and delete/modify conflicts never auto-merge.

Commands return 0 on success, 2 for invalid state or configuration, and 3 for
an unresolved conflict. The complete structured result is printed and the most
recent mutating result is written to
`pre-build/.pi-sync/last-report.json`. On status 3, no managed manuscript, code,
figure, or baseline file is changed. Preserve all three versions, review the
reported hashes and Git state, and obtain the appropriate PI resolution before
retrying.

### Paperclip coordination

1. Charles Darwin records the intended repository paths on the task. If any are
   protected, he creates or identifies an Ada-owned synchronization task and
   adds it to `blockedByIssueIds` only for affected tasks.
2. Ada Lovelace checks out the synchronization task, runs `pre-task`, and
   attaches or comments the JSON report, task ID, Git head, and tree digest.
3. On conflict, Ada preserves the three versions and report and creates a
   human-only Paperclip question bound to the exact paths and hashes. Affected
   tasks remain blocked; unrelated `analysis/` investigations receive no
   synchronization blocker.
4. After the synchronization task completes, each affected agent runs
   `verify-ready` for its actual target paths. A nonzero result stops the task.
5. After an authoritative revision is accepted and committed, the authenticated
   external decision is exported outside the repository. Ada runs `refresh`,
   records its JSON report, and only then prepares the next protected task.
6. Karl Popper independently reviews the receipt, conflict behavior, and
   separation of approval gates. No agent approves its own work.

Run the independent preview configuration with:

```bash
./scripts/pi-workspace preview
```

It renders only `pre-build/index.qmd` into the ignored
`pre-build/.preview/` directory and does not publish or alter `docs/`.

### Generated and manually edited figures

R and Python generators must write new candidates below
`pre-build/.pi-sync/generated/`; they do not write to a live manuscript figure.
Promote a candidate only through the guarded command:

```bash
./scripts/project-env.sh .venv/bin/python \
  pre-build/python/generate_example_figure.py \
  pre-build/.pi-sync/generated/example-trend.png
./scripts/pi-workspace promote-figure \
  figures/generated/example-trend.png \
  pre-build/.pi-sync/generated/example-trend.png
```

Promotion is limited to `figures/generated/` and stops if the workspace target
differs from its baseline. It can therefore never overwrite an intervening
manual pixel edit. Put Photoshop-edited PNGs and their PSD sources below
`pre-build/figures/edited/`; `import` preserves both binary files together.
Automated generation can never target that directory.

Before proposing changes, fetch and incorporate the newest default-branch
commits. Use a normal merge or rebase only with a clean worktree. If Git reports
a conflict involving PI work, abort the operation without deleting files and
request PI resolution. Never force-push, hard-reset, or silently overwrite a PI
contribution. Uncommitted modifications and untracked files belong to their
creator and must be preserved.

Quarto reports under `analysis/` never regenerate `index.qmd`. The final
manuscript is changed only by an explicitly authorized integration task, through
a reviewable diff. Publication remains separately authorized.
