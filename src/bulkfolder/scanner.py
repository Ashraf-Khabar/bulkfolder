from __future__ import annotations
from pathlib import Path
from .domain import FileItem

def scan_folder(root: Path, include_subfolders: bool = True) -> list[FileItem]:
    root = root.expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(root)
    if not root.is_dir():
        raise NotADirectoryError(root)

    pattern = "**/*" if include_subfolders else "*"
    items: list[FileItem] = []
    for p in root.glob(pattern):
        try:
            st = p.stat()
        except OSError:
            continue
        items.append(
            FileItem(
                path=p,
                is_file=p.is_file(),
                size=getattr(st, "st_size", 0),
                mtime=getattr(st, "st_mtime", 0.0),
            )
        )
    return items
