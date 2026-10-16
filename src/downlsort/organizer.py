"""Plan and execute file moves for Sort and Unsort."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .scanner import FileItem


@dataclass(frozen=True)
class PlannedMove:
    """A single intended move: *src* -> *dst*."""

    src: Path
    dst: Path


@dataclass
class MoveResult:
    """Outcome of executing a batch of moves."""

    moved: list[PlannedMove] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def unique_destination(dst: Path) -> Path:
    """Return *dst* or the first free "name (n).ext" variant of it.

    Guarantees the organizer never overwrites an existing file.
    """
    if not dst.exists():
        return dst
    stem, suffix = dst.stem, dst.suffix
    counter = 1
    while True:
        candidate = dst.with_name(f"{stem} ({counter}){suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def plan_moves(folder: str | Path, items: list[FileItem]) -> list[PlannedMove]:
    """Map each item to <folder>/<Category>/<filename>."""
    folder = Path(folder)
    return [
        PlannedMove(src=item.path, dst=folder / item.category / item.name)
        for item in items
    ]


def execute_moves(moves: list[PlannedMove]) -> MoveResult:
    """Perform *moves*, creating destination folders as needed.

    Each file is moved in its own try/except so one failure (file in
    use, permission denied, ...) is recorded while the rest continue.
    Name conflicts are resolved with :func:`unique_destination` and the
    *actual* destination is what gets recorded (needed for exact undo).
    """
    result = MoveResult()
    for move in moves:
        try:
            dst = unique_destination(move.dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(move.src), str(dst))
            result.moved.append(PlannedMove(src=move.src, dst=dst))
        except OSError as exc:
            result.errors.append(f"{move.src.name}: {exc.strerror or exc}")
    return result


def restore_moves(moves: list[PlannedMove]) -> MoveResult:
    """Reverse previously executed moves (used by Unsort).

    Each entry (original_src, sorted_dst) becomes a move
    sorted_dst -> original_src. Files that no longer exist at their
    sorted location are reported as errors, not crashes.
    """
    reversed_moves = [
        PlannedMove(src=move.dst, dst=move.src) for move in moves
    ]
    result = MoveResult()
    for move in reversed_moves:
        if not move.src.exists():
            result.errors.append(
                f"{move.src.name}: file no longer at sorted location, skipped"
            )
            continue
        try:
            dst = unique_destination(move.dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(move.src), str(dst))
            result.moved.append(PlannedMove(src=move.src, dst=dst))
        except OSError as exc:
            result.errors.append(f"{move.src.name}: {exc.strerror or exc}")
    return result


def remove_empty_dirs(folder: str | Path, names: list[str]) -> None:
    """Remove *names* inside *folder* when they are empty directories."""
    folder = Path(folder)
    for name in names:
        target = folder / name
        try:
            if target.is_dir() and not any(target.iterdir()):
                target.rmdir()
        except OSError:
            continue
