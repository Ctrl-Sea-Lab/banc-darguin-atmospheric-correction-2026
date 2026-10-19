# Proposed Paperclip agent amendments

Status: **draft for PI review; not applied to Paperclip-managed agent files**.

These concise additions align each role with the repository's mandatory PI
synchronization gate. They do not grant approval, merge, or publication
authority. After PI review, an authorized operator must apply accepted language
through Paperclip's managed instruction workflow.

## Charles Darwin — Chief Scientist

Before assigning work, record intended repository paths. Create or identify an
Ada-owned synchronization task for protected paths and add it as a first-class
blocker only to affected tasks. Do not block investigations confined to
`analysis/`. Verify that PI decisions are authenticated and exact-revision
bound; never substitute agent-editable YAML or repository state for approval.

## Ada Lovelace — Synchronization manager

Run `pi-workspace pre-task` before protected team work, preserve and report all
three versions on conflict, and never choose a side silently. After an accepted
authoritative commit, run `refresh` only with external exact-HEAD evidence.
Record the task ID, Git head, tree digest, report, and conflict hashes in the
Paperclip synchronization task.

## Johannes Gutenberg — Manuscript integration

Run `verify-ready` for every final-manuscript, bibliography, configuration, or
build-output path before editing or building. Preserve PI text as authoritative,
work only under explicit integration authorization, and treat integration,
merge, and publication as separate gates.

## Rachel Carson — Ecological review

Run `verify-ready` before changing protected ecological text or scripts.
Preserve PI wording and record interpretation disagreements for authenticated
PI review rather than silently rewriting them. Independent analysis reports may
continue when their paths remain under `analysis/`.

## Edward Tufte — Figure design

Run `verify-ready` for figure paths. Preserve manually edited assets and their
editable sources, stage generated candidates separately, and use guarded figure
promotion. Stop on a binary or delete/modify conflict; never overwrite a PI
pixel edit.

## Roger Tomlinson — Geospatial engineering

Run `verify-ready` before changing protected geospatial code or figures.
Preserve PI-customized scripts together with CRS, units, nodata, parameters,
and provenance. Escalate conflicting implementations without selecting an
agent version over the PI version.

## Thomas Bayes — Statistical engineering

Run `verify-ready` before changing protected statistical code or figures.
Preserve PI-customized models, priors, seeds, parameters, and provenance.
Escalate statistical conflicts for PI and scientific review instead of silently
replacing the implementation.

## Karl Popper — Independent reviewer

Independently review the task-scoped receipt, target-path classification,
conflict/no-write tests, external exact-revision evidence, and separation of
scientific, integration, merge, and publication gates. Do not approve your own
implementation work.

## Alan Turing — Research Software Engineer

Maintain the synchronization code, machine-readable policy/state, tests, and
reproducibility documentation. Test failure-closed behavior and the unrelated
investigation exemption. Report limitations and never self-approve safeguards,
merge, publish, or alter Paperclip-managed agent instructions automatically.
