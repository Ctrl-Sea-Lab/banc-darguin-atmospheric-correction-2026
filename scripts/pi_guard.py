#!/usr/bin/env python3
"""Fail closed when an agent change overlaps protected PI contributions."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


REGISTRY_PATH = ".pi-preservation/registry.json"
MANUSCRIPT_FILES = {"index.qmd", "_quarto.yml"}
MANUSCRIPT_PREFIXES = ("manuscript/", "docs/")
EDITED_PREFIX = "figures/edited/"
SYNC_BASELINE_PREFIX = "pre-build/.pi-sync/baseline/"
SYNC_STATE_PATH = "pre-build/.pi-sync/state.json"
SAFEGUARD_PATHS = {
    "AGENTS.md",
    "PI_CONTRIBUTIONS.md",
    "PI_SYNC_AGENT_AMENDMENTS.md",
    ".pi-preservation/sync-policy.json",
    REGISTRY_PATH,
    ".github/workflows/pi-contribution-guard.yml",
    ".github/workflows/pi-contribution-tests.yml",
    "scripts/pi_guard.py",
    "scripts/pi_sync.py",
    "scripts/pi-workspace",
    "scripts/github_pi_authorization.py",
    "scripts/figure_io.py",
    "tests/test_pi_contribution_guard.py",
    "tests/test_pi_sync.py",
    "pre-build/README.md",
    "pre-build/_quarto.yml",
}


class GuardError(RuntimeError):
    """A deterministic guard or repository validation error."""


@dataclass(frozen=True)
class Change:
    status: str
    old_path: str | None
    new_path: str | None

    @property
    def paths(self) -> tuple[str, ...]:
        return tuple(path for path in (self.old_path, self.new_path) if path)


def git(repository: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    process = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if check and process.returncode:
        detail = process.stderr.strip() or process.stdout.strip()
        raise GuardError(f"git {' '.join(arguments)} failed: {detail}")
    return process


def repository_root(repository: Path | str) -> Path:
    candidate = Path(repository).resolve()
    root = git(candidate, "rev-parse", "--show-toplevel").stdout.strip()
    return Path(root).resolve()


def normalize_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise GuardError(f"invalid repository-relative path: {value!r}")
    normalized = path.as_posix()
    if normalized == ".":
        raise GuardError("registry paths must identify files")
    return normalized


def resolve_commit(repository: Path, revision: str) -> str:
    return git(repository, "rev-parse", "--verify", f"{revision}^{{commit}}").stdout.strip()


def merge_base(repository: Path, base_ref: str, head_ref: str) -> str:
    return git(repository, "merge-base", base_ref, head_ref).stdout.strip()


def path_exists(repository: Path, revision: str, path: str) -> bool:
    return git(repository, "cat-file", "-e", f"{revision}:{path}", check=False).returncode == 0


def changes_between(repository: Path, base: str, head: str) -> list[Change]:
    process = subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "diff",
            "--name-status",
            "-z",
            "--find-renames",
            f"{base}...{head}",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode:
        raise GuardError(process.stderr.decode(errors="replace").strip())
    fields = process.stdout.decode(errors="strict").split("\0")
    if fields and not fields[-1]:
        fields.pop()
    result: list[Change] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        if status.startswith(("R", "C")):
            if index + 1 >= len(fields):
                raise GuardError("malformed rename/copy entry from git diff")
            result.append(Change(status, fields[index], fields[index + 1]))
            index += 2
        else:
            if index >= len(fields):
                raise GuardError("malformed path entry from git diff")
            path = fields[index]
            index += 1
            result.append(Change(status, path if status.startswith("D") else None, None if status.startswith("D") else path))
    return result


def load_json_at_revision(repository: Path, revision: str, path: str) -> dict:
    process = git(repository, "show", f"{revision}:{path}", check=False)
    if process.returncode:
        return {"version": 1, "contributions": []}
    try:
        document = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        raise GuardError(f"{path} at {revision} is not valid JSON: {error}") from error
    if document.get("version") != 1 or not isinstance(document.get("contributions"), list):
        raise GuardError(f"{path} at {revision} does not match registry version 1")
    return document


def registry_entries(repository: Path, revisions: Iterable[str]) -> dict[str, dict]:
    entries: dict[str, dict] = {}
    for revision in revisions:
        document = load_json_at_revision(repository, revision, REGISTRY_PATH)
        for entry in document["contributions"]:
            if not isinstance(entry, dict) or "path" not in entry or "sha256" not in entry:
                raise GuardError(f"invalid contribution entry in {REGISTRY_PATH} at {revision}")
            path = normalize_path(str(entry["path"]))
            digest = str(entry["sha256"])
            if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
                raise GuardError(f"invalid SHA-256 for registered path {path}")
            entries[path] = entry
    return entries


def blob_bytes(repository: Path, revision: str, path: str) -> bytes:
    process = subprocess.run(
        ["git", "-C", str(repository), "show", f"{revision}:{path}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode:
        raise GuardError(f"registered path is absent at {revision}: {path}")
    return process.stdout


def verify_head_registry(repository: Path, head: str) -> None:
    document = load_json_at_revision(repository, head, REGISTRY_PATH)
    seen: set[str] = set()
    for entry in document["contributions"]:
        if not isinstance(entry, dict) or "path" not in entry or "sha256" not in entry:
            raise GuardError(f"invalid contribution entry in {REGISTRY_PATH} at {head}")
        path = normalize_path(str(entry["path"]))
        if path in seen:
            raise GuardError(f"duplicate registered contribution path: {path}")
        seen.add(path)
        actual = hashlib.sha256(blob_bytes(repository, head, path)).hexdigest()
        if actual != entry["sha256"]:
            raise GuardError(
                f"registered hash mismatch for {path}: expected {entry['sha256']}, found {actual}"
            )
        evidence = entry.get("evidence")
        if not isinstance(evidence, dict) or not all(
            evidence.get(field) for field in ("kind", "decision_id", "verified_commit")
        ):
            raise GuardError(f"registered path lacks provenance evidence: {path}")


def is_manuscript(path: str) -> bool:
    return path in MANUSCRIPT_FILES or path.startswith(MANUSCRIPT_PREFIXES)


def conflict_markers(repository: Path, head: str, paths: Iterable[str]) -> set[str]:
    marked: set[str] = set()
    needles = (b"<<<<<<< ", b"=======", b">>>>>>> ")
    for path in paths:
        if not path_exists(repository, head, path):
            continue
        data = blob_bytes(repository, head, path)
        if b"\x00" in data:
            continue
        lines = data.splitlines()
        if all(any(line.startswith(needle) for line in lines) for needle in needles):
            marked.add(path)
    return marked


def required_reviews(repository: Path, base: str, head: str) -> dict[str, set[str]]:
    contributions = registry_entries(repository, (base, head))
    changes = changes_between(repository, base, head)
    requirements: dict[str, set[str]] = {}

    def require(path: str, decision_type: str) -> None:
        requirements.setdefault(path, set()).add(decision_type)

    changed_head_paths: set[str] = set()
    for change in changes:
        if change.new_path:
            changed_head_paths.add(change.new_path)
        for path in change.paths:
            if is_manuscript(path):
                require(path, "manuscript_integration")
            if path in contributions:
                require(path, "pi_contribution_change")
            if path in SAFEGUARD_PATHS and path_exists(repository, base, path):
                require(path, "safeguard_change")
            if path == SYNC_STATE_PATH or path.startswith(SYNC_BASELINE_PREFIX):
                require(path, "safeguard_change")
            synchronized_baseline = f"{SYNC_BASELINE_PREFIX}{path}"
            if path_exists(repository, base, synchronized_baseline) or path_exists(
                repository, head, synchronized_baseline
            ):
                require(path, "pi_contribution_change")
            if path.startswith(EDITED_PREFIX) and not change.status.startswith("A"):
                require(path, "edited_asset_change")

    for path in conflict_markers(repository, head, changed_head_paths):
        require(path, "merge_conflict")
    return requirements


def validate_authorization(
    repository: Path,
    authorization_file: Path,
    base_commit: str,
    head_commit: str,
    requirements: dict[str, set[str]],
) -> None:
    authorization_file = authorization_file.resolve()
    try:
        authorization_file.relative_to(repository)
    except ValueError:
        pass
    else:
        raise GuardError("authorization evidence must be provided from outside the repository")
    try:
        document = json.loads(authorization_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise GuardError(f"cannot read authorization evidence: {error}") from error
    if document.get("version") != 1:
        raise GuardError("authorization evidence must use version 1")
    if document.get("base_commit") != base_commit or document.get("head_commit") != head_commit:
        raise GuardError("authorization evidence is not bound to the exact base and head commits")
    evidence = document.get("evidence")
    if not isinstance(evidence, dict) or evidence.get("kind") not in {
        "github_review",
        "paperclip_human_decision",
    }:
        raise GuardError("authorization lacks authenticated external evidence")
    if not all(evidence.get(field) for field in ("decision_id", "verified_by", "decided_at")):
        raise GuardError("authorization evidence is incomplete")
    authorized_paths = {normalize_path(path) for path in document.get("authorized_paths", [])}
    authorized_types = set(document.get("decision_types", []))
    required_paths = set(requirements)
    required_types = {item for values in requirements.values() for item in values}
    if not required_paths.issubset(authorized_paths):
        missing = sorted(required_paths - authorized_paths)
        raise GuardError(f"authorization does not cover protected paths: {', '.join(missing)}")
    if not required_types.issubset(authorized_types):
        missing = sorted(required_types - authorized_types)
        raise GuardError(f"authorization does not cover decision types: {', '.join(missing)}")


def report_document(
    base_commit: str, head_commit: str, requirements: dict[str, set[str]]
) -> dict:
    return {
        "version": 1,
        "base_commit": base_commit,
        "head_commit": head_commit,
        "protected_changes": [
            {"path": path, "decision_types": sorted(types)}
            for path, types in sorted(requirements.items())
        ],
        "required_paths": sorted(requirements),
        "required_decision_types": sorted(
            {decision_type for types in requirements.values() for decision_type in types}
        ),
    }


def write_report(path: Path | None, document: dict) -> None:
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def check_command(arguments: argparse.Namespace) -> int:
    repository = repository_root(arguments.repository)
    status = git(repository, "status", "--porcelain=v1", "--untracked-files=all").stdout
    if status:
        raise GuardError("working tree is not clean; preserve and resolve local files before checking")
    head_commit = resolve_commit(repository, arguments.head_ref)
    base_commit = merge_base(repository, arguments.base_ref, arguments.head_ref)
    requirements = required_reviews(repository, base_commit, head_commit)
    document = report_document(base_commit, head_commit, requirements)
    write_report(arguments.report_json, document)
    if requirements and arguments.authorization_file is None:
        print(json.dumps(document, indent=2))
        print("PI contribution guard: explicit review is required", file=sys.stderr)
        return 3
    if requirements:
        validate_authorization(
            repository,
            arguments.authorization_file,
            base_commit,
            head_commit,
            requirements,
        )
    verify_head_registry(repository, head_commit)
    if not requirements:
        print("PI contribution guard: no protected changes detected")
        return 0
    print("PI contribution guard: exact-revision external authorization verified")
    return 0


def preflight_command(arguments: argparse.Namespace) -> int:
    repository = repository_root(arguments.repository)
    status = git(repository, "status", "--porcelain=v1", "--untracked-files=all").stdout
    if status:
        print(status, end="", file=sys.stderr)
        raise GuardError("working tree contains modifications or untracked files; nothing was changed")
    branch = git(repository, "symbolic-ref", "--quiet", "--short", "HEAD", check=False).stdout.strip()
    if not branch:
        raise GuardError("detached HEAD is not an agent work branch")
    default_names = {"main", "master", "origin/main", "origin/master"}
    if branch in default_names:
        raise GuardError(f"refusing to work directly on default branch {branch}")
    base_commit = resolve_commit(repository, arguments.base_ref)
    head_commit = resolve_commit(repository, "HEAD")
    ancestor = git(repository, "merge-base", "--is-ancestor", base_commit, head_commit, check=False)
    if ancestor.returncode:
        raise GuardError(
            f"{arguments.base_ref} is not contained in HEAD; incorporate the fetched base before editing"
        )
    print(f"branch={branch}")
    print(f"base={base_commit}")
    print(f"head={head_commit}")
    print("working_tree=clean")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--repository", type=Path, default=Path.cwd())
    subparsers = result.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight", help="verify a safe agent worktree")
    preflight.add_argument("--base-ref", default="origin/main")
    preflight.set_defaults(handler=preflight_command)

    check = subparsers.add_parser("check", help="classify and gate a committed diff")
    check.add_argument("--base-ref", default="origin/main")
    check.add_argument("--head-ref", default="HEAD")
    check.add_argument("--authorization-file", type=Path)
    check.add_argument("--report-json", type=Path)
    check.set_defaults(handler=check_command)
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        return arguments.handler(arguments)
    except GuardError as error:
        print(f"PI contribution guard: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
