from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from ..scanner import scan_folder
from ..rules import ReplaceTextRule, MoveByExtensionRule
from ..planner import build_plan
from ..executor import apply_plan as exec_apply_plan
from ..undo import undo_last as exec_undo_last
from ..duplicates import find_duplicates
from ..config import save_settings

DEFAULT_MAPPING = {
    "jpg": "Images", "jpeg": "Images", "png": "Images", "gif": "Images", "webp": "Images",
    "pdf": "PDFs", "doc": "Docs", "docx": "Docs", "txt": "Docs", "md": "Docs",
    "zip": "Archives", "rar": "Archives", "7z": "Archives",
    "mp3": "Audio", "wav": "Audio", "mp4": "Video", "mov": "Video",
}

# ---------- Organizer actions ----------

def choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if not path: return
    app.ui_state.root = Path(path)
    app.organizer_panel.set_folder(str(app.ui_state.root))
    app.set_status("Folder selected.")
    app.log(f"Selected folder: {app.ui_state.root}", level="SUCCESS")
    app.organizer_panel.set_undo_enabled(True)
    if getattr(app, "settings", None) and app.settings.autoscan_on_folder_select:
        scan_and_plan(app)

def toggle_subfolders(app, enabled: bool) -> None:
    app.ui_state.include_subfolders = enabled

def toggle_move_by_ext(app, enabled: bool) -> None:
    app.ui_state.move_by_ext = enabled

def scan_and_plan(app) -> None:
    if not app.ui_state.root:
        messagebox.showwarning("BulkFolder", "Please choose a folder first.")
        return
    app.ui_state.find_text = app.organizer_panel.get_find_text().strip()
    app.ui_state.replace_text = app.organizer_panel.get_replace_text().strip()
    app.set_status("Scanning...")
    
    scanned = scan_folder(app.ui_state.root, include_subfolders=app.ui_state.include_subfolders)
    app.last_scan = scanned

    replace_rule = ReplaceTextRule(app.ui_state.find_text, app.ui_state.replace_text) if app.ui_state.find_text else None
    move_rule = MoveByExtensionRule(DEFAULT_MAPPING) if app.ui_state.move_by_ext else None
    plan = build_plan(app.ui_state.root, scanned, replace_rule=replace_rule, move_rule=move_rule)
    app.last_plan = plan

    files_count = sum(1 for x in scanned if x.is_file)
    planned = sum(1 for it in plan.items if it.action.value != "skip")
    conflicts = sum(1 for it in plan.items if it.conflict)
    total_size = sum(x.size for x in scanned if x.is_file)

    app.cards_view.set_values(str(files_count), str(planned), str(conflicts), app.human_bytes(total_size))
    app.preview_view.render(plan)
    app.dashboard_view.render(scanned, mapping=DEFAULT_MAPPING)
    app.organizer_panel.set_apply_enabled((not plan.has_conflicts) and planned > 0)
    app.organizer_panel.set_undo_enabled(True)
    app.tabs.set("Preview")

def apply_plan(app) -> None:
    if not app.last_plan or sum(1 for it in app.last_plan.items if it.action.value != "skip") == 0: return
    if app.last_plan.has_conflicts:
        messagebox.showerror("BulkFolder", "Plan has conflicts.")
        return
    if messagebox.askyesno("BulkFolder", "Apply changes?"):
        try:
            n = exec_apply_plan(app.last_plan, allow_conflicts=False)
            app.set_status("Applied.")
            scan_and_plan(app)
        except Exception as e:
            messagebox.showerror("BulkFolder", f"Apply failed:\n{e}")

def undo_last_ops(app) -> None:
    if not app.ui_state.root: return
    if messagebox.askyesno("BulkFolder", "Undo the last applied operations?"):
        try:
            n = exec_undo_last(app.ui_state.root)
            scan_and_plan(app)
        except Exception as e:
            messagebox.showerror("BulkFolder", f"Undo failed:\n{e}")

