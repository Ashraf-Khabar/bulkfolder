from __future__ import annotations

import os
import sys
import shutil
import webbrowser
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

# --- Core Logic Imports ---
from ..scanner import scan_folder
from ..rules import ReplaceTextRule, MoveByExtensionRule
from ..planner import build_plan
from ..executor import apply_plan as exec_apply_plan
from ..undo import undo_last as exec_undo_last
from ..duplicates import find_duplicates
from ..config import save_settings
from ..pdf_converter import convert_images_to_pdf
from ..chunker import plan_chunks, apply_chunks

# --- Global Configuration ---
DEFAULT_MAPPING = {
    "jpg": "Images", "jpeg": "Images", "png": "Images", "gif": "Images", "webp": "Images", 
    "bmp": "Images", "tiff": "Images", "svg": "Images", "ico": "Images", "raw": "Images", "heic": "Images",
    "pdf": "PDFs", "doc": "Docs", "docx": "Docs", "txt": "Docs", "md": "Docs", 
    "rtf": "Docs", "odt": "Docs",
    "xls": "Spreadsheets", "xlsx": "Spreadsheets", "csv": "Spreadsheets", "ods": "Spreadsheets",
    "ppt": "Presentations", "pptx": "Presentations", "odp": "Presentations", "key": "Presentations",
    "zip": "Archives", "rar": "Archives", "7z": "Archives", "tar": "Archives", "gz": "Archives", 
    "bz2": "Archives", "xz": "Archives", "iso": "Archives",
    "mp3": "Audio", "wav": "Audio", "flac": "Audio", "aac": "Audio", "ogg": "Audio", 
    "wma": "Audio", "m4a": "Audio",
    "mp4": "Video", "mov": "Video", "avi": "Video", "mkv": "Video", "wmv": "Video", 
    "flv": "Video", "webm": "Video", "m4v": "Video",
    "py": "Code", "js": "Code", "html": "Code", "css": "Code", "java": "Code", 
    "c": "Code", "cpp": "Code", "cs": "Code", "php": "Code", "rb": "Code", 
    "go": "Code", "rs": "Code", "ts": "Code", "swift": "Code", "kt": "Code",
    "sh": "Code", "bat": "Code", "ps1": "Code",
    "json": "Data", "xml": "Data", "yaml": "Data", "yml": "Data", "sql": "Data", 
    "db": "Data", "sqlite": "Data", "ini": "Data", "env": "Data", "toml": "Data",
    "psd": "Design", "ai": "Design", "xd": "Design", "fig": "Design", "sketch": "Design", 
    "indd": "Design", "blend": "Design", "fbx": "Design", "obj": "Design",
    "exe": "Executables", "msi": "Executables", "apk": "Executables", "app": "Executables", 
    "dmg": "Executables", "deb": "Executables", "rpm": "Executables",
    "ttf": "Fonts", "otf": "Fonts", "woff": "Fonts", "woff2": "Fonts",
    "epub": "Books", "mobi": "Books", "azw3": "Books"
}

def _ask_confirm(app, title: str, message: str) -> bool:
    """Helper for user confirmation."""
    if not getattr(app.settings, "ask_confirmations", True):
        return True 
    return messagebox.askyesno(title, message)


# ==========================================
# ORGANIZER ACTIONS (Main Tab)
# ==========================================

def choose_folder(app) -> None:
    """Select working directory."""
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

def scan_and_plan(app) -> None:
    """Scan folder and build virtual plan in a background thread."""
    root = getattr(app.ui_state, "root", None)
    if not root:
        messagebox.showwarning("BulkFolder", "Please choose a folder first.")
        return
    
    app.set_status("Scanning...")
    app.topbar_view.show_loading(True)
    
    def run_scan():
        try:
            # 1. Heavy Scanning Logic
            scanned = scan_folder(app.ui_state.root, include_subfolders=app.ui_state.include_subfolders)
            move_rule = MoveByExtensionRule(DEFAULT_MAPPING) if app.ui_state.move_by_ext else None
            plan = build_plan(app.ui_state.root, scanned, replace_rule=None, move_rule=move_rule)
            
            # Statistics calculation
            files_count = sum(1 for x in scanned if x.is_file)
            planned = sum(1 for it in plan.items if it.action.value != "skip")
            conflicts = sum(1 for it in plan.items if it.conflict)
            total_size = sum(x.size for x in scanned if x.is_file)

            # 2. Update UI back on main thread
            app.after(0, lambda: finalize_scan(scanned, plan, files_count, planned, conflicts, total_size))
            
        except Exception as e:
            app.after(0, lambda: handle_scan_error(str(e)))

    def finalize_scan(scanned, plan, files_count, planned, conflicts, total_size):
        app.last_scan = scanned
        app.last_plan = plan
        app.cards_view.set_values(str(files_count), str(planned), str(conflicts), app.human_bytes(total_size))
        app.preview_view.render(plan)
        app.dashboard_view.render(scanned, mapping=DEFAULT_MAPPING)
        
        app.organizer_panel.set_apply_enabled((not plan.has_conflicts) and planned > 0)
        app.organizer_panel.set_undo_enabled(True)
        app.tabs.set("Preview")
        
        app.topbar_view.show_loading(False)
        app.set_status("Ready")
        app.log(f"Scan complete: {files_count} files found.", level="INFO")

    def handle_scan_error(error_msg: str):
        app.topbar_view.show_loading(False)
        app.set_status("Error during scan.")
        messagebox.showerror("BulkFolder", f"Scan failed: {error_msg}")

    # Start the background thread
    threading.Thread(target=run_scan, daemon=True).start()

