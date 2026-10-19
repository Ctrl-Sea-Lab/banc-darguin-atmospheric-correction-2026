#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
project_root=$(CDPATH= cd -- "$script_dir/.." && pwd -P)

read_tool_version() {
  local key=$1
  awk -v key="$key" '$1 == key ":" {gsub(/"/, "", $2); print $2; exit}' \
    "$project_root/config/toolchain.yml"
}

fail() {
  echo "environment check failed: $*" >&2
  exit 1
}

for command_name in uv python3 Rscript quarto gdalinfo; do
  command -v "$command_name" >/dev/null 2>&1 || fail "$command_name is unavailable"
done

[[ "$(uv --version | awk '{print $2}')" == "$(read_tool_version uv)" ]] || fail "uv version mismatch"
[[ "$(python3 -c 'import platform; print(platform.python_version())')" == "$(read_tool_version python)" ]] || fail "Python version mismatch"
[[ "$(Rscript --vanilla -e 'cat(paste(R.version$major, R.version$minor, sep="."))')" == "$(read_tool_version r)" ]] || fail "R version mismatch"
[[ "$(quarto --version)" == "$(read_tool_version quarto)" ]] || fail "Quarto version mismatch"
[[ "$(gdalinfo --version | sed -E 's/^GDAL ([0-9.]+).*/\1/')" == "$(read_tool_version gdal)" ]] || fail "GDAL version mismatch"

[[ -f "$project_root/uv.lock" ]] || fail "uv.lock is missing"
[[ -f "$project_root/renv.lock" ]] || fail "renv.lock is missing"
[[ -x "$project_root/.venv/bin/python" ]] || fail "project Python is missing"

cd "$project_root"
./scripts/project-env.sh uv lock --check --no-python-downloads
./scripts/project-env.sh uv sync --locked --dry-run --no-python-downloads --python "$(read_tool_version python)"
./scripts/project-env.sh .venv/bin/python tests/environment/validate_lockfiles.py
./scripts/project-env.sh .venv/bin/python -c \
  'import pathlib,sys; expected=(pathlib.Path.cwd()/".venv/bin/python").resolve(); actual=pathlib.Path(sys.executable).resolve(); assert actual==expected,(actual,expected)'
./scripts/project-env.sh Rscript -e \
  'root <- normalizePath(Sys.getenv("RENV_PROJECT")); lib <- normalizePath(.libPaths()[1L]); stopifnot(startsWith(lib, file.path(root, "renv", "library"))); status <- renv::status(project = root); if (!isTRUE(status$synchronized)) quit(status = 1L); py <- normalizePath(reticulate::py_config()$python); expected <- normalizePath(Sys.getenv("RETICULATE_PYTHON")); stopifnot(identical(py, expected))'

echo "Environment checks passed."
