from __future__ import annotations

import os
import sys
import shutil
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

# --- Core Logic Imports ---
# Importing the actual engines that do the heavy lifting (scanning, moving, splitting, etc.)
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
# A dictionary mapping file extensions to their target category folder names.
# This is used by the Organizer when the "Move by Extension" rule is enabled.
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
    """
    Helper function to ask the user for confirmation before performing destructive or major actions.
    It checks the user's settings to see if confirmations are disabled globally.
    """
    if not getattr(app.settings, "ask_confirmations", True):
        return True 
    return messagebox.askyesno(title, message)


# ==========================================
# ORGANIZER ACTIONS (Main Tab)
# ==========================================

def choose_folder(app) -> None:
    """Opens a dialog to select the main working directory and updates the UI state."""
    path = filedialog.askdirectory()
    if not path: return
    app.ui_state.root = Path(path)
    app.organizer_panel.set_folder(str(app.ui_state.root))
    app.set_status("Folder selected.")
    app.log(f"Selected folder: {app.ui_state.root}", level="SUCCESS")
    app.organizer_panel.set_undo_enabled(True)
    
    # Auto-scan feature: automatically builds the plan if enabled in settings
    if getattr(app, "settings", None) and app.settings.autoscan_on_folder_select:
        scan_and_plan(app)

def toggle_subfolders(app, enabled: bool) -> None:
    app.ui_state.include_subfolders = enabled

def toggle_move_by_ext(app, enabled: bool) -> None:
    app.ui_state.move_by_ext = enabled

def scan_and_plan(app) -> None:
    """
    Reads the selected folder and builds a virtual "Plan" of what will happen 
    (renaming, moving) without actually modifying any files yet.
    """
    root = getattr(app.ui_state, "root", None)
    if not root:
        messagebox.showwarning("BulkFolder", "Please choose a folder first.")
        return
    
    # Retrieve user input from the UI fields
    app.ui_state.find_text = app.organizer_panel.get_find_text().strip()
    app.ui_state.replace_text = app.organizer_panel.get_replace_text().strip()
    app.set_status("Scanning...")
    
    # 1. Scan the actual hard drive
    scanned = scan_folder(app.ui_state.root, include_subfolders=app.ui_state.include_subfolders)
    app.last_scan = scanned

    # 2. Apply chosen rules to generate the plan
    replace_rule = ReplaceTextRule(app.ui_state.find_text, app.ui_state.replace_text) if app.ui_state.find_text else None
    move_rule = MoveByExtensionRule(DEFAULT_MAPPING) if app.ui_state.move_by_ext else None
    plan = build_plan(app.ui_state.root, scanned, replace_rule=replace_rule, move_rule=move_rule)
    app.last_plan = plan

    # 3. Calculate statistics for the dashboard cards
    files_count = sum(1 for x in scanned if x.is_file)
    planned = sum(1 for it in plan.items if it.action.value != "skip")
    conflicts = sum(1 for it in plan.items if it.conflict)
    total_size = sum(x.size for x in scanned if x.is_file)

    # 4. Update the UI with the calculated data
    app.cards_view.set_values(str(files_count), str(planned), str(conflicts), app.human_bytes(total_size))
    app.preview_view.render(plan)
    app.dashboard_view.render(scanned, mapping=DEFAULT_MAPPING)
    
    # Only enable the "Apply" button if there's work to do and no conflicting file names
    app.organizer_panel.set_apply_enabled((not plan.has_conflicts) and planned > 0)
    app.organizer_panel.set_undo_enabled(True)
    app.tabs.set("Preview")

def apply_plan(app) -> None:
    """Executes the virtual plan, physically moving and renaming files on the disk."""
    if not app.last_plan or sum(1 for it in app.last_plan.items if it.action.value != "skip") == 0: return
    if app.last_plan.has_conflicts:
        messagebox.showerror("BulkFolder", "Plan has conflicts.")
        return
    if _ask_confirm(app, "BulkFolder", "Apply changes?"):
        try:
            n = exec_apply_plan(app.last_plan, allow_conflicts=False)
            app.set_status("Applied.")
            scan_and_plan(app) # Rescan to show the updated state
        except Exception as e:
            messagebox.showerror("BulkFolder", f"Apply failed:\n{e}")

