from __future__ import annotations
from pathlib import Path
from collections import Counter
from .domain import FileItem, Plan, PlanItem, ActionType
from .rules import ReplaceTextRule, MoveByExtensionRule

def build_plan(
    root: Path,
    scanned: list[FileItem],
    replace_rule: ReplaceTextRule | None = None,
    move_rule: MoveByExtensionRule | None = None,
) -> Plan:
    root = root.expanduser().resolve()
    plan_items: list[PlanItem] = []

    for item in scanned:
        if not item.is_file:
            continue

        src = item.path
        dst_dir = src.parent
        new_name = src.name

        if replace_rule:
            new_name = replace_rule.apply_name(new_name)

        if move_rule:
            bucket = move_rule.target_subfolder(src)
            dst_dir = root / bucket

        dst = (dst_dir / new_name).resolve()

        if dst == src:
            plan_items.append(PlanItem(src=src, dst=dst, action=ActionType.SKIP, reason="no change"))
            continue

        action = ActionType.RENAME if src.parent == dst.parent else ActionType.MOVE
        plan_items.append(PlanItem(src=src, dst=dst, action=action))

    dst_counts = Counter([p.dst for p in plan_items if p.action != ActionType.SKIP])
    final_items: list[PlanItem] = []
    for p in plan_items:
        conflict = None
        if p.action != ActionType.SKIP:
            if dst_counts[p.dst] > 1:
                conflict = "multiple sources target same destination"
            elif p.dst.exists():
                conflict = "destination already exists"
        final_items.append(PlanItem(src=p.src, dst=p.dst, action=p.action, reason=p.reason, conflict=conflict))

    return Plan(root=root, items=final_items)
