from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
from typing import Iterable

@dataclass(frozen=True)
class JournalEntry:
    op: str
    src: str
    dst: str
    ts: str

def journal_path_for(root: Path) -> Path:
    return root / ".bulkfolder_journal.jsonl"

def append_entries(jpath: Path, entries: Iterable[JournalEntry]) -> None:
    jpath.parent.mkdir(parents=True, exist_ok=True)
    with jpath.open("a", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e.__dict__, ensure_ascii=False) + "\n")

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
