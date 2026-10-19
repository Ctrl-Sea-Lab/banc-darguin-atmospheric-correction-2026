#!/usr/bin/env python3
"""Validate lockfiles and dependency-source policy."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYPI = "https://pypi.org/simple"
CRAN = "CRAN"


def fail(message: str) -> None:
    raise SystemExit(f"lockfile validation failed: {message}")


def validate_direct_spec(spec: str) -> None:
    lowered = spec.lower()
    forbidden = (" @ ", "://", "git+", "file:", "../", "./")
    if any(marker in lowered for marker in forbidden):
        fail(f"non-registry Python dependency is not approved: {spec}")


def validate_pyproject() -> None:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        data = tomllib.load(stream)
    for spec in data.get("project", {}).get("dependencies", []):
        validate_direct_spec(spec)
    for specs in data.get("dependency-groups", {}).values():
        for spec in specs:
            validate_direct_spec(spec)
    sources = data.get("tool", {}).get("uv", {}).get("sources", {})
    if sources:
        fail("tool.uv.sources requires explicit review")
    if data.get("tool", {}).get("uv", {}).get("python-downloads") != "manual":
        fail("automatic Python downloads are not disabled")


def validate_uv_lock() -> None:
    with (ROOT / "uv.lock").open("rb") as stream:
        data = tomllib.load(stream)
    if not data.get("package"):
        fail("uv.lock contains no packages")
    for package in data["package"]:
        source = package.get("source", {})
        if "registry" in source and source["registry"].rstrip("/") != PYPI:
            fail(f"{package['name']} uses unapproved registry {source['registry']}")
        forbidden_keys = {"git", "url", "directory", "editable", "path"}
        if forbidden_keys.intersection(source):
            fail(f"{package['name']} uses a non-registry source")


def validate_renv_lock() -> None:
    with (ROOT / "renv.lock").open(encoding="utf-8") as stream:
        data = json.load(stream)
    repository_urls = {
        record["Name"]: record["URL"].rstrip("/")
        for record in data.get("R", {}).get("Repositories", [])
    }
    if repository_urls != {CRAN: "https://cloud.r-project.org"}:
        fail(f"unexpected R repositories: {repository_urls}")
    packages = data.get("Packages", {})
    if not packages:
        fail("renv.lock contains no packages")
    for name, record in packages.items():
        if record.get("Source") != "Repository" or record.get("Repository") != CRAN:
            fail(f"{name} has unapproved source metadata")
        if not record.get("Version"):
            fail(f"{name} has no exact version")
        forbidden = ("RemoteUrl", "RemoteHost", "RemoteRepo", "Path")
        if any(record.get(field) for field in forbidden):
            fail(f"{name} contains remote or local source fields")


def main() -> int:
    validate_pyproject()
    validate_uv_lock()
    validate_renv_lock()
    print("Lockfile sources and versions are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