def apply_plan(app) -> None:
    """Physically apply changes in background."""
    if not app.last_plan or sum(1 for it in app.last_plan.items if it.action.value != "skip") == 0: return
    if app.last_plan.has_conflicts:
        messagebox.showerror("BulkFolder", "Plan has conflicts.")
        return
    
    if _ask_confirm(app, "BulkFolder", "Apply changes?"):
        app.set_status("Applying changes...")
        app.topbar_view.show_loading(True)

        def run_apply():
            try:
                # Execution with our custom logging callback (UIState.log)
                n = exec_apply_plan(app.last_plan, allow_conflicts=False, on_progress=app.log)
                app.after(0, lambda: finalize_apply())
            except Exception as e:
                app.after(0, lambda: handle_apply_error(str(e)))

        def finalize_apply():
            app.topbar_view.show_loading(False)
            app.set_status("Ready")
            scan_and_plan(app) # Refresh after apply

        def handle_apply_error(error_msg: str):
            app.topbar_view.show_loading(False)
            app.set_status("Error applying.")
            messagebox.showerror("BulkFolder", f"Apply failed: {error_msg}")

        threading.Thread(target=run_apply, daemon=True).start()

def undo_last_ops(app) -> None:
    """Revert last applied operations."""
    root = getattr(app.ui_state, "root", None)
    if not root: return
    if _ask_confirm(app, "BulkFolder", "Undo the last applied operations?"):
        try:
            n = exec_undo_last(app.ui_state.root)
            scan_and_plan(app)
        except Exception as e:
            messagebox.showerror("BulkFolder", f"Undo failed:\n{e}")

def find_duplicates_action(app) -> None:
    """Scans for duplicate files in background."""
    root = getattr(app.ui_state, "root", None)
    if not root: return
    
    app.set_status("Finding duplicates...")
    app.topbar_view.show_loading(True)

    def run_duplicates():
        min_kb = int(app.settings.duplicate_min_size_kb) if getattr(app, "settings", None) else 1
        scanned = app.last_scan or scan_folder(app.ui_state.root, include_subfolders=app.ui_state.include_subfolders)
        groups = find_duplicates(scanned, min_size_bytes=min_kb * 1024)
        ui_groups = [[str(p) for p in grp] for grp in groups]
        
        app.after(0, lambda: finalize_duplicates(ui_groups))

    def finalize_duplicates(ui_groups):
        app.duplicates_view.render(ui_groups)
        app.tabs.set("Duplicates")
        app.topbar_view.show_loading(False)
        app.set_status("Ready")

    threading.Thread(target=run_duplicates, daemon=True).start()

def chunker_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.chunker_root = Path(path)
        app.chunker_page.set_folder(str(path))
        app.chunker_page.render_preview([])
        app.chunker_plan = []

def chunker_preview(app) -> None:
    root = getattr(app.ui_state, "chunker_root", None)
    if not root:
        messagebox.showwarning("Folder Splitter", "Please choose a folder first.")
        return
    mode = app.chunker_page.mode_var.get()
    try:
        val = float(app.chunker_page.val_var.get())
        if val <= 0: raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number greater than 0.")
        return
    chunks = plan_chunks(root, mode, val)
    app.chunker_plan = chunks
    app.chunker_page.render_preview(chunks)
    app.set_status(f"Splitter: {len(chunks)} parts planned.")

