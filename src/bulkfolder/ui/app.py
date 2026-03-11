from __future__ import annotations
import sys
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk

from .theme import DR_BG, DR_TEXT, DR_MUTED, DR_SURFACE, DR_BORDER, DR_PURPLE
from .state import UIState
from . import actions
from ..info import get_project_info
from ..config import load_settings

from .views.sidebar import SidebarView
from .views.topbar import TopbarView
from .views.cards import CardsRow
from .views.dashboard import DashboardView
from .views.preview import PreviewView
from .views.logs import LogsView
from .views.duplicates import DuplicatesView
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
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")
        if logo_path and logo_path.exists():
            img = Image.open(logo_path)
            self.photo = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
            ctk.CTkLabel(inner, text="", image=self.photo).pack(pady=(0, 20))
        ctk.CTkLabel(inner, text="BulkFolder", font=ctk.CTkFont(size=26, weight="bold"), text_color=DR_TEXT).pack()
        self.pb = ctk.CTkProgressBar(inner, width=220, progress_color=DR_PURPLE, fg_color=DR_BORDER)
        self.pb.pack(pady=(20, 0))
        self.pb.set(0)
        self.pb.start()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.settings = load_settings()
        ctk.set_appearance_mode("dark")
        
        self.title("BulkFolder")
        self.geometry("1200x750")
        self.configure(fg_color=DR_BG)

        self.logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logo.png"
        if self.logo_path.exists():
            img = Image.open(self.logo_path)
            photo = ImageTk.PhotoImage(img)
            self.wm_iconphoto(True, photo)
            if sys.platform.startswith("win"):
                try:
                    import ctypes
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("bulkfolder.app.v1.1")
                    ico_path = self.logo_path.with_suffix(".ico")
                    if ico_path.exists(): self.iconbitmap(str(ico_path))
                except: pass

        self.splash = SplashScreen(self, self.logo_path)
        self.splash.update()

        self.ui_state = UIState()
        self.last_plan = None
        self.renamer_plan = []
        self.chunker_plan = []
        self.flattener_plan = []
        self.dateorg_plan = []

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_view = SidebarView(get_project_info(), self, on_page=self.switch_page, logo_path=self.logo_path)
        self.sidebar_view.grid(row=0, column=0, sticky="nsw")

        self.main = ctk.CTkFrame(self, corner_radius=0, fg_color=DR_BG)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        self.topbar_view = TopbarView(self.main)
        self.topbar_view.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))

        self.page_container = ctk.CTkFrame(self.main, corner_radius=0, fg_color=DR_BG)
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        self.pages: dict[str, ctk.CTkFrame] = {}
        self._build_all_pages()
        self._current_page = ""
        self.switch_page("Organizer")

        self.after(2000, self._show_main_window)

    @property
    def settings_page(self):
        """ Redirection for actions.py to find the settings page in the pages dictionary """
        return self.pages.get("Settings")

    def _build_all_pages(self):
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

    def switch_page(self, page_name: str) -> None:
        if page_name not in self.pages: return
        if self._current_page: self.pages[self._current_page].grid_forget()
        self.pages[page_name].grid(row=0, column=0, sticky="nsew")
        self._current_page = page_name
        self.topbar_view.set_title(page_name)

    def _show_main_window(self):
        try: self.splash.destroy()
        except: pass
        self.deiconify()

    def _build_page_organizer(self, parent) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, corner_radius=0, fg_color=DR_BG)
        frame.grid_columnconfigure(1, weight=1); frame.grid_rowconfigure(0, weight=1)
        self.organizer_panel = OrganizerPanel(frame,
            on_choose_folder=lambda: actions.choose_folder(self),
            on_scan=lambda: actions.scan_and_plan(self),
            on_find_duplicates=lambda: actions.find_duplicates_action(self),
            on_apply=lambda: actions.apply_plan(self),
            on_undo=lambda: actions.undo_last_ops(self),
            on_toggle_subfolders=lambda e: actions.toggle_subfolders(self, e),
            on_toggle_move_by_ext=lambda e: actions.toggle_move_by_ext(self, e))
        self.organizer_panel.grid(row=0, column=0, sticky="ns", padx=(18, 10), pady=(0, 18))
        right = ctk.CTkFrame(frame, fg_color=DR_BG)
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
        self.duplicates_view = DuplicatesView(self.tabs.add("Duplicates"))
        self.duplicates_view.pack(fill="both", expand=True)
        self.logs_view = LogsView(self.tabs.add("Logs"))
        self.logs_view.pack(fill="both", expand=True)
        return frame

    def _build_page_renamer(self, p): return RenamerPage(p, lambda: actions.renamer_choose_folder(self), lambda: actions.renamer_preview(self), lambda: actions.renamer_apply(self))
    def _build_page_chunker(self, p): return ChunkerPage(p, lambda: actions.chunker_choose_folder(self), lambda: actions.chunker_preview(self), lambda: actions.chunker_apply(self))
    def _build_page_flattener(self, p): return FlattenerPage(p, lambda: actions.flattener_choose_folder(self), lambda: actions.flattener_preview(self), lambda: actions.flattener_apply(self))
    def _build_page_unzipper(self, p): return UnzipperPage(p, lambda: actions.unzipper_choose_folder(self), lambda: actions.unzipper_refresh(self), lambda ps: actions.unzipper_extract_selected(self, ps))
    def _build_page_pdf(self, p): return PdfPage(p, lambda: actions.pdf_choose_folder(self), lambda: actions.pdf_refresh(self), lambda ps: actions.pdf_convert_selected(self, ps))
    def _build_page_dateorg(self, p): return DateOrgPage(p, lambda: actions.dateorg_choose_folder(self), lambda: actions.dateorg_preview(self), lambda: actions.dateorg_apply(self))
    def _build_page_empty_folders(self, p): return EmptyFoldersPage(p, lambda: actions.empty_folders_choose_folder(self), lambda: actions.empty_folders_refresh(self), lambda ps: actions.empty_folders_delete_selected(self, ps))
    def _build_page_large_files(self, p): return LargeFilesPage(p, lambda: actions.large_files_choose_folder(self), lambda m: actions.large_files_refresh(self, m), lambda ps: actions.large_files_delete_selected(self, ps))
    def _build_page_settings(self, p): return SettingsPage(p, self.settings, lambda: actions.settings_save(self))
    def _build_page_about(self, p): return AboutPage(p, get_project_info(), lambda u: actions.open_github(self, u))

    def log(self, s, level="INFO"):
        if hasattr(self, "logs_view"): self.logs_view.log(s, level=level)

    def toggle_sidebar(self): pass