def find_duplicates_action(app) -> None:
    if not app.ui_state.root: return
    min_kb = int(app.settings.duplicate_min_size_kb) if getattr(app, "settings", None) else 1
    scanned = app.last_scan or scan_folder(app.ui_state.root, include_subfolders=app.ui_state.include_subfolders)
    app.last_scan = scanned
    groups = find_duplicates(scanned, min_size_bytes=min_kb * 1024)
    ui_groups = [[str(p) for p in grp] for grp in groups]
    app.duplicates_view.render(ui_groups)
    app.tabs.set("Duplicates")


# ---------- Folder Flattener actions ----------

def flattener_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.flattener_root = Path(path)
        app.flattener_page.set_folder(str(path))
        app.flattener_page.clear_preview()
        app.flattener_plan = []

def flattener_preview(app) -> None:
    root = app.ui_state.flattener_root
    if not root: return
    scanned = scan_folder(root, include_subfolders=True)
    app.flattener_plan = []
    preview_list = []
    taken_names = set(p.path.name for p in scanned if p.is_file and p.path.parent == root)

    for item in scanned:
        if item.is_file and item.path.parent != root:
            new_path = root / item.path.name
            counter = 1
            while new_path.name in taken_names:
                new_path = root / f"{item.path.stem}_{counter}{item.path.suffix}"
                counter += 1
            taken_names.add(new_path.name)
            app.flattener_plan.append((item.path, new_path))
            preview_list.append((str(item.path.relative_to(root)), new_path.name))

    app.flattener_page.render_preview(preview_list)

def flattener_apply(app) -> None:
    plan = getattr(app, "flattener_plan", [])
    if not plan: return
    if messagebox.askyesno("Folder Flattener", f"Extract {len(plan)} files?"):
        for old_path, new_path in plan:
            try: old_path.rename(new_path)
            except Exception: pass
        if app.flattener_page.switch_delete.get():
            root = app.ui_state.flattener_root
            dirs = sorted([d for d in root.rglob('*') if d.is_dir()], key=lambda x: len(x.parts), reverse=True)
            for d in dirs:
                try:
                    if not any(d.iterdir()): d.rmdir()
                except Exception: pass
        app.flattener_page.clear_preview()
        app.flattener_plan = []


# ---------- Large Files actions ----------

def large_files_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.large_files_root = Path(path)
        app.large_files_page.set_folder(str(path))
        app.large_files_scan = None
        app.large_files_page.render_files([])

def large_files_refresh(app, min_mb: float) -> None:
    root = app.ui_state.large_files_root
    if not root: return
    if getattr(app, "large_files_scan", None) is None:
        app.large_files_scan = scan_folder(root, include_subfolders=True)
    min_bytes = min_mb * 1024 * 1024
    large_files = sorted([(i.path, i.size) for i in app.large_files_scan if i.is_file and i.size >= min_bytes], key=lambda x: x[1], reverse=True)
    app.large_files_page.render_files(large_files)

def large_files_delete_selected(app, paths: list[Path]) -> None:
    if not paths: return
    if messagebox.askyesno("Delete", f"Permanently delete {len(paths)} selected file(s)?\nThis action cannot be undone."):
        deleted = 0
        for path in paths:
            try:
                path.unlink()
                deleted += 1
                if getattr(app, "large_files_scan", None):
                    app.large_files_scan = [i for i in app.large_files_scan if i.path != path]
            except Exception as e:
                app.log(f"Error deleting {path.name}: {e}", level="ERROR")
        app.log(f"Deleted {deleted} files.", level="WARN")
        large_files_refresh(app, float(app.large_files_page.min_mb_var.get() or 0))


# ---------- Advanced Renamer actions ----------

def renamer_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.renamer_root = Path(path)
        app.renamer_page.set_folder(str(path))
        app.renamer_page.clear_preview()
        app.renamer_plan = []

