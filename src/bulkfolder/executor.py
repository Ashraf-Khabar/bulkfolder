from __future__ import annotations
from pathlib import Path
from .domain import Plan, ActionType
from .journal import JournalEntry, append_entries, journal_path_for, now_iso

def apply_plan(plan: Plan, *, allow_conflicts: bool = False) -> int:
    if plan.has_conflicts and not allow_conflicts:
        raise RuntimeError("Plan has conflicts. Resolve before applying.")

    jpath = journal_path_for(plan.root)
    applied = 0
    entries: list[JournalEntry] = []

    for item in plan.items:
        if item.action == ActionType.SKIP:
            continue

        src, dst = item.src, item.dst
        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.exists() and not allow_conflicts:
            raise FileExistsError(dst)

        src.replace(dst)

        entries.append(JournalEntry(op="move", src=str(src), dst=str(dst), ts=now_iso()))
        applied += 1

    append_entries(jpath, entries)
    return applied
