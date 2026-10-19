"""Safe output helpers for automated figure generation."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


class UnsafeFigurePath(ValueError):
    """Raised when automated output is outside figures/generated."""


def generated_figure_path(repository: Path | str, relative_name: Path | str) -> Path:
    """Return a safe generated-figure path below *repository*.

    Absolute paths, traversal, the directory itself, and paths escaping through
    a symlink are rejected.
    """

    repository = Path(repository).resolve()
    generated = (repository / "figures" / "generated").resolve()
    relative_name = Path(relative_name)
    if relative_name.is_absolute():
        raise UnsafeFigurePath("generated figure names must be relative")

    candidate = (generated / relative_name).resolve()
    try:
        candidate.relative_to(generated)
    except ValueError as error:
        raise UnsafeFigurePath(
            "automated figures may only be written below figures/generated"
        ) from error
    if candidate == generated:
        raise UnsafeFigurePath("a generated figure filename is required")
    return candidate


def write_generated_bytes(
    repository: Path | str, relative_name: Path | str, content: bytes
) -> Path:
    """Atomically write an automated figure without touching edited assets."""

    destination = generated_figure_path(repository, relative_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=destination.parent, prefix=f".{destination.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return destination