def chunker_apply(app) -> None:
    plan = getattr(app, "chunker_plan", [])
    root = getattr(app.ui_state, "chunker_root", None)
    if not plan or not root: return
    if _ask_confirm(app, "Folder Splitter", f"Split this folder into {len(plan)} parts?"):
        app.set_status("Splitting folder...")
        app.topbar_view.show_loading(True)
        
        def run_chunk():
            success, errors = apply_chunks(root, plan)
            app.after(0, lambda: finalize_chunk(success, errors))

        def finalize_chunk(success, errors):
            app.topbar_view.show_loading(False)
            app.set_status("Ready")
            if errors:
                messagebox.showwarning("Partial Success", f"Moved: {success}\nErrors: {len(errors)}")
            else:
                messagebox.showinfo("Success", f"Successfully chunked folder!")
            app.chunker_page.render_preview([])

        threading.Thread(target=run_chunk, daemon=True).start()

def flattener_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.flattener_root = Path(path)
        app.flattener_page.set_folder(str(path))
        app.flattener_page.clear_preview()
        app.flattener_plan = []

def flattener_preview(app) -> None:
    root = getattr(app.ui_state, "flattener_root", None)
    if not root:
        messagebox.showwarning("Folder Flattener", "Please choose a folder first.")
        return
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
    if _ask_confirm(app, "Folder Flattener", f"Extract {len(plan)} files?"):
        for old_path, new_path in plan:
            try: old_path.rename(new_path)
            except Exception: pass
        if app.flattener_page.switch_delete.get():
            root = getattr(app.ui_state, "flattener_root", None)
            if root:
                dirs = sorted([d for d in root.rglob('*') if d.is_dir()], key=lambda x: len(x.parts), reverse=True)
                for d in dirs:
                    try:
                        if not any(d.iterdir()): d.rmdir()
                    except Exception: pass
        app.flattener_page.clear_preview()
        app.flattener_plan = []

def unzipper_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.unzipper_root = Path(path)
        app.unzipper_page.set_folder(str(path))
        app.unzipper_page.render_archives([])

def unzipper_refresh(app) -> None:
    root = getattr(app.ui_state, "unzipper_root", None)
    if not root:
        messagebox.showwarning("Archive Extractor", "Please choose a folder first.")
        return
    app.set_status("Scanning for archives...")
    allowed_exts = {'.zip', '.tar', '.gz', '.tgz', '.bz2', '.xz'}
    scanned = scan_folder(root, include_subfolders=True)
    archives = [item.path for item in scanned if item.is_file and item.path.suffix.lower() in allowed_exts]
    app.unzipper_page.render_archives(archives)

def unzipper_extract_selected(app, paths: list[Path]) -> None:
    if not paths: return
    delete_after = app.unzipper_page.switch_delete.get()
    if _ask_confirm(app, "Extract Archives", f"Extract {len(paths)} archive(s)?"):
        success_count = 0
        for path in paths:
            try:
                safe_name = path.name.replace(path.suffix, "")
                extract_dir = path.parent / safe_name
                counter = 1
                base_dir = extract_dir
                while extract_dir.exists():
                    extract_dir = path.parent / f"{base_dir.name}_{counter}"
                    counter += 1
                extract_dir.mkdir(parents=True, exist_ok=True)
                shutil.unpack_archive(str(path), str(extract_dir))
                success_count += 1
                if delete_after: path.unlink()
            except Exception as e:
                app.log(f"Failed to extract {path.name}: {e}", level="ERROR")
        messagebox.showinfo("Success", f"Successfully extracted {success_count} archives!")
        unzipper_refresh(app)

def pdf_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.pdf_root = Path(path)
        app.pdf_page.set_folder(str(path))
        app.pdf_page.render_files([])

def pdf_refresh(app) -> None:
    root = getattr(app.ui_state, "pdf_root", None)
    if not root:
        messagebox.showwarning("PDF Converter", "Please choose a folder first.")
        return
    allowed_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    scanned = scan_folder(root, include_subfolders=True)
    images = [item.path for item in scanned if item.is_file and item.path.suffix.lower() in allowed_exts]
    app.pdf_page.render_files(images)

def pdf_convert_selected(app, paths: list[Path]) -> None:
    if not paths: return
    delete_after = app.pdf_page.switch_delete.get()
    if _ask_confirm(app, "Convert to PDF", f"Convert {len(paths)} image(s)?"):
        success, errors = convert_images_to_pdf(paths, delete_original=delete_after)
        if errors:
            messagebox.showwarning("Partial Success", f"Converted: {success}\nFailed: {len(errors)}")
        else:
            messagebox.showinfo("Success", f"Successfully converted images!")
        pdf_refresh(app)

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
    if getattr(app, "large_files_scan", None) is None:
        app.large_files_scan = scan_folder(root, include_subfolders=True)
    min_bytes = min_mb * 1024 * 1024
    large_files = sorted([(i.path, i.size) for i in app.large_files_scan if i.is_file and i.size >= min_bytes], key=lambda x: x[1], reverse=True)
    app.large_files_page.render_files(large_files)

