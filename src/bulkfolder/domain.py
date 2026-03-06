from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Optional

@dataclass(frozen=True)
class FileItem:
    path: Path
    is_file: bool
    size: int
    mtime: float

class ActionType(str, Enum):
    MOVE = "move"
    RENAME = "rename"
    SKIP = "skip"

@dataclass(frozen=True)
class PlanItem:
    src: Path
    dst: Path
    action: ActionType
    reason: str = ""
    conflict: Optional[str] = None

@dataclass(frozen=True)
class Plan:
    root: Path
    items: list[PlanItem]

    @property
    def has_conflicts(self) -> bool:
        return any(i.conflict for i in self.items)
