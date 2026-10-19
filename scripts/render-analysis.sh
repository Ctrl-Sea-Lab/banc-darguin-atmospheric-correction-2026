#!/usr/bin/env bash
set -euo pipefail

if (($# != 1)); then
  echo "usage: $0 analysis/<TASK-ID>_<concise-name>" >&2
  exit 64
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
project_root=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
analysis_root=$(realpath -e "$project_root/analysis")
target=$(realpath -e "$1")
target_parent=$(dirname -- "$target")
target_name=$(basename -- "$target")

[[ "$target_parent" == "$analysis_root" ]] || {
  echo "render error: target must be a direct child of analysis/" >&2
  exit 64
}
[[ "$target_name" != "_template" ]] || {
  echo "render error: analysis/_template is not an active investigation" >&2
  exit 64
}
[[ "$target_name" =~ ^[A-Z][A-Z0-9]*-[0-9]+_[a-z0-9][a-z0-9-]*$ ]] || {
  echo "render error: target name must be <TASK-ID>_<concise-name>" >&2
  exit 64
}
[[ -f "$target/report.qmd" && -f "$target/_quarto.yml" ]] || {
  echo "render error: target lacks report.qmd or _quarto.yml" >&2
  exit 64
}

(
  cd "$target"
  "$project_root/scripts/project-env.sh" quarto render report.qmd --to html
)

[[ -f "$target/report.html" ]] || {
  echo "render error: Quarto did not produce report.html" >&2
  exit 1
}
echo "Rendered $target/report.html"
