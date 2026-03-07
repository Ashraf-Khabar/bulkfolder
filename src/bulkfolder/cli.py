from __future__ import annotations
import argparse
from pathlib import Path
from .scanner import scan_folder
from .rules import ReplaceTextRule, MoveByExtensionRule
from .planner import build_plan
from .undo import undo_last

DEFAULT_MAPPING = {
    "jpg": "Images", "jpeg": "Images", "png": "Images", "gif": "Images", "webp": "Images",
    "pdf": "PDFs",
    "doc": "Docs", "docx": "Docs", "txt": "Docs", "md": "Docs",
    "zip": "Archives", "rar": "Archives", "7z": "Archives",
    "mp3": "Audio", "wav": "Audio",
    "mp4": "Video", "mov": "Video",
    "py" : "Code", "python" : "Code", "xsls" : "Sheets", "csv" : "Sheets", "exe" : "Programs",
}

def main() -> None:
    p = argparse.ArgumentParser(prog="bulkfolder")
    sub = p.add_subparsers(dest="cmd", required=True)

    plan_p = sub.add_parser("plan")
    plan_p.add_argument("root")
    plan_p.add_argument("--no-subfolders", action="store_true")
    plan_p.add_argument("--find", default="")
    plan_p.add_argument("--replace", default="")
    plan_p.add_argument("--move-by-ext", action="store_true")

    undo_p = sub.add_parser("undo")
    undo_p.add_argument("root")
    undo_p.add_argument("--max-ops", type=int, default=None)

    args = p.parse_args()
    root = Path(args.root)

    if args.cmd == "plan":
        scanned = scan_folder(root, include_subfolders=not args.no_subfolders)
        replace_rule = ReplaceTextRule(args.find, args.replace) if args.find else None
        move_rule = MoveByExtensionRule(DEFAULT_MAPPING) if args.move_by_ext else None
        plan = build_plan(root, scanned, replace_rule=replace_rule, move_rule=move_rule)

        for it in plan.items[:200]:
            flag = "CONFLICT" if it.conflict else it.action.value.upper()
            print(f"{flag}: {it.src} -> {it.dst}" + (f" ({it.conflict})" if it.conflict else ""))

        print(f"\nTotal items: {len(plan.items)} | Conflicts: {sum(1 for i in plan.items if i.conflict)}")
        return

    if args.cmd == "undo":
        n = undo_last(root, max_ops=args.max_ops)
        print(f"Undone: {n}")

if __name__ == "__main__":
    main()
