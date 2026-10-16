"""Scan a folder and describe the files it contains."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .categories import categorize

#: Folder shown on first launch.
DEFAULT_FOLDER = Path.home() / "Downloads"


@dataclass(frozen=True)
class FileItem:
    """A single top-level file found by :func:`scan_folder`."""

    path: Path
    size: int
    category: str

    @property
    def name(self) -> str:
        return self.path.name


def format_size(num_bytes: int) -> str:
    """Format a byte count as a human-readable string, e.g. "2.4 MB"."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(size)} B"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"  # pragma: no cover - unreachable


def scan_folder(folder: str | Path) -> list[FileItem]:
    """List top-level files in *folder*, sorted by name.

    Subdirectories (including the category folders created by sorting)
    are ignored. Files that cannot be stat'ed are skipped so one bad
    entry never breaks a scan.
    """
    folder = Path(folder)
    items: list[FileItem] = []
    try:
        entries = list(folder.iterdir())
    except OSError:
        return []
    for entry in entries:
        if not entry.is_file():
            continue
        try:
            size = entry.stat().st_size
        except OSError:
            continue
        items.append(
            FileItem(path=entry, size=size, category=categorize(entry.name))
        )
    items.sort(key=lambda item: item.name.lower())
    return items
