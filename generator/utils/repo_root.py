from __future__ import annotations

from pathlib import Path


def find_repo_root(start_path: Path | None = None) -> Path:
    """
    Locate the repository root by walking upward until a .git directory is found.
    Fail closed if no .git directory exists.
    """
    current = (start_path or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        if (parent / ".git").is_dir():
            return parent
    message = (
        "ERROR: Repository root could not be determined.\n"
        "Reason: No .git directory found during upward traversal."
    )
    raise RuntimeError(message)
