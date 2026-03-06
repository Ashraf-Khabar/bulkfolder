from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from .domain import FileItem


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(
    files: Iterable[FileItem],
    *,
    min_size_bytes: int = 1,
) -> list[list[Path]]:
    """
    Returns groups of duplicate files (same content hash), each group len >= 2.
    Strategy:
      1) group by size (fast)
      2) hash only candidates (slower)
    """

    # 1) group by size
    by_size: dict[int, list[Path]] = {}
    for it in files:
        if not it.is_file:
            continue
        if it.size < min_size_bytes:
            continue
        by_size.setdefault(it.size, []).append(it.path)

    # 2) hash within each size bucket
    dup_groups: list[list[Path]] = []
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue

        by_hash: dict[str, list[Path]] = {}
        for p in paths:
            try:
                digest = _sha256_file(p)
            except OSError:
                # unreadable file (permissions/locked) -> ignore
                continue
            by_hash.setdefault(digest, []).append(p)

        for group in by_hash.values():
            if len(group) >= 2:
                dup_groups.append(group)

    # Sort: biggest file size desc, then group length desc
    def safe_size(p: Path) -> int:
        try:
            return p.stat().st_size
        except OSError:
            return 0

    dup_groups.sort(key=lambda g: (-safe_size(g[0]) if g else 0, -len(g)))
    return dup_groups