def undo_last_ops(app) -> None:
    """Reverts the last applied plan by using the undo log saved on disk."""
    root = getattr(app.ui_state, "root", None)
    if not root: return
    if _ask_confirm(app, "BulkFolder", "Undo the last applied operations?"):
        try:
            n = exec_undo_last(app.ui_state.root)
            scan_and_plan(app)
        except Exception as e:
            messagebox.showerror("BulkFolder", f"Undo failed:\n{e}")

def find_duplicates_action(app) -> None:
    """Scans for duplicate files based on file hashing (content comparison, not just name)."""
    root = getattr(app.ui_state, "root", None)
    if not root: return
    
    min_kb = int(app.settings.duplicate_min_size_kb) if getattr(app, "settings", None) else 1
    scanned = app.last_scan or scan_folder(app.ui_state.root, include_subfolders=app.ui_state.include_subfolders)
    app.last_scan = scanned
    
    groups = find_duplicates(scanned, min_size_bytes=min_kb * 1024)
    ui_groups = [[str(p) for p in grp] for grp in groups]
    
    app.duplicates_view.render(ui_groups)
    app.tabs.set("Duplicates")


# ==========================================
# FOLDER SPLITTER (Chunker)
# ==========================================

def chunker_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.chunker_root = Path(path)
        app.chunker_page.set_folder(str(path))
        app.chunker_page.render_preview([])
        app.chunker_plan = []

def chunker_preview(app) -> None:
    """Creates a virtual plan dividing files into chunks by Count or Size."""
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

    # Call the core logic to calculate chunks
    chunks = plan_chunks(root, mode, val)
    app.chunker_plan = chunks
    app.chunker_page.render_preview(chunks)
    app.set_status(f"Splitter: {len(chunks)} parts planned.")

def chunker_apply(app) -> None:
    """Physically creates subfolders and moves files into their respective chunks."""
    plan = getattr(app, "chunker_plan", [])
    root = getattr(app.ui_state, "chunker_root", None)
    if not plan or not root: return

    if _ask_confirm(app, "Folder Splitter", f"Split this folder into {len(plan)} parts?"):
        app.set_status("Splitting folder... Please wait.")
        app.update() # Force UI refresh before heavy operation
        
        success, errors = apply_chunks(root, plan)
        
        if errors:
            messagebox.showwarning("Partial Success", f"Moved: {success}\nErrors: {len(errors)}")
            for err in errors:
                app.log(f"Split Error: {err}", level="ERROR")
        else:
            messagebox.showinfo("Success", f"Successfully chunked folder into {len(plan)} parts!")
            
        app.log(f"Successfully moved {success} files into {len(plan)} chunks.", level="SUCCESS")
        
        # Clear the preview after successful execution
        app.chunker_page.render_preview([])
        app.chunker_plan = []


# ==========================================
# FOLDER FLATTENER
# ==========================================

def flattener_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.flattener_root = Path(path)
        app.flattener_page.set_folder(str(path))
        app.flattener_page.clear_preview()
        app.flattener_plan = []

def flattener_preview(app) -> None:
    """Plans to move all files from subdirectories into the root directory."""
    root = getattr(app.ui_state, "flattener_root", None)
    if not root:
        messagebox.showwarning("Folder Flattener", "Please choose a folder first.")
        return
        
    scanned = scan_folder(root, include_subfolders=True)
    app.flattener_plan = []
    preview_list = []
    # Keep track of names to prevent overwriting files with the same name
    taken_names = set(p.path.name for p in scanned if p.is_file and p.path.parent == root)

    for item in scanned:
        if item.is_file and item.path.parent != root:
            new_path = root / item.path.name
            counter = 1
            # Append a number if the filename already exists in the root
            while new_path.name in taken_names:
                new_path = root / f"{item.path.stem}_{counter}{item.path.suffix}"
                counter += 1
            taken_names.add(new_path.name)
            app.flattener_plan.append((item.path, new_path))
            preview_list.append((str(item.path.relative_to(root)), new_path.name))

    app.flattener_page.render_preview(preview_list)

