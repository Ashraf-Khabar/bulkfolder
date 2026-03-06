from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

import customtkinter as ctk

from ..scanner import scan_folder
from ..rules import ReplaceTextRule, MoveByExtensionRule
from ..planner import build_plan
from ..executor import apply_plan as exec_apply_plan
from ..undo import undo_last as exec_undo_last
from ..duplicates import find_duplicates

from ..presets import Preset, upsert_preset, delete_preset, get_preset
from ..config import save_settings


DEFAULT_MAPPING = {
    "jpg": "Images",
    "jpeg": "Images",
    "png": "Images",
    "gif": "Images",
    "webp": "Images",
    "pdf": "PDFs",
    "doc": "Docs",
    "docx": "Docs",
    "txt": "Docs",
    "md": "Docs",
    "zip": "Archives",
    "rar": "Archives",
    "7z": "Archives",
    "mp3": "Audio",
    "wav": "Audio",
    "mp4": "Video",
    "mov": "Video",
}


# ---------- Organizer actions ----------

def choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if not path:
        return

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
        messagebox.showwarning("BulkFolder", "Choose a folder first.")
        return

    app.ui_state.find_text = app.organizer_panel.get_find_text().strip()
    app.ui_state.replace_text = app.organizer_panel.get_replace_text().strip()

    app.set_status("Scanning…")
    app.log("Scanning files…", level="INFO")

    scanned = scan_folder(app.ui_state.root, include_subfolders=app.ui_state.include_subfolders)
    app.last_scan = scanned

    replace_rule = None
    if app.ui_state.find_text:
        replace_rule = ReplaceTextRule(app.ui_state.find_text, app.ui_state.replace_text)

    move_rule = MoveByExtensionRule(DEFAULT_MAPPING) if app.ui_state.move_by_ext else None

    plan = build_plan(app.ui_state.root, scanned, replace_rule=replace_rule, move_rule=move_rule)
    app.last_plan = plan

    files_count = sum(1 for x in scanned if x.is_file)
    planned = sum(1 for it in plan.items if it.action.value != "skip")
    conflicts = sum(1 for it in plan.items if it.conflict)
    total_size = sum(x.size for x in scanned if x.is_file)

    app.cards_view.set_values(
        scanned=str(files_count),
        planned=str(planned),
        conflicts=str(conflicts),
        total_size=app.human_bytes(total_size),
    )

    app.preview_view.render(plan)
    app.dashboard_view.render(scanned, mapping=DEFAULT_MAPPING)

    app.organizer_panel.set_apply_enabled((not plan.has_conflicts) and planned > 0)
    app.organizer_panel.set_undo_enabled(True)

    app.set_status("Preview ready.")
    app.tabs.set("Preview")

    if conflicts:
        app.log(f"Scan done. files={files_count}, planned={planned}, conflicts={conflicts}", level="WARN")
    else:
        app.log(f"Scan done. files={files_count}, planned={planned}, conflicts={conflicts}", level="SUCCESS")


def apply_plan(app) -> None:
    if not app.last_plan:
        messagebox.showwarning("BulkFolder", "Nothing to apply. Run Scan & Preview first.")
        return

    plan = app.last_plan
    planned = sum(1 for it in plan.items if it.action.value != "skip")

    if planned == 0:
        messagebox.showinfo("BulkFolder", "No changes to apply.")
        return

    if plan.has_conflicts:
        messagebox.showerror("BulkFolder", "Plan has conflicts. Resolve them before applying.")
        return

    confirm = messagebox.askyesno("BulkFolder", f"This will apply {planned} changes.\n\nAre you sure?")
    if not confirm:
        return

    try:
        app.set_status("Applying…")
        app.log(f"Applying {planned} operations…", level="INFO")

        n = exec_apply_plan(plan, allow_conflicts=False)

        app.log(f"Applied: {n}", level="SUCCESS")
        app.set_status("Applied.")
        app.organizer_panel.set_undo_enabled(True)

        scan_and_plan(app)

    except Exception as e:
        app.set_status("Error.")
        app.log(f"Apply failed: {e}", level="ERROR")
        messagebox.showerror("BulkFolder", f"Apply failed:\n{e}")