def renamer_preview(app) -> None:
    root = app.ui_state.renamer_root
    if not root: return
    prefix = app.renamer_page.entry_prefix.get().strip()
    suffix = app.renamer_page.entry_suffix.get().strip()
    add_num = app.renamer_page.switch_num.get()

    if not prefix and not suffix and not add_num: return

    scanned_files = sorted([item for item in scan_folder(root, include_subfolders=False) if item.is_file], key=lambda x: x.path.name)
    app.renamer_plan = []
    preview_list = []
    count = 1

    for item in scanned_files:
        old_path = item.path
        new_name = old_path.stem
        if prefix: new_name = f"{prefix}{new_name}"
        if suffix: new_name = f"{new_name}{suffix}"
        if add_num:
            new_name = f"{new_name}_{count:03d}"
            count += 1
        new_full_name = f"{new_name}{old_path.suffix}"

        if new_full_name != old_path.name:
            new_path = old_path.parent / new_full_name
            preview_list.append((old_path.name, new_full_name))
            app.renamer_plan.append((old_path, new_path))
    app.renamer_page.render_preview(preview_list)

def renamer_apply(app) -> None:
    plan = getattr(app, "renamer_plan", [])
    if not plan: return
    if messagebox.askyesno("Mass Renamer", f"Apply new names to {len(plan)} files?"):
        for old_path, new_path in plan:
            try:
                if not new_path.exists(): old_path.rename(new_path)
            except Exception: pass
        app.renamer_page.clear_preview()
        app.renamer_plan = []


# ---------- Date Organizer actions ----------

def dateorg_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.dateorg_root = Path(path)
        app.dateorg_page.set_folder(str(path))
        app.dateorg_page.clear_preview()
        app.dateorg_plan = []

def dateorg_preview(app) -> None:
    root = app.ui_state.dateorg_root
    if not root:
        messagebox.showwarning("Date Organizer", "Please choose a folder first.")
        return

    mode = app.dateorg_page.mode_var.get()
    scanned_files = [item for item in scan_folder(root, include_subfolders=False) if item.is_file]
    
    app.dateorg_plan = []
    preview_list = []

    for item in scanned_files:
        try:
            mtime = item.path.stat().st_mtime
            dt = datetime.fromtimestamp(mtime)
            
            if "Year/Month/Day" in mode:
                folder_name = os.path.join(dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d"))
            elif "Year/Month" in mode:
                folder_name = os.path.join(dt.strftime("%Y"), dt.strftime("%m"))
            else:
                folder_name = dt.strftime("%Y")
                
            dest_dir = root / folder_name
            new_path = dest_dir / item.path.name
            
            # Handle name collision
            counter = 1
            while new_path.exists() or new_path in [p[1] for p in app.dateorg_plan]:
                new_path = dest_dir / f"{item.path.stem}_{counter}{item.path.suffix}"
                counter += 1

            app.dateorg_plan.append((item.path, new_path))
            preview_list.append((item.path.name, f"{folder_name}/{new_path.name}"))
        except Exception as e:
            app.log(f"Error reading date for {item.path.name}: {e}", level="ERROR")

    app.dateorg_page.render_preview(preview_list)
    app.set_status(f"DateOrg: {len(preview_list)} files to sort.")

def dateorg_apply(app) -> None:
    plan = getattr(app, "dateorg_plan", [])
    if not plan: return

    if messagebox.askyesno("Date Organizer", f"Organize {len(plan)} files by date?"):
        applied = 0
        for old_path, new_path in plan:
            try:
                new_path.parent.mkdir(parents=True, exist_ok=True)
                old_path.rename(new_path)
                applied += 1
            except Exception as e:
                app.log(f"Error moving {old_path.name}: {e}", level="ERROR")
                
        app.log(f"Date organization complete: {applied}/{len(plan)} files moved.", level="SUCCESS")
        app.dateorg_page.clear_preview()
        app.dateorg_plan = []

# ---------- Settings actions ----------

def settings_save(app) -> None:
    new_settings = app.settings_page.read_settings_from_form()
    app.settings = new_settings
    mode = new_settings.appearance_mode
    ctk.set_appearance_mode("system" if mode == "system" else mode)
    save_settings(new_settings)