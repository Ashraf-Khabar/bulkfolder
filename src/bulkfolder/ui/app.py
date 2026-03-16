from __future__ import annotations
import sys
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk

# --- Imports: Theme, State, and Logic ---
from .theme import DR_BG, DR_TEXT, DR_MUTED, DR_SURFACE, DR_BORDER, DR_PURPLE
from .state import UIState
from . import actions

# --- Imports: Configuration and Project Info ---
from ..config import load_settings, AppSettings
from ..info import get_project_info

# --- Imports: Views (UI Components) ---
from .views.sidebar import SidebarView
from .views.topbar import TopbarView
from .views.cards import CardsRow
from .views.dashboard import DashboardView
from .views.preview import PreviewView
from .views.logs import LogsView
from .views.organizer_panel import OrganizerPanel
from .views.renamer_page import RenamerPage
from .views.chunker_page import ChunkerPage
from .views.flattener_page import FlattenerPage  
from .views.unzipper_page import UnzipperPage
from .views.pdf_page import PdfPage              
from .views.dateorg_page import DateOrgPage
from .views.empty_folders_page import EmptyFoldersPage
from .views.settings_page import SettingsPage
from .views.large_files_page import LargeFilesPage
from .views.about_page import AboutPage

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master, logo_path):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color=DR_BG)
        width, height = 340, 380
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.grid(row=0, column=0)
        if logo_path and logo_path.exists():
            img = Image.open(logo_path)
            self.photo = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
            ctk.CTkLabel(inner, text="", image=self.photo).pack(pady=(0, 20))
        ctk.CTkLabel(inner, text="BulkFolder", font=ctk.CTkFont(size=26, weight="bold"), text_color=DR_TEXT).pack()
        ctk.CTkLabel(inner, text="Organize & Rename safely", font=ctk.CTkFont(size=13), text_color=DR_MUTED).pack(pady=(0, 20))
        self.pb = ctk.CTkProgressBar(inner, width=220, progress_color=DR_PURPLE, fg_color=DR_BORDER)
        self.pb.pack(pady=(5, 0))
        self.pb.set(0)
        self.pb.start()

