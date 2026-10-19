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
  echo "bootstrap error: $*" >&2
  exit 1
}

for command_name in uv python3 Rscript quarto gdalinfo sha256sum; do
  command -v "$command_name" >/dev/null 2>&1 || \
    fail "$command_name is not provisioned; host-tool installation requires separate approval"
done

expected_uv=$(read_tool_version uv)
expected_python=$(read_tool_version python)
expected_r=$(read_tool_version r)
expected_quarto=$(read_tool_version quarto)
expected_gdal=$(read_tool_version gdal)

actual_uv=$(uv --version | awk '{print $2}')
actual_python=$(python3 -c 'import platform; print(platform.python_version())')
actual_r=$(Rscript --vanilla -e 'cat(paste(R.version$major, R.version$minor, sep="."))')
actual_quarto=$(quarto --version)
actual_gdal=$(gdalinfo --version | sed -E 's/^GDAL ([0-9.]+).*/\1/')

[[ "$actual_uv" == "$expected_uv" ]] || fail "uv $actual_uv found; expected $expected_uv"
[[ "$actual_python" == "$expected_python" ]] || fail "Python $actual_python found; expected $expected_python"
[[ "$actual_r" == "$expected_r" ]] || fail "R $actual_r found; expected $expected_r"
[[ "$actual_quarto" == "$expected_quarto" ]] || fail "Quarto $actual_quarto found; expected $expected_quarto"
[[ "$actual_gdal" == "$expected_gdal" ]] || fail "GDAL $actual_gdal found; expected $expected_gdal"

[[ -f "$project_root/uv.lock" ]] || fail "uv.lock is missing"
[[ -f "$project_root/renv.lock" ]] || fail "renv.lock is missing"

cd "$project_root"
./scripts/project-env.sh uv sync --locked --no-python-downloads --python "$expected_python"
./scripts/project-env.sh Rscript --vanilla scripts/bootstrap-renv.R restore
./scripts/check-env.sh
