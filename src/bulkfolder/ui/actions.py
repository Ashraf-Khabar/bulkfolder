from __future__ import annotations
import os
import sys
import shutil
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk

from ..scanner import scan_folder
from ..rules import MoveByExtensionRule
from ..planner import build_plan
from ..executor import apply_plan as exec_apply_plan
from ..undo import undo_last as exec_undo_last
from ..config import save_settings
from ..pdf_converter import convert_images_to_pdf
from ..chunker import plan_chunks, apply_chunks

DEFAULT_MAPPING = {
    "jpg": "Images", "jpeg": "Images", "png": "Images", "gif": "Images", "webp": "Images", 
    "pdf": "PDFs", "doc": "Docs", "docx": "Docs", "txt": "Docs", "md": "Docs", 
    "zip": "Archives", "rar": "Archives", "7z": "Archives",
    "mp3": "Audio", "wav": "Audio", "mp4": "Video", "mov": "Video",
    "py": "Code", "js": "Code", "html": "Code", "exe": "Executables"
}

def _ask_confirm(app, title: str, message: str) -> bool:
    if not getattr(app.settings, "ask_confirmations", True):
        return True 
    return messagebox.askyesno(title, message)

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
    root = getattr(app.ui_state, "root", None)
    if not root:
        messagebox.showwarning("BulkFolder", "Please choose a folder first.")
        return
    
    app.set_status("Scanning...")
    scanned = scan_folder(app.ui_state.root, include_subfolders=app.ui_state.include_subfolders)
    app.last_scan = scanned

    # Règle de remplacement de texte supprimée ici
    move_rule = MoveByExtensionRule(DEFAULT_MAPPING) if app.ui_state.move_by_ext else None
    plan = build_plan(app.ui_state.root, scanned, replace_rule=None, move_rule=move_rule)
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
    if _ask_confirm(app, "BulkFolder", "Apply changes?"):
        try:
            exec_apply_plan(app.last_plan, allow_conflicts=False)
            app.set_status("Applied.")
            scan_and_plan(app)
        except Exception as e:
            messagebox.showerror("BulkFolder", f"Apply failed:\n{e}")

def undo_last_ops(app) -> None:
    root = getattr(app.ui_state, "root", None)
    if not root: return
    if _ask_confirm(app, "BulkFolder", "Undo the last applied operations?"):
        try:
            exec_undo_last(app.ui_state.root)
            scan_and_plan(app)
        except Exception as e:
            messagebox.showerror("BulkFolder", f"Undo failed:\n{e}")

# Fonctions de chunker, flattener, etc. inchangées mais on ajuste Large Files

def large_files_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.large_files_root = Path(path)
        app.large_files_page.set_folder(str(path))
        app.large_files_scan = None
        app.large_files_page.render_files([])

def large_files_refresh(app, min_mb: float) -> None:
    root = getattr(app.ui_state, "large_files_root", None)
    if not root:
        messagebox.showwarning("Large Files", "Please choose a folder first.")
        return
    
    app.set_status("Analyzing large files...")
    if getattr(app, "large_files_scan", None) is None:
        app.large_files_scan = scan_folder(root, include_subfolders=True)
    
    min_bytes = min_mb * 1024 * 1024
    large_files = sorted([(i.path, i.size) for i in app.large_files_scan if i.is_file and i.size >= min_bytes], key=lambda x: x[1], reverse=True)
    app.large_files_page.render_files(large_files)
    
    # Ajout d'un log coloré pour l'analyse
    app.log(f"Analyzed {len(large_files)} files larger than {min_mb} MB.", level="INFO")

# La fonction large_files_delete_selected est supprimée car lecture seule