def undo_last_ops(app) -> None:
    if not app.ui_state.root:
        messagebox.showwarning("BulkFolder", "Choose a folder first.")
        return

    confirm = messagebox.askyesno("BulkFolder", "Undo the last applied operations?")
    if not confirm:
        return

    try:
        app.set_status("Undoing…")
        app.log("Undoing last operations…", level="INFO")

        n = exec_undo_last(app.ui_state.root)

        app.log(f"Undone: {n}", level="SUCCESS")
        app.set_status("Undo done.")

        scan_and_plan(app)

    except Exception as e:
        app.set_status("Error.")
        app.log(f"Undo failed: {e}", level="ERROR")
        messagebox.showerror("BulkFolder", f"Undo failed:\n{e}")


def find_duplicates_action(app) -> None:
    if not app.ui_state.root:
        messagebox.showwarning("BulkFolder", "Choose a folder first.")
        return

    min_kb = 1
    if getattr(app, "settings", None):
        min_kb = int(app.settings.duplicate_min_size_kb)

    app.set_status("Finding duplicates…")
    app.log(f"Finding duplicates (SHA-256)… min={min_kb}KB", level="INFO")

    scanned = app.last_scan
    if scanned is None:
        scanned = scan_folder(app.ui_state.root, include_subfolders=app.ui_state.include_subfolders)
        app.last_scan = scanned

    groups = find_duplicates(scanned, min_size_bytes=min_kb * 1024)
    ui_groups = [[str(p) for p in grp] for grp in groups]

    app.duplicates_view.render(ui_groups)
    app.tabs.set("Duplicates")
    app.set_status(f"Duplicates: {len(ui_groups)} groups")

    if ui_groups:
        app.log(f"Duplicates found: {len(ui_groups)} groups", level="SUCCESS")
    else:
        app.log("No duplicates found.", level="DEBUG")


# ---------- Presets actions ----------

def presets_refresh(app) -> None:
    app.presets_page.refresh()
    app.set_status("Presets refreshed.")
    app.log("Presets refreshed.", level="DEBUG")


def presets_apply_selected(app) -> None:
    name = app.presets_page.get_selected_name()
    if not name:
        messagebox.showwarning("Presets", "Select a preset first.")
        return

    p = get_preset(name)
    if not p:
        messagebox.showerror("Presets", "Preset not found.")
        return

    app.ui_state.include_subfolders = p.include_subfolders
    app.ui_state.move_by_ext = p.move_by_extension
    app.ui_state.find_text = p.find_text
    app.ui_state.replace_text = p.replace_text

    app.organizer_panel.set_include_subfolders(p.include_subfolders)
    app.organizer_panel.set_move_by_extension(p.move_by_extension)
    app.organizer_panel.set_find_replace(p.find_text, p.replace_text)

    app.set_status(f"Preset applied: {p.name}")
    app.log(f"Preset applied: {p.name}", level="SUCCESS")

    app.switch_page("Organizer")


def presets_save_current(app) -> None:
    name = simpledialog.askstring("Save preset", "Preset name:")
    if not name:
        return
    name = name.strip()
    if not name:
        return

    preset = Preset(
        name=name,
        include_subfolders=bool(app.ui_state.include_subfolders),
        move_by_extension=bool(app.ui_state.move_by_ext),
        find_text=app.organizer_panel.get_find_text().strip(),
        replace_text=app.organizer_panel.get_replace_text().strip(),
    )
    upsert_preset(preset)
    app.presets_page.refresh()
    app.set_status(f"Preset saved: {name}")
    app.log(f"Preset saved: {name}", level="SUCCESS")


def presets_delete_selected(app) -> None:
    name = app.presets_page.get_selected_name()
    if not name:
        messagebox.showwarning("Presets", "Select a preset first.")
        return

    ok = messagebox.askyesno("Delete preset", f"Delete preset '{name}'?")
    if not ok:
        return

    deleted = delete_preset(name)
    app.presets_page.refresh()

    if deleted:
        app.set_status(f"Preset deleted: {name}")
        app.log(f"Preset deleted: {name}", level="WARN")
    else:
        app.set_status("Nothing deleted.")
        app.log("Preset delete: not found.", level="DEBUG")


# ---------- Settings actions ----------

def settings_save(app) -> None:
    new_settings = app.settings_page.read_settings_from_form()
    app.settings = new_settings

    mode = new_settings.appearance_mode
    if mode == "system":
        ctk.set_appearance_mode("system")
    else:
        ctk.set_appearance_mode(mode)

    save_settings(new_settings)

    app.set_status("Settings saved.")
    app.log("Settings saved.", level="SUCCESS")