def flattener_apply(app) -> None:
    """Executes the flattening plan and optionally deletes empty leftover directories."""
    plan = getattr(app, "flattener_plan", [])
    if not plan: return
    if _ask_confirm(app, "Folder Flattener", f"Extract {len(plan)} files?"):
        for old_path, new_path in plan:
            try: old_path.rename(new_path)
            except Exception: pass
            
        # If user checked "Delete empty folders after flattening"
        if app.flattener_page.switch_delete.get():
            root = getattr(app.ui_state, "flattener_root", None)
            if root:
                # Sort from deepest to shallowest to avoid deleting a parent before its children
                dirs = sorted([d for d in root.rglob('*') if d.is_dir()], key=lambda x: len(x.parts), reverse=True)
                for d in dirs:
                    try:
                        if not any(d.iterdir()): d.rmdir()
                    except Exception: pass
                    
        app.flattener_page.clear_preview()
        app.flattener_plan = []


# ==========================================
# ARCHIVE EXTRACTOR (Unzipper)
# ==========================================

def unzipper_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.unzipper_root = Path(path)
        app.unzipper_page.set_folder(str(path))
        app.unzipper_page.render_archives([])

def unzipper_refresh(app) -> None:
    """Scans the directory specifically for supported compressed archive formats."""
    root = getattr(app.ui_state, "unzipper_root", None)
    if not root:
        messagebox.showwarning("Archive Extractor", "Please choose a folder first.")
        return

    app.set_status("Scanning for archives...")
    allowed_exts = {'.zip', '.tar', '.gz', '.tgz', '.bz2', '.xz'}
    scanned = scan_folder(root, include_subfolders=True)
    
    archives = [item.path for item in scanned if item.is_file and item.path.suffix.lower() in allowed_exts]
    app.unzipper_page.render_archives(archives)
    app.set_status(f"Archives: {len(archives)} found.")

def unzipper_extract_selected(app, paths: list[Path]) -> None:
    """Extracts the selected archives into individual folders named after the archive."""
    if not paths: return
    delete_after = app.unzipper_page.switch_delete.get()
    
    msg = f"Extract {len(paths)} archive(s)?"
    if delete_after:
        msg += "\nOriginal archives will be DELETED after successful extraction."

    if _ask_confirm(app, "Extract Archives", msg):
        app.set_status("Extracting... Please wait.")
        app.update() 
        
        success_count = 0
        for path in paths:
            try:
                # Create a safe target directory name based on the archive name
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
                
                if delete_after:
                    path.unlink() # Delete the original .zip
            except Exception as e:
                app.log(f"Failed to extract {path.name}: {e}", level="ERROR")

        messagebox.showinfo("Success", f"Successfully extracted {success_count} archives!")
        app.log(f"Successfully extracted {success_count}/{len(paths)} archives.", level="SUCCESS")
        unzipper_refresh(app)


# ==========================================
# IMAGE TO PDF
# ==========================================

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

    app.set_status("Scanning for images...")
    allowed_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    scanned = scan_folder(root, include_subfolders=True)
    
    images = [item.path for item in scanned if item.is_file and item.path.suffix.lower() in allowed_exts]
    app.pdf_page.render_files(images)
    app.set_status(f"Images: {len(images)} found.")

