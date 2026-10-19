#!/usr/bin/env python3
"""Synchronize the PI-editable pre-build workspace without destructive Git operations."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


VERSION = 1
WORKSPACE_DIRECTORY = "pre-build"
SYNC_DIRECTORY = ".pi-sync"
POLICY_RELATIVE = PurePosixPath(".pi-preservation", "sync-policy.json")
STATE_RELATIVE = PurePosixPath(WORKSPACE_DIRECTORY, SYNC_DIRECTORY, "state.json")
REPORT_RELATIVE = PurePosixPath(WORKSPACE_DIRECTORY, SYNC_DIRECTORY, "last-report.json")
BASELINE_RELATIVE = PurePosixPath(WORKSPACE_DIRECTORY, SYNC_DIRECTORY, "baseline")
GENERATED_RELATIVE = PurePosixPath(WORKSPACE_DIRECTORY, SYNC_DIRECTORY, "generated")
SINGLE_FILES = ("index.qmd", "library.bib")
MANAGED_DIRECTORIES = ("R", "python", "figures")
PROTECTED_SINGLE_FILES = {
    "index.qmd",
    "library.bib",
    "_quarto.yml",
    "AGENTS.md",
    "PI_CONTRIBUTIONS.md",
}
PROTECTED_PREFIXES = (
    "manuscript/",
    "docs/",
    "R/",
    "python/",
    "figures/",
    "pre-build/",
    ".pi-preservation/",
)
WORKFLOW_STATES = {
    "requires_pre_task_sync",
    "synchronized_unscoped",
    "ready",
    "conflict",
    "refreshed",
}
TEXT_SUFFIXES = {
    ".bib",
    ".json",
    ".md",
    ".py",
    ".qmd",
    ".r",
    ".txt",
    ".yaml",
    ".yml",
}


class SyncError(RuntimeError):
    """A deterministic validation or synchronization error."""


class SyncConflict(SyncError):
    """Raised after a conflict report has been prepared."""

    def __init__(self, report: dict) -> None:
        super().__init__("unresolved synchronization conflicts")
        self.report = report


@dataclass(frozen=True)
class GitContext:
    head: str
    branch: str
    status: tuple[str, ...]
    changes_since_sync: tuple[str, ...]


def sha256(content: bytes | None) -> str | None:
    return None if content is None else hashlib.sha256(content).hexdigest()


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
        raise SyncError(f"git {' '.join(arguments)} failed: {detail}")
    return process


def repository_root(candidate: Path | str) -> Path:
    candidate = Path(candidate).resolve()
    root = git(candidate, "rev-parse", "--show-toplevel").stdout.strip()
    return Path(root).resolve()


def normalized_relative(value: str | PurePosixPath) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or path == PurePosixPath("."):
        raise SyncError(f"invalid repository-relative path: {value!s}")
    return path


def safe_read(path: Path) -> bytes | None:
    if path.is_symlink():
        raise SyncError(f"managed paths must not be symbolic links: {path}")
    if not path.exists():
        return None
    if not path.is_file():
        raise SyncError(f"managed path is not a regular file: {path}")
    return path.read_bytes()


def discover_files(root: Path, relative_roots: Iterable[PurePosixPath]) -> set[PurePosixPath]:
    discovered: set[PurePosixPath] = set()
    for relative_root in relative_roots:
        path = root.joinpath(*relative_root.parts)
        if path.is_symlink():
            raise SyncError(f"managed paths must not be symbolic links: {path}")
        if not path.exists():
            continue
        if path.is_file():
            discovered.add(relative_root)
            continue
        for candidate in path.rglob("*"):
            if candidate.is_symlink():
                raise SyncError(f"managed paths must not be symbolic links: {candidate}")
            if not candidate.is_file():
                continue
            relative = candidate.relative_to(root)
            if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
                continue
            if candidate.name.endswith(("~", ".tmp", ".pyc", ".pyo")):
                continue
            discovered.add(PurePosixPath(relative.as_posix()))
    return discovered


def managed_paths(repository: Path) -> list[PurePosixPath]:
    canonical_roots = tuple(PurePosixPath(path) for path in (*SINGLE_FILES, *MANAGED_DIRECTORIES))
    workspace_root = repository / WORKSPACE_DIRECTORY
    baseline_root = workspace_root / SYNC_DIRECTORY / "baseline"

    paths = discover_files(repository, canonical_roots)
    paths.update(discover_files(workspace_root, canonical_roots))
    paths.update(discover_files(baseline_root, canonical_roots))
    return sorted(paths, key=lambda item: item.as_posix())


def protected_task_path(value: str) -> bool:
    path = normalized_relative(value).as_posix()
    return path in PROTECTED_SINGLE_FILES or path.startswith(PROTECTED_PREFIXES)


def snapshot_digest(snapshot: dict[str, dict[str, str | None]]) -> str:
    serialized = json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(serialized).hexdigest()


def actual_snapshot(repository: Path) -> dict[str, dict[str, str | None]]:
    snapshot: dict[str, dict[str, str | None]] = {}
    for path in managed_paths(repository):
        snapshot[path.as_posix()] = {
            "authoritative": sha256(safe_read(repository.joinpath(*path.parts))),
            "workspace": sha256(
                safe_read(repository / WORKSPACE_DIRECTORY / Path(*path.parts))
            ),
            "baseline": sha256(
                safe_read(repository.joinpath(*BASELINE_RELATIVE.parts, *path.parts))
            ),
        }
    return snapshot


def workflow_document(
    state: str,
    operation: str,
    digest: str,
    *,
    task_id: str | None = None,
    prepared_by: str | None = None,
    acceptance: dict | None = None,
) -> dict:
    if state not in WORKFLOW_STATES:
        raise SyncError(f"unsupported workflow state: {state}")
    document = {
        "state": state,
        "last_operation": operation,
        "blocking_scope": None if state == "ready" else "protected_content",
        "task_id": task_id,
        "prepared_by": prepared_by,
        "managed_tree_sha256": digest,
    }
    if acceptance is not None:
        document["acceptance"] = acceptance
    return document


def load_state(repository: Path, required: bool = True) -> dict | None:
    state_path = repository.joinpath(*STATE_RELATIVE.parts)
    if not state_path.exists():
        if required:
            raise SyncError("pre-build is not initialized; run scripts/pi-workspace init")
        return None
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError(f"cannot read synchronization state: {error}") from error
    if (
        state.get("version") != VERSION
        or not isinstance(state.get("files"), dict)
        or not isinstance(state.get("workflow"), dict)
        or state["workflow"].get("state") not in WORKFLOW_STATES
    ):
        raise SyncError(f"unsupported synchronization state in {state_path}")
    for path_text, expected in state["files"].items():
        path = normalized_relative(path_text)
        actual = sha256(safe_read(repository.joinpath(*BASELINE_RELATIVE.parts, *path.parts)))
        if actual != expected:
            raise SyncError(
                f"baseline hash mismatch for {path}; restore it from Git or resolve it explicitly"
            )
    return state


def head_path_bytes(repository: Path, path: PurePosixPath) -> bytes | None:
    process = subprocess.run(
        ["git", "-C", str(repository), "show", f"HEAD:{path.as_posix()}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode:
        return None
    return process.stdout


def validate_refresh_acceptance(
    repository: Path,
    acceptance_file: Path | None,
    changed_paths: list[PurePosixPath],
) -> dict | None:
    if not changed_paths:
        return None
    if acceptance_file is None:
        raise SyncError(
            "refresh would propagate authoritative changes; provide externally authenticated "
            "acceptance with --acceptance-file"
        )
    acceptance_file = acceptance_file.resolve()
    try:
        acceptance_file.relative_to(repository)
    except ValueError:
        pass
    else:
        raise SyncError("refresh acceptance evidence must be outside the repository")
    try:
        document = json.loads(acceptance_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError(f"cannot read refresh acceptance evidence: {error}") from error
    if not isinstance(document, dict):
        raise SyncError("refresh acceptance evidence must be a JSON object")

    head = git(repository, "rev-parse", "HEAD").stdout.strip()
    if (
        document.get("version") != 1
        or document.get("operation") != "post_acceptance_refresh"
        or document.get("accepted_head") != head
    ):
        raise SyncError("refresh acceptance is not bound to the exact current HEAD")
    evidence = document.get("evidence")
    if not isinstance(evidence, dict) or evidence.get("kind") not in {
        "github_review",
        "paperclip_human_decision",
    }:
        raise SyncError("refresh acceptance lacks authenticated external evidence")
    if not all(evidence.get(field) for field in ("decision_id", "verified_by", "decided_at")):
        raise SyncError("refresh acceptance evidence is incomplete")

    accepted_values = document.get("accepted_paths")
    if not isinstance(accepted_values, list) or not all(
        isinstance(value, str) for value in accepted_values
    ):
        raise SyncError("refresh acceptance must contain a list of accepted paths")
    accepted_paths = {normalized_relative(value).as_posix() for value in accepted_values}
    required_paths = {path.as_posix() for path in changed_paths}
    if not required_paths.issubset(accepted_paths):
        missing = ", ".join(sorted(required_paths - accepted_paths))
        raise SyncError(f"refresh acceptance does not cover authoritative paths: {missing}")
    for path in changed_paths:
        if safe_read(repository.joinpath(*path.parts)) != head_path_bytes(repository, path):
            raise SyncError(
                f"authoritative path is not committed at accepted HEAD: {path.as_posix()}"
            )
    return {
        "accepted_head": head,
        "accepted_paths": sorted(required_paths),
        "evidence": {
            field: evidence[field]
            for field in ("kind", "decision_id", "verified_by", "decided_at")
        },
    }


def git_context(repository: Path, previous_head: str | None = None) -> GitContext:
    head = git(repository, "rev-parse", "HEAD").stdout.strip()
    branch_process = git(repository, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    branch = branch_process.stdout.strip() or "(detached)"
    scopes = [*SINGLE_FILES, *MANAGED_DIRECTORIES, WORKSPACE_DIRECTORY]
    status_text = git(
        repository,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        *scopes,
    ).stdout
    changes: tuple[str, ...] = ()
    if previous_head:
        valid = git(repository, "cat-file", "-e", f"{previous_head}^{{commit}}", check=False)
        if valid.returncode == 0:
            diff = git(
                repository,
                "diff",
                "--name-status",
                f"{previous_head}..HEAD",
                "--",
                *scopes,
                check=False,
            )
            if diff.returncode == 0:
                changes = tuple(line for line in diff.stdout.splitlines() if line)
    return GitContext(
        head=head,
        branch=branch,
        status=tuple(line for line in status_text.splitlines() if line),
        changes_since_sync=changes,
    )


def git_report(context: GitContext) -> dict:
    return {
        "head": context.head,
        "branch": context.branch,
        "status": list(context.status),
        "changes_since_sync": list(context.changes_since_sync),
    }


def is_mergeable_text(path: PurePosixPath, *contents: bytes | None) -> bool:
    if path.suffix.lower() not in TEXT_SUFFIXES or any(content is None for content in contents):
        return False
    try:
        for content in contents:
            assert content is not None
            content.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return all(b"\0" not in content for content in contents if content is not None)


def merge_text(current: bytes, baseline: bytes, other: bytes) -> tuple[bytes | None, str | None]:
    with tempfile.TemporaryDirectory(prefix="pi-sync-merge-") as temporary_name:
        temporary = Path(temporary_name)
        current_path = temporary / "current"
        baseline_path = temporary / "baseline"
        other_path = temporary / "other"
        current_path.write_bytes(current)
        baseline_path.write_bytes(baseline)
        other_path.write_bytes(other)
        process = subprocess.run(
            [
                "git",
                "merge-file",
                "-p",
                "--diff3",
                str(current_path),
                str(baseline_path),
                str(other_path),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    if process.returncode == 0:
        return process.stdout, None
    if process.returncode == 1:
        return None, "overlapping text edits"
    detail = process.stderr.decode(errors="replace").strip()
    raise SyncError(f"git merge-file failed: {detail or process.returncode}")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def apply_transaction(repository: Path, changes: dict[Path, bytes | None]) -> None:
    effective = {
        path: content for path, content in changes.items() if safe_read(path) != content
    }
    if not effective:
        return
    with tempfile.TemporaryDirectory(dir=repository, prefix=".pi-sync-transaction-") as temporary_name:
        temporary = Path(temporary_name)
        backups: dict[Path, Path | None] = {}
        completed: list[Path] = []
        try:
            for index, path in enumerate(effective):
                existing = safe_read(path)
                if existing is None:
                    backups[path] = None
                else:
                    backup = temporary / str(index)
                    backup.write_bytes(existing)
                    backups[path] = backup
            for path, content in effective.items():
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_write(path, content)
                completed.append(path)
        except BaseException:
            for path in reversed(completed):
                backup = backups[path]
                if backup is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_write(path, backup.read_bytes())
            raise


def state_bytes(
    context: GitContext,
    baseline: dict[PurePosixPath, bytes | None],
    workflow: dict,
) -> bytes:
    document = {
        "version": VERSION,
        "last_synced_git_head": context.head,
        "last_synced_git_branch": context.branch,
        "workflow": workflow,
        "files": {
            path.as_posix(): sha256(content)
            for path, content in sorted(baseline.items(), key=lambda item: item[0].as_posix())
            if content is not None
        },
    }
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode()


def write_report(repository: Path, report: dict) -> None:
    report_path = repository.joinpath(*REPORT_RELATIVE.parts)
    atomic_write(report_path, (json.dumps(report, indent=2, sort_keys=True) + "\n").encode())


def initialize(repository: Path) -> dict:
    if load_state(repository, required=False) is not None:
        raise SyncError("pre-build is already initialized; use import or refresh")
    context = git_context(repository)
    changes: dict[Path, bytes | None] = {}
    baseline: dict[PurePosixPath, bytes | None] = {}
    records: list[dict] = []
    for path in managed_paths(repository):
        authoritative = safe_read(repository.joinpath(*path.parts))
        workspace = safe_read(repository / WORKSPACE_DIRECTORY / Path(*path.parts))
        if authoritative is None and workspace is not None:
            raise SyncError(f"refusing to initialize over workspace-only file: {path}")
        if authoritative is None:
            continue
        if workspace is not None and workspace != authoritative:
            raise SyncError(f"refusing to initialize over differing workspace file: {path}")
        workspace_path = repository / WORKSPACE_DIRECTORY / Path(*path.parts)
        baseline_path = repository.joinpath(*BASELINE_RELATIVE.parts, *path.parts)
        changes[workspace_path] = authoritative
        changes[baseline_path] = authoritative
        baseline[path] = authoritative
        records.append({"path": path.as_posix(), "action": "initialized"})
    if not records:
        raise SyncError("no authoritative manuscript, bibliography, code, or figure files found")
    snapshot = {
        path.as_posix(): {
            "authoritative": sha256(content),
            "workspace": sha256(content),
            "baseline": sha256(content),
        }
        for path, content in baseline.items()
    }
    workflow = workflow_document(
        "requires_pre_task_sync",
        "init",
        snapshot_digest(snapshot),
    )
    changes[repository.joinpath(*STATE_RELATIVE.parts)] = state_bytes(
        context, baseline, workflow
    )
    apply_transaction(repository, changes)
    report = {
        "version": VERSION,
        "operation": "init",
        "result": "success",
        "git": git_report(context),
        "workflow": workflow,
        "changes": records,
        "conflicts": [],
    }
    write_report(repository, report)
    return report


def synchronize(
    repository: Path,
    operation: str,
    *,
    acceptance_file: Path | None = None,
    task_id: str | None = None,
    prepared_by: str | None = None,
) -> dict:
    if operation not in {"import", "refresh"}:
        raise SyncError(f"unsupported operation: {operation}")
    if bool(task_id) != bool(prepared_by):
        raise SyncError("task-scoped synchronization requires both task ID and preparing agent")
    if task_id is not None and (not task_id.strip() or not prepared_by or not prepared_by.strip()):
        raise SyncError("task ID and preparing agent must be non-empty")
    state = load_state(repository)
    assert state is not None
    context = git_context(repository, state.get("last_synced_git_head"))
    paths = managed_paths(repository)
    authoritative_changes = [
        path
        for path in paths
        if safe_read(repository.joinpath(*path.parts))
        != safe_read(repository.joinpath(*BASELINE_RELATIVE.parts, *path.parts))
    ]
    acceptance = (
        validate_refresh_acceptance(repository, acceptance_file, authoritative_changes)
        if operation == "refresh"
        else None
    )
    changes: dict[Path, bytes | None] = {}
    records: list[dict] = []
    conflicts: list[dict] = []
    baseline_after: dict[PurePosixPath, bytes | None] = {}
    final_snapshot: dict[str, dict[str, str | None]] = {}

    for path in paths:
        authoritative_path = repository.joinpath(*path.parts)
        workspace_path = repository / WORKSPACE_DIRECTORY / Path(*path.parts)
        baseline_path = repository.joinpath(*BASELINE_RELATIVE.parts, *path.parts)
        authoritative = safe_read(authoritative_path)
        workspace = safe_read(workspace_path)
        baseline = safe_read(baseline_path)
        baseline_after[path] = baseline
        hashes = {
            "baseline_sha256": sha256(baseline),
            "authoritative_sha256": sha256(authoritative),
            "workspace_sha256": sha256(workspace),
        }

        action: str | None = None
        desired_authoritative = authoritative
        desired_workspace = workspace
        desired_baseline = baseline

        if authoritative == baseline and workspace == baseline:
            action = None
        elif authoritative == workspace:
            desired_baseline = authoritative
            action = "advanced-baseline"
        elif workspace == baseline:
            desired_workspace = authoritative
            desired_baseline = authoritative
            action = "refreshed-from-authoritative"
        elif authoritative == baseline:
            if operation == "import":
                desired_authoritative = workspace
                desired_baseline = workspace
                action = "imported-from-workspace"
            else:
                action = "preserved-workspace-edit"
        else:
            if is_mergeable_text(path, authoritative, baseline, workspace):
                assert authoritative is not None and baseline is not None and workspace is not None
                if operation == "import":
                    merged, reason = merge_text(authoritative, baseline, workspace)
                    if reason is None:
                        desired_authoritative = merged
                        desired_workspace = merged
                        desired_baseline = merged
                        action = "merged-into-authoritative"
                else:
                    merged, reason = merge_text(workspace, baseline, authoritative)
                    if reason is None:
                        desired_workspace = merged
                        desired_baseline = authoritative
                        action = "merged-into-workspace"
                if reason is not None:
                    conflicts.append({"path": path.as_posix(), "reason": reason, **hashes})
                    continue
            else:
                reason = (
                    "delete/modify conflict"
                    if None in {authoritative, baseline, workspace}
                    else "divergent binary changes"
                )
                conflicts.append({"path": path.as_posix(), "reason": reason, **hashes})
                continue

        baseline_after[path] = desired_baseline
        final_snapshot[path.as_posix()] = {
            "authoritative": sha256(desired_authoritative),
            "workspace": sha256(desired_workspace),
            "baseline": sha256(desired_baseline),
        }
        if desired_authoritative != authoritative:
            changes[authoritative_path] = desired_authoritative
        if desired_workspace != workspace:
            changes[workspace_path] = desired_workspace
        if desired_baseline != baseline:
            changes[baseline_path] = desired_baseline
        if action is not None:
            records.append({"path": path.as_posix(), "action": action, **hashes})

    workflow_state = (
        "conflict"
        if conflicts
        else "ready"
        if operation == "import" and task_id and prepared_by
        else "synchronized_unscoped"
        if operation == "import"
        else "refreshed"
    )
    if operation == "refresh" and not authoritative_changes and not conflicts:
        workflow = state["workflow"]
    else:
        workflow = workflow_document(
            workflow_state,
            "pre-task" if operation == "import" and task_id else operation,
            snapshot_digest(final_snapshot if not conflicts else actual_snapshot(repository)),
            task_id=task_id,
            prepared_by=prepared_by,
            acceptance=acceptance,
        )
    report = {
        "version": VERSION,
        "operation": "pre-task" if operation == "import" and task_id else operation,
        "result": "conflict" if conflicts else "success",
        "git": git_report(context),
        "workflow": workflow,
        "changes": [] if conflicts else records,
        "planned_changes": records if conflicts else [],
        "conflicts": conflicts,
    }
    if conflicts:
        current_baseline = {
            path: safe_read(repository.joinpath(*BASELINE_RELATIVE.parts, *path.parts))
            for path in paths
        }
        apply_transaction(
            repository,
            {
                repository.joinpath(*STATE_RELATIVE.parts): state_bytes(
                    context, current_baseline, workflow
                )
            },
        )
        write_report(repository, report)
        raise SyncConflict(report)

    changes[repository.joinpath(*STATE_RELATIVE.parts)] = state_bytes(
        context, baseline_after, workflow
    )
    apply_transaction(repository, changes)
    write_report(repository, report)
    return report


def status_report(repository: Path) -> dict:
    state = load_state(repository)
    assert state is not None
    context = git_context(repository, state.get("last_synced_git_head"))
    records = []
    for path in managed_paths(repository):
        authoritative = safe_read(repository.joinpath(*path.parts))
        workspace = safe_read(repository / WORKSPACE_DIRECTORY / Path(*path.parts))
        baseline = safe_read(repository.joinpath(*BASELINE_RELATIVE.parts, *path.parts))
        if authoritative == baseline and workspace == baseline:
            category = "unchanged"
        elif authoritative == workspace:
            category = "same-change-both-sides"
        elif authoritative == baseline:
            category = "workspace-changed"
        elif workspace == baseline:
            category = "authoritative-changed"
        else:
            category = "both-changed"
        records.append(
            {
                "path": path.as_posix(),
                "category": category,
                "baseline_sha256": sha256(baseline),
                "authoritative_sha256": sha256(authoritative),
                "workspace_sha256": sha256(workspace),
            }
        )
    return {
        "version": VERSION,
        "operation": "status",
        "result": "success",
        "git": git_report(context),
        "workflow": state["workflow"],
        "protected_ready": (
            state["workflow"].get("state") == "ready"
            and state["workflow"].get("managed_tree_sha256")
            == snapshot_digest(actual_snapshot(repository))
        ),
        "files": records,
    }


def verify_ready(
    repository: Path,
    task_id: str,
    agent: str,
    paths: list[str],
) -> dict:
    if not task_id.strip() or not agent.strip():
        raise SyncError("task ID and agent must be non-empty")
    normalized_paths = [normalized_relative(path).as_posix() for path in paths]
    affected = sorted(path for path in normalized_paths if protected_task_path(path))
    if not affected:
        return {
            "version": VERSION,
            "operation": "verify-ready",
            "result": "ready",
            "task_id": task_id,
            "agent": agent,
            "affected": False,
            "paths": normalized_paths,
            "reason": "unrelated investigation paths do not depend on PI synchronization",
        }

    state = load_state(repository)
    assert state is not None
    workflow = state["workflow"]
    if workflow.get("state") != "ready":
        raise SyncError(
            f"protected task is blocked by synchronization state {workflow.get('state')!r}"
        )
    if workflow.get("task_id") != task_id:
        raise SyncError(
            f"protected task receipt is for {workflow.get('task_id')!r}, not {task_id!r}"
        )
    actual_digest = snapshot_digest(actual_snapshot(repository))
    if workflow.get("managed_tree_sha256") != actual_digest:
        raise SyncError(
            "protected task receipt is stale because managed manuscript, script, or figure "
            "content changed"
        )
    return {
        "version": VERSION,
        "operation": "verify-ready",
        "result": "ready",
        "task_id": task_id,
        "agent": agent,
        "affected": True,
        "paths": affected,
        "prepared_by": workflow.get("prepared_by"),
        "managed_tree_sha256": actual_digest,
        "policy": POLICY_RELATIVE.as_posix(),
    }


def promote_figure(repository: Path, target_text: str, generated_text: str) -> dict:
    state = load_state(repository)
    assert state is not None
    target = normalized_relative(target_text)
    if target.parts[:2] != ("figures", "generated") or len(target.parts) < 3:
        raise SyncError("automated figure targets must be below figures/generated/")
    generated = (repository / generated_text).resolve()
    generated_root = repository.joinpath(*GENERATED_RELATIVE.parts).resolve()
    try:
        generated.relative_to(generated_root)
    except ValueError as error:
        raise SyncError(f"generated source must be below {GENERATED_RELATIVE}") from error
    generated_content = safe_read(generated)
    if generated_content is None:
        raise SyncError(f"generated source does not exist: {generated}")

    target_path = repository / WORKSPACE_DIRECTORY / Path(*target.parts)
    baseline_path = repository.joinpath(*BASELINE_RELATIVE.parts, *target.parts)
    current = safe_read(target_path)
    baseline = safe_read(baseline_path)
    if current != baseline:
        raise SyncConflict(
            {
                "version": VERSION,
                "operation": "promote-figure",
                "result": "conflict",
                "git": git_report(git_context(repository, state.get("last_synced_git_head"))),
                "changes": [],
                "conflicts": [
                    {
                        "path": target.as_posix(),
                        "reason": "workspace figure differs from baseline; manual edit protected",
                        "baseline_sha256": sha256(baseline),
                        "workspace_sha256": sha256(current),
                        "generated_sha256": sha256(generated_content),
                    }
                ],
            }
        )
    atomic_write(target_path, generated_content)
    report = {
        "version": VERSION,
        "operation": "promote-figure",
        "result": "success",
        "git": git_report(git_context(repository, state.get("last_synced_git_head"))),
        "changes": [{"path": target.as_posix(), "action": "promoted-staged-figure"}],
        "conflicts": [],
    }
    write_report(repository, report)
    return report


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--repository", type=Path, default=Path.cwd())
    subparsers = result.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init", help="create pre-build and its synchronization baseline")
    subparsers.add_parser("import", help="import PI edits before team work")
    pre_task = subparsers.add_parser(
        "pre-task", help="synchronize and issue a task-scoped protected-content receipt"
    )
    pre_task.add_argument("--task-id", required=True)
    pre_task.add_argument("--agent", required=True)
    refresh = subparsers.add_parser(
        "refresh", help="refresh pre-build after an accepted revision"
    )
    refresh.add_argument("--acceptance-file", type=Path)
    subparsers.add_parser("status", help="show Git context and three-way file states")
    verify = subparsers.add_parser(
        "verify-ready", help="verify whether target paths may proceed for a task"
    )
    verify.add_argument("--task-id", required=True)
    verify.add_argument("--agent", required=True)
    verify.add_argument("--path", action="append", dest="paths", required=True)
    promote = subparsers.add_parser(
        "promote-figure", help="promote a staged automated figure without overwriting manual edits"
    )
    promote.add_argument("target", help="target below pre-build/figures/generated/")
    promote.add_argument("generated", help="staged source below pre-build/.pi-sync/generated/")
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        repository = repository_root(arguments.repository)
        if arguments.command == "init":
            report = initialize(repository)
        elif arguments.command == "import":
            report = synchronize(repository, "import")
        elif arguments.command == "pre-task":
            report = synchronize(
                repository,
                "import",
                task_id=arguments.task_id,
                prepared_by=arguments.agent,
            )
        elif arguments.command == "refresh":
            report = synchronize(
                repository,
                "refresh",
                acceptance_file=arguments.acceptance_file,
            )
        elif arguments.command == "status":
            report = status_report(repository)
        elif arguments.command == "verify-ready":
            report = verify_ready(
                repository,
                arguments.task_id,
                arguments.agent,
                arguments.paths,
            )
        else:
            report = promote_figure(repository, arguments.target, arguments.generated)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except SyncConflict as error:
        write_report(repository_root(arguments.repository), error.report)
        print(json.dumps(error.report, indent=2, sort_keys=True), file=sys.stderr)
        print("PI synchronization stopped: resolve every reported conflict before retrying", file=sys.stderr)
        return 3
    except SyncError as error:
        print(f"PI synchronization error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
