from __future__ import annotations
import json
import os
import ctypes
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
    
    file_exists = jpath.exists()
    
    with jpath.open("a", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e.__dict__, ensure_ascii=False) + "\n")
    
    # Rendre le fichier caché sous Windows lors de la création
    if not file_exists and os.name == 'nt':
        try:
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(str(jpath), FILE_ATTRIBUTE_HIDDEN)
        except Exception:
            pass

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()