def pdf_convert_selected(app, paths: list[Path]) -> None:
    if not paths: return
    delete_after = app.pdf_page.switch_delete.get()
    
    msg = f"Convert {len(paths)} image(s) to PDF?"
    if delete_after: msg += "\nOriginal images will be DELETED."

    if _ask_confirm(app, "Convert to PDF", msg):
        app.set_status("Converting... Please wait.")
        app.update() 
        
        success, errors = convert_images_to_pdf(paths, delete_original=delete_after)
        
        if errors:
            messagebox.showwarning("Partial Success", f"Converted: {success}\nFailed: {len(errors)}\nCheck logs for details.")
            for err in errors:
                app.log(f"PDF Error: {err}", level="ERROR")
        else:
            messagebox.showinfo("Success", f"Successfully converted {success} images to PDF!")
            
        app.log(f"Successfully converted {success}/{len(paths)} images to PDF.", level="SUCCESS")
        pdf_refresh(app)


# ==========================================
# LARGE FILES CLEANER
# ==========================================

def large_files_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.large_files_root = Path(path)
        app.large_files_page.set_folder(str(path))
        app.large_files_scan = None
        app.large_files_page.render_files([])

def large_files_refresh(app, min_mb: float) -> None:
    """Finds files larger than the specified Megabyte threshold."""
    root = getattr(app.ui_state, "large_files_root", None)
    if not root:
        messagebox.showwarning("Large Files", "Please choose a folder first.")
        return
    
    app.set_status("Scanning for large files...")
    # Cache the scan to avoid reading the disk again if we just change the MB slider
    if getattr(app, "large_files_scan", None) is None:
        app.large_files_scan = scan_folder(root, include_subfolders=True)
    
    min_bytes = min_mb * 1024 * 1024
    large_files = sorted([(i.path, i.size) for i in app.large_files_scan if i.is_file and i.size >= min_bytes], key=lambda x: x[1], reverse=True)
    app.large_files_page.render_files(large_files)

def large_files_delete_selected(app, paths: list[Path]) -> None:
    if not paths: return
    if _ask_confirm(app, "Delete", f"Permanently delete {len(paths)} selected file(s)?\nThis action cannot be undone."):
        deleted = 0
        for path in paths:
            try:
                path.unlink()
                deleted += 1
                # Remove from cache to keep UI in sync without a full rescan
                if getattr(app, "large_files_scan", None):
                    app.large_files_scan = [i for i in app.large_files_scan if i.path != path]
            except Exception as e:
                app.log(f"Error deleting {path.name}: {e}", level="ERROR")
        
        messagebox.showinfo("Cleaned", f"Successfully deleted {deleted} files!")
        app.log(f"Deleted {deleted} files.", level="WARN")
        large_files_refresh(app, float(app.large_files_page.min_mb_var.get() or 0))


# ==========================================
# MASS RENAMER
# ==========================================

def renamer_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.renamer_root = Path(path)
        app.renamer_page.set_folder(str(path))
        app.renamer_page.clear_preview()
        app.renamer_plan = []

def renamer_preview(app) -> None:
    """Builds a plan to add prefixes, suffixes, or sequential numbers to filenames."""
    root = getattr(app.ui_state, "renamer_root", None)
    if not root:
        messagebox.showwarning("Mass Renamer", "Please choose a folder first.")
        return

    prefix = app.renamer_page.entry_prefix.get().strip()
    suffix = app.renamer_page.entry_suffix.get().strip()
    add_num = app.renamer_page.switch_num.get()

    if not prefix and not suffix and not add_num: return

    # Sort files alphabetically to ensure numbering is consistent
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
            # Add a zero-padded number (e.g., _001, _002)
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


# ==========================================
# DATE ORGANIZER
# ==========================================

def dateorg_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.dateorg_root = Path(path)
        app.dateorg_page.set_folder(str(path))
        app.dateorg_page.clear_preview()
        app.dateorg_plan = []

