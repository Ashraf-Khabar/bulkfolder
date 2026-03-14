from __future__ import annotations
from pathlib import Path
from typing import Callable, Optional
from .domain import Plan, ActionType
from .journal import JournalEntry, append_entries, journal_path_for, now_iso

def apply_plan(
    plan: Plan, 
    *, 
    allow_conflicts: bool = False, 
    on_progress: Optional[Callable[[str, str], None]] = None
) -> int:
    """
    Applies the given plan by executing file operations.
    
    Args:
        plan: The Plan object containing items to process.
        allow_conflicts: If True, overwrites existing files.
        on_progress: Optional callback function(message, level) for logging.
    """
    if plan.has_conflicts and not allow_conflicts:
        raise RuntimeError("Plan has conflicts. Resolve before applying.")

    jpath = journal_path_for(plan.root)
    applied = 0
    entries: list[JournalEntry] = []

    for item in plan.items:
        if item.action == ActionType.SKIP:
            continue

        src, dst = item.src, item.dst
        
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)

            if dst.exists() and not allow_conflicts:
                if on_progress:
                    on_progress(f"Conflict: {dst.name} already exists. Skipping.", "WARNING")
                continue

            src.replace(dst)
            
            # Logging the success of the operation
            if on_progress:
                on_progress(f"Moved: {src.name} -> {dst.parent.name}/", "SUCCESS")

            entries.append(JournalEntry(op="move", src=str(src), dst=str(dst), ts=now_iso()))
            applied += 1
            
        except Exception as e:
            if on_progress:
                on_progress(f"Error processing {src.name}: {str(e)}", "ERROR")

    append_entries(jpath, entries)
    
    if on_progress:
        on_progress(f"Task completed. {applied} operations applied.", "INFO")
        
    return applied