# Dependency management

## Boundary and sources

One Git repository owns one `.venv/`, one `renv/library/`, and repository-local
`.cache/uv/` and `.cache/renv/` directories. These generated directories are
ignored. `uv.lock` and `renv.lock` are the dependency truth and must be
committed.

The only approved default registries are:

- Python: `https://pypi.org/simple`
- R: `https://cloud.r-project.org`

VCS, URL, local-path, private-index, credentialed, and unknown-source
dependencies require explicit review before use. Lockfiles do not reproduce OS
packages, native libraries, drivers, external executables, or remote data;
record those in provenance.

## Restore

`./scripts/bootstrap-env.sh` checks every host tool against
`config/toolchain.yml`, refuses automatic Python downloads, synchronizes Python
exactly from `uv.lock`, bootstraps the pinned `renv` release into the project
library, and restores `renv.lock`. It does not install host tools or native
libraries.

Run `./scripts/check-env.sh` after restore and before each pull request. The
check is read-only: it verifies tool versions, lock/manifest agreement,
environment location, R lock sources, and interpreter bindings.

## Dependency changes

Work on a task branch. Use `uv add`, `uv remove`, or a deliberately scoped
`uv lock --upgrade-package <name>` for Python. Use
`scripts/manage-r-dependencies.R` for R. Review direct-manifest and lockfile
diffs, explain why the package is needed, then run tests and smoke renders.

Do not run unconstrained bulk upgrades during rendering or analysis. Do not use
`pip install`, `uv pip install --system`, global/user R libraries, or automatic
Python downloads as shortcuts.

## Rollback

Revert the manifest and lockfile changes together, move only the generated
environment directories for this repository aside, and restore again:

```bash
git restore --source=<reviewed-revision> -- pyproject.toml uv.lock renv.lock
mv .venv .venv.failed
mv renv/library renv/library.failed
./scripts/bootstrap-env.sh
```

Inspect the moved environments before deleting them. Never apply this procedure
to another repository or to raw/scientific data.

## System requirements and failures

If compilation or import fails because a system header, shared library,
compiler, GDAL component, or other native prerequisite is missing:

1. Preserve the package name/version and complete error log.
2. Record the detected native requirement and current toolchain versions.
3. Stop without using `sudo` or an OS package manager.
4. Request PI/infrastructure approval for the exact host change.

If lockfiles drift, do not silently regenerate them. Determine whether the
manifest or lockfile is the reviewed source, make an intentional dependency
change, and include the resulting diff in the pull request.

## Pull-request contract

Every dependency-changing pull request includes the direct manifest and
lockfile diffs, rationale, validation output, smoke-render result, and any
uninstalled system requirement. It must not include caches, environments,
credentials, raw data, or unrelated manuscript changes. Independent review is
required; merge and publication remain separately authorized actions.
