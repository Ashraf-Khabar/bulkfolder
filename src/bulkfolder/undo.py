from __future__ import annotations
import json
from pathlib import Path
from .journal import journal_path_for

def undo_last(root: Path, *, max_ops: int | None = None) -> int:
    root = root.expanduser().resolve()
    jpath = journal_path_for(root)
    if not jpath.exists():
        return 0

    lines = jpath.read_text(encoding="utf-8").splitlines()
    if not lines:
        return 0

    ops = [json.loads(line) for line in lines if line.strip()]
    if max_ops is not None:
        ops = ops[-max_ops:]

    undone = 0
    for op in reversed(ops):
        src = Path(op["src"])
        dst = Path(op["dst"])
        if dst.exists():
            src.parent.mkdir(parents=True, exist_ok=True)
            dst.replace(src)
            undone += 1

    if max_ops is None:
        jpath.write_text("", encoding="utf-8")
    else:
        remaining = lines[:-max_ops]
        jpath.write_text("\n".join(remaining) + ("\n" if remaining else ""), encoding="utf-8")

    return undone
