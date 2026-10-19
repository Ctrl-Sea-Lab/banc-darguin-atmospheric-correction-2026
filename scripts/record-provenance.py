#!/usr/bin/env python3
"""Record reproducibility metadata for one investigation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_ROOT = (ROOT / "analysis").resolve()
TARGET_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*-[0-9]+_[a-z0-9][a-z0-9-]*$")


def run(*args: str) -> str:
    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except FileNotFoundError:
        raise SystemExit(f"required tool is unavailable: {args[0]}") from None
    return result.stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_parameters(values: list[str]) -> dict[str, str]:
    parameters: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"parameter must be KEY=VALUE: {value}")
        key, item = value.split("=", 1)
        if not key or key in parameters:
            raise ValueError(f"invalid or duplicate parameter: {key}")
        parameters[key] = item
    return parameters


def r_packages() -> list[dict[str, str]]:
    script = (
        'x <- installed.packages(); '
        'write.table(x[, c("Package", "Version", "LibPath"), drop=FALSE], '
        'row.names=FALSE, col.names=FALSE, quote=FALSE, sep="\\t")'
    )
    rows = run("Rscript", "--vanilla", "-e", script)
    packages = []
    for row in rows.splitlines():
        name, version, library = row.split("\t", 2)
        packages.append({"name": name, "version": version, "library": library})
    return packages


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("investigation")
    parser.add_argument("--render-command", required=True)
    parser.add_argument("--parameter", action="append", default=[])
    parser.add_argument(
        "--validation-status",
        choices=("passed", "failed", "not_run"),
        default="not_run",
    )
    options = parser.parse_args()

    target = Path(options.investigation).resolve(strict=True)
    if target == ANALYSIS_ROOT / "_template":
        parser.error("analysis/_template is not an active investigation")
    if target.parent != ANALYSIS_ROOT or not TARGET_PATTERN.fullmatch(target.name):
        parser.error("investigation must be analysis/<TASK-ID>_<concise-name>")

    lockfiles = {}
    for name in ("uv.lock", "renv.lock"):
        path = ROOT / name
        if not path.is_file():
            parser.error(f"required lockfile is missing: {name}")
        lockfiles[name] = {"path": name, "sha256": sha256(path)}

    expected_python = (ROOT / ".venv" / "bin" / "python").resolve(strict=True)
    if Path(sys.executable).resolve() != expected_python:
        parser.error("run with the project virtual-environment Python")

    git_status = run("git", "status", "--porcelain")
    python_packages = sorted(
        (
            {"name": distribution.metadata["Name"], "version": distribution.version}
            for distribution in importlib.metadata.distributions()
            if distribution.metadata["Name"]
        ),
        key=lambda item: item["name"].lower(),
    )

    record = {
        "schema_version": 1,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "investigation": str(target.relative_to(ROOT)),
        "git": {
            "revision": run("git", "rev-parse", "HEAD"),
            "dirty": bool(git_status),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "tools": {
            "python": platform.python_version(),
            "python_executable": str(expected_python),
            "r": run("Rscript", "--vanilla", "-e", 'cat(paste(R.version$major, R.version$minor, sep="."))'),
            "quarto": run("quarto", "--version"),
            "gdal": run("gdalinfo", "--version"),
            "uv": run("uv", "--version"),
        },
        "lockfiles": lockfiles,
        "bindings": {
            "QUARTO_PYTHON": os.environ.get("QUARTO_PYTHON"),
            "RETICULATE_PYTHON": os.environ.get("RETICULATE_PYTHON"),
            "RENV_PROJECT": os.environ.get("RENV_PROJECT"),
        },
        "render_command": options.render_command,
        "parameters": parse_parameters(options.parameter),
        "validation_status": options.validation_status,
        "packages": {"python": python_packages, "r": r_packages()},
    }

    destination = target / "provenance" / "environment.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=destination.parent, delete=False
    ) as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(destination)
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