def dateorg_preview(app) -> None:
    """Plans sorting files into subfolders based on their last modification date."""
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
            # Read the OS modification time stamp and convert it to a datetime object
            mtime = item.path.stat().st_mtime
            dt = datetime.fromtimestamp(mtime)
            
            # Format the folder hierarchy based on user selection
            if "Year/Month/Day" in mode:
                folder_name = os.path.join(dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d"))
            elif "Year/Month" in mode:
                folder_name = os.path.join(dt.strftime("%Y"), dt.strftime("%m"))
            else:
                folder_name = dt.strftime("%Y")
                
            dest_dir = root / folder_name
            new_path = dest_dir / item.path.name
            
            # Prevent overwriting if a file with the same name exists in the target date folder
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

    if _ask_confirm(app, "Date Organizer", f"Organize {len(plan)} files by date?"):
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


# ==========================================
# EMPTY FOLDERS CLEANER
# ==========================================

def empty_folders_choose_folder(app) -> None:
    path = filedialog.askdirectory()
    if path:
        app.ui_state.empty_folders_root = Path(path)
        app.empty_folders_page.set_folder(str(path))
        app.empty_folders_page.render_folders([])

def empty_folders_refresh(app) -> None:
    """Finds directories that contain no files (ignoring system files like .DS_Store)."""
    root = getattr(app.ui_state, "empty_folders_root", None)
    if not root:
        messagebox.showwarning("Empty Folders Cleaner", "Please choose a folder first.")
        return
        
    app.set_status("Scanning for empty folders...")
    
    empty_dirs = []
    ignored_files = {'.ds_store', 'thumbs.db', 'desktop.ini'}
    
    # Sort deepest folders first, so we can detect if a parent folder will become empty
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
        except Exception:
            pass

    # Reverse to show highest-level empty folders at the top of the UI
    empty_dirs.reverse()
    app.empty_folders_page.render_folders(empty_dirs)
    app.set_status(f"Empty Folders: {len(empty_dirs)} found.")

def empty_folders_delete_selected(app, paths: list[Path]) -> None:
    if not paths: return
    if _ask_confirm(app, "Delete", f"Delete {len(paths)} empty folder(s)?"):
        deleted = 0
        # Always delete from the deepest level first
        paths.sort(key=lambda x: len(x.parts), reverse=True)
        for path in paths:
            try:
                shutil.rmtree(path)
                deleted += 1
            except Exception as e:
                app.log(f"Error deleting folder {path.name}: {e}", level="ERROR")
                
        app.log(f"Cleaned {deleted} empty folders.", level="SUCCESS")
        empty_folders_refresh(app)


# ==========================================
# ℹABOUT & LINKS
# ==========================================

def open_github(app, url: str) -> None:
    """Opens the user's default web browser to the given URL."""
    if url:
        app.log(f"Opening browser: {url}", level="INFO")
        webbrowser.open(url)
    else:
        messagebox.showerror("Error", "No repository URL found in configuration.")


# ==========================================
# SETTINGS ACTIONS
# ==========================================

def settings_save(app) -> None:
    """
    Saves user preferences (scaling, theme, etc.) to the disk.
    If the theme changes, it automatically reboots the application to apply the new colors.
    """
    old_theme = app.settings.theme_name
    new_settings = app.settings_page.read_settings_from_form()
    app.settings = new_settings
    
    app.set_status("Applying settings...")
    
    try:
        scale_val = float(new_settings.ui_scaling.replace("%", "")) / 100.0
        ctk.set_widget_scaling(scale_val)
        ctk.set_window_scaling(scale_val)
    except Exception:
        pass

    # Save to JSON config file
    save_settings(new_settings)
    app.set_status("Settings saved.")
    app.log("Settings saved. UI updated.", level="SUCCESS")

    # If the theme has changed, we must restart the app completely
    if new_settings.theme_name != old_theme:
        messagebox.showwarning(
            "Restart Required", 
            f"Theme set to '{new_settings.theme_name}'.\n\nThe application will now restart automatically to apply the new colors."
        )
        
        # --- RESTART FIX ---
        # 1. Cleanly close the current Tkinter window
        app.destroy() 
        
        # 2. Get the path to the current Python interpreter
        python = sys.executable 
        
        # 3. Replace the current process with a new one. 
        # Using "-m bulkfolder.ui.main" ensures relative imports work perfectly!
        os.execv(python, [python, "-m", "bulkfolder.ui.main"])