class App(ctk.CTk):
    def __init__(self):
        try:
            if sys.platform.startswith("win"):
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception: pass
        super().__init__()
        self.withdraw()
        self._resize_after_id = None
        self.settings: AppSettings = load_settings()
        ctk.set_appearance_mode("dark")
        self.title("BulkFolder")
        self.geometry("1240x800")
        self.minsize(1020, 700)
        self.configure(fg_color=DR_BG)
        self.bind("<Configure>", self._smart_resize)
        self.logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logo.png"
        self._ensure_logo_exists(self.logo_path)
        self.ui_state = UIState()
        self.last_plan = None
        self.last_scan = None
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.splash = SplashScreen(self, self.logo_path)
        self.splash.update()
        info = get_project_info()
        self.sidebar_view = SidebarView(info, self, on_page=self.switch_page, logo_path=self.logo_path)
        self.sidebar_view.grid(row=0, column=0, rowspan=2, sticky="nsw")
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color=DR_BG)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1) 
        self.content_area.grid_rowconfigure(2, weight=0) 
        self.topbar_view = TopbarView(self.content_area, on_toggle_sidebar=self.toggle_terminal)
        self.topbar_view.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
        self.page_container = ctk.CTkFrame(self.content_area, corner_radius=0, fg_color=DR_BG)
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)
        self.logs_view = LogsView(self.content_area, on_close=self.toggle_terminal)
        self.logs_view.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        self._terminal_visible = True
        self.ui_state.log_view = self.logs_view
        self.pages: dict[str, ctk.CTkFrame] = {}
        self.pages["Organizer"] = self._build_page_organizer(self.page_container)
        self.pages["Renamer"] = self._build_page_renamer(self.page_container)
        self.pages["Chunker"] = self._build_page_chunker(self.page_container)
        self.pages["Flattener"] = self._build_page_flattener(self.page_container)
        self.pages["Unzipper"] = self._build_page_unzipper(self.page_container)
        self.pages["PdfConverter"] = self._build_page_pdf(self.page_container) 
        self.pages["DateOrg"] = self._build_page_dateorg(self.page_container)
        self.pages["EmptyFolders"] = self._build_page_empty_folders(self.page_container)
        self.pages["LargeFiles"] = self._build_page_large_files(self.page_container)
        self.pages["Settings"] = self._build_page_settings(self.page_container)
        self.pages["About"] = self._build_page_about(self.page_container)
        self._current_page = ""
        self.switch_page("Organizer")
        self.after(2000, self._show_main_window)

    def _smart_resize(self, event):
        if event.widget == self:
            if self._resize_after_id: self.after_cancel(self._resize_after_id)
            self._resize_after_id = self.after(50, self._do_refresh)

    def _do_refresh(self):
        self.update_idletasks()
        self._resize_after_id = None

    @staticmethod
    def _ensure_logo_exists(png_path: Path):
        ico_path = png_path.with_suffix(".ico")
        if not png_path.exists(): return
        try:
            img = Image.open(png_path).convert("RGBA")
            bbox = img.getbbox()
            if bbox: img = img.crop(bbox)
            layers = [img.resize((s, s), Image.Resampling.LANCZOS) for s in [256, 128, 64, 48, 32, 16]]
            layers[0].save(ico_path, format="ICO", append_images=layers[1:])
        except Exception: pass

    def _show_main_window(self):
        try: self.splash.destroy()
        except: pass
        self.deiconify()

    def _build_page_organizer(self, parent) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, corner_radius=0, fg_color=DR_BG)
        frame.grid_columnconfigure(0, weight=0); frame.grid_columnconfigure(1, weight=1); frame.grid_rowconfigure(0, weight=1)
        self.organizer_panel = OrganizerPanel(frame,
            on_choose_folder=lambda: actions.choose_folder(self),
            on_scan=lambda: actions.scan_and_plan(self),
            on_apply=lambda: actions.apply_plan(self),
            on_undo=lambda: actions.undo_last_ops(self),
            on_toggle_subfolders=lambda enabled: actions.toggle_subfolders(self, enabled),
        )
        self.organizer_panel.grid(row=0, column=0, sticky="ns", padx=(18, 10), pady=(0, 18))
        right = ctk.CTkFrame(frame, corner_radius=0, fg_color=DR_BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 18), pady=(0, 18))
        right.grid_columnconfigure(0, weight=1); right.grid_rowconfigure(2, weight=1)
        self.cards_view = CardsRow(right)
        self.cards_view.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.tabs = ctk.CTkTabview(right, fg_color=DR_BG)
        self.tabs.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        self.dashboard_view = DashboardView(self.tabs.add("Dashboard"))
        self.dashboard_view.pack(fill="both", expand=True)
        self.preview_view = PreviewView(self.tabs.add("Preview"))
        self.preview_view.pack(fill="both", expand=True)
        return frame

    def _build_page_renamer(self, p): return RenamerPage(p, on_choose_folder=lambda: actions.renamer_choose_folder(self), on_preview=lambda: actions.renamer_preview(self), on_apply=lambda: actions.renamer_apply(self))
    def _build_page_chunker(self, p): return ChunkerPage(p, on_choose_folder=lambda: actions.chunker_choose_folder(self), on_preview=lambda: actions.chunker_preview(self), on_apply=lambda: actions.chunker_apply(self))
    def _build_page_flattener(self, p): return FlattenerPage(p, on_choose_folder=lambda: actions.flattener_choose_folder(self), on_preview=lambda: actions.flattener_preview(self), on_apply=lambda: actions.flattener_apply(self))
    def _build_page_unzipper(self, p): return UnzipperPage(p, on_choose_folder=lambda: actions.unzipper_choose_folder(self), on_refresh=lambda: actions.unzipper_refresh(self), on_extract_selected=lambda paths: actions.unzipper_extract_selected(self, paths))
    def _build_page_pdf(self, p): return PdfPage(p, on_choose_folder=lambda: actions.pdf_choose_folder(self), on_refresh=lambda: actions.pdf_refresh(self), on_convert=lambda paths: actions.pdf_convert_selected(self, paths))
    def _build_page_dateorg(self, p): return DateOrgPage(p, on_choose_folder=lambda: actions.dateorg_choose_folder(self), on_preview=lambda: actions.dateorg_preview(self), on_apply=lambda: actions.dateorg_apply(self))
    def _build_page_empty_folders(self, p): return EmptyFoldersPage(p, on_choose_folder=lambda: actions.empty_folders_choose_folder(self), on_refresh=lambda: actions.empty_folders_refresh(self), on_delete_selected=lambda paths: actions.empty_folders_delete_selected(self, paths))
    def _build_page_large_files(self, p): return LargeFilesPage(p, on_choose_folder=lambda: actions.large_files_choose_folder(self), on_refresh=lambda m: actions.large_files_refresh(self, m), on_delete_selected=lambda paths: actions.large_files_delete_selected(self, paths))
    def _build_page_settings(self, p): return SettingsPage(p, settings=self.settings, on_save=lambda: actions.settings_save(self))
    def _build_page_about(self, p): return AboutPage(p, project_info=get_project_info(), on_open_github=lambda url: actions.open_github(self, url))

    def switch_page(self, page_name: str) -> None:
        if page_name not in self.pages: return
        if self._current_page: self.pages[self._current_page].grid_forget()
        self.pages[page_name].grid(row=0, column=0, sticky="nsew")
        self._current_page = page_name
        self.topbar_view.set_title(page_name)
        self.update_idletasks()

    def toggle_terminal(self) -> None:
        if self._terminal_visible:
            self.logs_view.grid_forget(); self._terminal_visible = False
        else:
            self.logs_view.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18)); self._terminal_visible = True

    def set_status(self, s: str) -> None: self.topbar_view.set_status(s)
    def log(self, s: str, level: str = "INFO") -> None: self.ui_state.log(s, level=level)

    @staticmethod
    def human_bytes(n: int) -> str:
        step = 1024.0
        for u in ["B", "KB", "MB", "GB", "TB"]:
            if n < step: return f"{n:.1f} {u}"
            n /= step
        return f"{n:.1f} PB"
