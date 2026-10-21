#!/usr/bin/env bash
set -euo pipefail
analysis_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
repo_dir=$(CDPATH= cd -- "$analysis_dir/../.." && pwd -P)
ctr54_python=${CTR54_PYTHON:-"$repo_dir/.venv/bin/python"}
export CTR54_SCRATCH=${CTR54_SCRATCH:-/tmp/ctr54-paired-reflectance}
for step in 01_inventory 09_fill_audit 02_process 03_validate 04_figures; do
  "$ctr54_python" "$analysis_dir/scripts/$step.py"
done
Rscript --vanilla "$analysis_dir/scripts/05_R_crosscheck.R" "$analysis_dir"
"$ctr54_python" "$analysis_dir/scripts/06_input_manifest.py"
"$ctr54_python" "$analysis_dir/scripts/07_report.py"
cd "$repo_dir"
./scripts/render-analysis.sh "$analysis_dir"
