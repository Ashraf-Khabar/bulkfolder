from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass
class UIState:
    root: Path | None = None
    include_subfolders: bool = True
    find_text: str = ""
    replace_text: str = ""
    move_by_ext: bool = True
    large_files_root: Path | None = None
    renamer_root: Path | None = None
    flattener_root: Path | None = None
    dateorg_root: Path | None = None
    empty_folders_root: Path | None = None