def large_files_delete_selected(app, paths: list[Path]) -> None:
    if not paths: return
    if _ask_confirm(app, "Delete", f"Permanently delete {len(paths)} file(s)?"):
        deleted = 0
        for path in paths:
            try:
                path.unlink()
                deleted += 1
                if getattr(app, "large_files_scan", None):
                    app.large_files_scan = [i for i in app.large_files_scan if i.path != path]
            except Exception: pass
        large_files_refresh(app, float(app.large_files_page.min_mb_var.get() or 0))

def renamer_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.renamer_root = Path(path)
        app.renamer_page.set_folder(str(path))
        app.renamer_page.clear_preview()
        app.renamer_plan = []

def renamer_preview(app) -> None:
    root = getattr(app.ui_state, "renamer_root", None)
    if not root:
        messagebox.showwarning("Mass Renamer", "Please choose a folder first.")
        return
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
    if _ask_confirm(app, "Mass Renamer", f"Apply new names to {len(plan)} files?"):
        for old_path, new_path in plan:
            try:
                if not new_path.exists(): old_path.rename(new_path)
            except Exception: pass
        app.renamer_page.clear_preview()
        app.renamer_plan = []

def dateorg_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.dateorg_root = Path(path)
        app.dateorg_page.set_folder(str(path))
        app.dateorg_page.clear_preview()
        app.dateorg_plan = []

def dateorg_preview(app) -> None:
    root = getattr(app.ui_state, "dateorg_root", None)
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
            counter = 1
            while new_path.exists() or new_path in [p[1] for p in app.dateorg_plan]:
                new_path = dest_dir / f"{item.path.stem}_{counter}{item.path.suffix}"
                counter += 1
            app.dateorg_plan.append((item.path, new_path))
            preview_list.append((item.path.name, f"{folder_name}/{new_path.name}"))
        except Exception: pass
    app.dateorg_page.render_preview(preview_list)

def dateorg_apply(app) -> None:
    plan = getattr(app, "dateorg_plan", [])
    if not plan: return
    if _ask_confirm(app, "Date Organizer", f"Organize {len(plan)} files?"):
        for old_path, new_path in plan:
            try:
                new_path.parent.mkdir(parents=True, exist_ok=True)
                old_path.rename(new_path)
            except Exception: pass
        app.dateorg_page.clear_preview()
        app.dateorg_plan = []

def empty_folders_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.empty_folders_root = Path(path)
        app.empty_folders_page.set_folder(str(path))
        app.empty_folders_page.render_folders([])

def empty_folders_refresh(app) -> None:
    root = getattr(app.ui_state, "empty_folders_root", None)
    if not root:
        messagebox.showwarning("Empty Folders Cleaner", "Please choose a folder first.")
        return
    empty_dirs = []
    ignored_files = {'.ds_store', 'thumbs.db', 'desktop.ini'}
    dirs = sorted([d for d in root.rglob('*') if d.is_dir()], key=lambda x: len(x.parts), reverse=True)
    virtual_empty = set()
    for d in dirs:
        is_empty = True
        try:
            for item in d.iterdir():
                if item.is_file() and item.name.lower() not in ignored_files:
                    is_empty = False
                    break
                if item.is_dir() and item not in virtual_empty:
                    is_empty = False
                    break
            if is_empty:
                virtual_empty.add(d)
                empty_dirs.append(d)
        except Exception: pass
    empty_dirs.reverse()
    app.empty_folders_page.render_folders(empty_dirs)

def empty_folders_delete_selected(app, paths: list[Path]) -> None:
    if not paths: return
    if _ask_confirm(app, "Delete", f"Delete {len(paths)} empty folder(s)?"):
        paths.sort(key=lambda x: len(x.parts), reverse=True)
        for path in paths:
            try: shutil.rmtree(path)
            except Exception: pass
        empty_folders_refresh(app)

def open_github(app, url: str) -> None:
    if url: webbrowser.open(url)

def settings_save(app) -> None:
    old_theme = app.settings.theme_name
    new_settings = app.settings_page.read_settings_from_form()
    app.settings = new_settings
    save_settings(new_settings)
    if new_settings.theme_name != old_theme:
        app.destroy() 
        python = sys.executable 
        os.execv(python, [python, "-m", "bulkfolder.ui.main"])