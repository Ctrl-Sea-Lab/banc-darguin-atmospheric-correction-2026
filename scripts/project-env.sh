#!/usr/bin/env bash
set -euo pipefail

if (($# == 0)); then
  echo "usage: $0 COMMAND [ARG ...]" >&2
  exit 64
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
project_root=$(CDPATH= cd -- "$script_dir/.." && pwd -P)

export QUARTO_PYTHON="$project_root/.venv/bin/python"
export RETICULATE_PYTHON="$project_root/.venv/bin/python"
export RENV_PROJECT="$project_root"
export R_PROFILE_USER="$project_root/.Rprofile"
export UV_PROJECT_ENVIRONMENT="$project_root/.venv"
export UV_CACHE_DIR="$project_root/.cache/uv"
export RENV_PATHS_CACHE="$project_root/.cache/renv"
export UV_PYTHON_DOWNLOADS=manual
export PYTHONNOUSERSITE=1
export PIP_REQUIRE_VIRTUALENV=true

exec "$@"
