"""Persistent movement history powering the Unsort feature.

Every Sort appends one session record (original path -> new path for each
moved file) to a JSON file kept *outside* the managed folder, so rescans
or user cleanup cannot delete it. Unsort reverses the most recent session
that has not been undone yet.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .organizer import PlannedMove


def default_history_path() -> Path:
    """Location of the history file, per-OS application data dir."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
        return base / "DownLSort" / "history.json"
    if os.name == "posix":
        return Path.home() / ".config" / "downlsort" / "history.json"
    return Path.home() / ".downlsort" / "history.json"


@dataclass
class SortSession:
    timestamp: str
    moves: list[PlannedMove] = field(default_factory=list)
    undone: bool = False

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "undone": self.undone,
            "moves": [
                {"src": str(m.src), "dst": str(m.dst)} for m in self.moves
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> SortSession:
        return cls(
            timestamp=data.get("timestamp", ""),
            undone=data.get("undone", False),
            moves=[
                PlannedMove(src=Path(m["src"]), dst=Path(m["dst"]))
                for m in data.get("moves", [])
            ],
        )


class HistoryLog:
    """Append-only JSON log of sort sessions."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else default_history_path()
        self.sessions: list[SortSession] = []
        self._load()

    def _load(self) -> None:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return  # Missing or corrupt file: start with empty history.
        if isinstance(raw, list):
            self.sessions = [SortSession.from_dict(s) for s in raw if isinstance(s, dict)]

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps([s.to_dict() for s in self.sessions], indent=2),
            encoding="utf-8",
        )
        tmp.replace(self.path)

    def record(self, moves: list[PlannedMove]) -> SortSession:
        """Append a session for a just-completed Sort and persist it."""
        session = SortSession(
            timestamp=datetime.now(timezone.utc).isoformat(),
            moves=list(moves),
        )
        self.sessions.append(session)
        self._save()
        return session

    def latest_pending(self) -> SortSession | None:
        """Most recent session that has not been undone, or None."""
        for session in reversed(self.sessions):
            if not session.undone and session.moves:
                return session
        return None

    def mark_undone(self, session: SortSession) -> None:
        session.undone = True
        self._save()
