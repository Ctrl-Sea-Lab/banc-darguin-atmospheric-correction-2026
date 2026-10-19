#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
project_root=$(CDPATH= cd -- "$script_dir/../.." && pwd -P)

for fixture in python r mixed; do
  (
    cd "$script_dir/smoke/$fixture"
    "$project_root/scripts/project-env.sh" quarto render report.qmd
    [[ -f _output/report.html ]]
  )
done

echo "Python, R, and mixed-language Quarto smoke renders passed."
