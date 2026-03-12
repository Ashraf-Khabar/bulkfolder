from __future__ import annotations
import sys
import customtkinter as ctk

from pathlib import Path
from PIL import Image, ImageTk, ImageDraw

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
    """
    A temporary loading screen that appears before the main application window is ready.
    """
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
        ctk.CTkLabel(inner, text="Loading...", font=ctk.CTkFont(size=12), text_color=DR_MUTED).pack(pady=(0, 5))

        self.pb = ctk.CTkProgressBar(inner, width=220, progress_color=DR_PURPLE, fg_color=DR_BORDER)
        self.pb.pack(pady=(5, 0))
        self.pb.set(0)
        self.pb.start()


class App(ctk.CTk):
    """
    The main application window.
    """
    def __init__(self):
        super().__init__()
        self.withdraw()
        
        self.settings: AppSettings = load_settings()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        try:
            scale_val = float(self.settings.ui_scaling.replace("%", "")) / 100.0
            ctk.set_widget_scaling(scale_val)
            ctk.set_window_scaling(scale_val)
        except Exception:
            pass

        self.title("BulkFolder")
        self.geometry("1200x720")
        self.minsize(1020, 640)
        self.configure(fg_color=DR_BG)

        self.logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logo.png"
        self._ensure_logo_exists(self.logo_path)

        if self.logo_path.exists():
            img = Image.open(self.logo_path)
            photo = ImageTk.PhotoImage(img)
            self.wm_iconphoto(True, photo)
            self.iconphoto(True, photo)
            
            if sys.platform.startswith("win"):
                try:
                    import ctypes
                    myappid = 'monprojet.bulkfolder.app.1.1'
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                except Exception:
                    pass

                ico_path = self.logo_path.with_suffix(".ico")
                try:
                    img.save(ico_path, format="ICO", sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)])
                except Exception:
                    pass

                if ico_path.exists():
                    self.iconbitmap(str(ico_path))

        self.splash = SplashScreen(self, self.logo_path)
        self.splash.update()

        self.ui_state = UIState()
        self.last_plan = None
        self.last_scan = None
        self.large_files_scan = None
        self.renamer_plan = []  
        self.chunker_plan = []
        self.flattener_plan = []
        self.dateorg_plan = [] 

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        info = get_project_info()
        self.sidebar_view = SidebarView(info, self, on_page=self.switch_page, logo_path=self.logo_path)
        self.sidebar_view.grid(row=0, column=0, sticky="nsw")

        self.main = ctk.CTkFrame(self, corner_radius=0, fg_color=DR_BG)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        # Removed on_toggle_sidebar callback as it's no longer needed
        self.topbar_view = TopbarView(self.main, on_toggle_sidebar=None)
        self.topbar_view.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))

        self.page_container = ctk.CTkFrame(self.main, corner_radius=0, fg_color=DR_BG)
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

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
        start_page = self.settings.default_page
        if start_page not in self.pages:
            start_page = "Organizer"
        self.switch_page(start_page)

        self.log("App started.", level="DEBUG")
        self.set_status("Ready.")
        
        self.after(2500, self._show_main_window)

    @staticmethod
    def _ensure_logo_exists(png_path: Path):
        """Generates a dummy placeholder logo if the user hasn't provided one."""
        ico_path = png_path.with_suffix(".ico")
        if png_path.exists() and ico_path.exists(): return
        try:
            size = 256
            img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            bg_color, folder_back, folder_front = (40, 42, 54, 255), (98, 114, 164, 255), (189, 147, 249, 255)
            draw.ellipse([(10, 10), (246, 246)], fill=bg_color)
            draw.rounded_rectangle([(64, 70), (130, 110)], radius=8, fill=folder_back)
            draw.rounded_rectangle([(64, 90), (192, 180)], radius=12, fill=folder_back)
            draw.rounded_rectangle([(48, 110), (208, 190)], radius=12, fill=folder_front)
            png_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(png_path, format="PNG")
            img.save(ico_path, format="ICO")
        except Exception: pass

    def _show_main_window(self):
        try:
            self.splash.pb.stop()
            self.splash.destroy()
        except: pass
        self.deiconify()

    def _build_page_organizer(self, parent) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, corner_radius=0, fg_color=DR_BG)
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        self.organizer_panel = OrganizerPanel(
            frame,
            on_choose_folder=lambda: actions.choose_folder(self),
            on_scan=lambda: actions.scan_and_plan(self),
            on_find_duplicates=lambda: actions.find_duplicates_action(self),
            on_apply=lambda: actions.apply_plan(self),
            on_undo=lambda: actions.undo_last_ops(self),
            on_toggle_subfolders=lambda enabled: actions.toggle_subfolders(self, enabled),
            on_toggle_move_by_ext=lambda enabled: actions.toggle_move_by_ext(self, enabled),
        )
        self.organizer_panel.grid(row=0, column=0, sticky="ns", padx=(18, 10), pady=(0, 18))
        self.organizer_panel.configure(width=320)

        right = ctk.CTkFrame(frame, corner_radius=0, fg_color=DR_BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 18), pady=(0, 18))
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=1)

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

    def _build_page_renamer(self, parent) -> ctk.CTkFrame:
        self.renamer_page = RenamerPage(
            parent,
            on_choose_folder=lambda: actions.renamer_choose_folder(self),
            on_preview=lambda: actions.renamer_preview(self),
            on_apply=lambda: actions.renamer_apply(self),
        )
        return self.renamer_page

    def _build_page_chunker(self, parent) -> ctk.CTkFrame:
        self.chunker_page = ChunkerPage(
            parent,
            on_choose_folder=lambda: actions.chunker_choose_folder(self),
            on_preview=lambda: actions.chunker_preview(self),
            on_apply=lambda: actions.chunker_apply(self),
        )
        return self.chunker_page

    def _build_page_flattener(self, parent) -> ctk.CTkFrame:
        self.flattener_page = FlattenerPage(
            parent,
            on_choose_folder=lambda: actions.flattener_choose_folder(self),
            on_preview=lambda: actions.flattener_preview(self),
            on_apply=lambda: actions.flattener_apply(self),
        )
        return self.flattener_page

    def _build_page_unzipper(self, parent) -> ctk.CTkFrame:
        self.unzipper_page = UnzipperPage(
            parent,
            on_choose_folder=lambda: actions.unzipper_choose_folder(self),
            on_refresh=lambda: actions.unzipper_refresh(self),
            on_extract_selected=lambda paths: actions.unzipper_extract_selected(self, paths),
        )
        return self.unzipper_page

    def _build_page_pdf(self, parent) -> ctk.CTkFrame:
        self.pdf_page = PdfPage(
            parent,
            on_choose_folder=lambda: actions.pdf_choose_folder(self),
            on_refresh=lambda: actions.pdf_refresh(self),
            on_convert=lambda paths: actions.pdf_convert_selected(self, paths),
        )
        return self.pdf_page

    def _build_page_dateorg(self, parent) -> ctk.CTkFrame:
        self.dateorg_page = DateOrgPage(
            parent,
            on_choose_folder=lambda: actions.dateorg_choose_folder(self),
            on_preview=lambda: actions.dateorg_preview(self),
            on_apply=lambda: actions.dateorg_apply(self),
        )
        return self.dateorg_page

    def _build_page_empty_folders(self, parent) -> ctk.CTkFrame:
        self.empty_folders_page = EmptyFoldersPage(
            parent,
            on_choose_folder=lambda: actions.empty_folders_choose_folder(self),
            on_refresh=lambda: actions.empty_folders_refresh(self),
            on_delete_selected=lambda paths: actions.empty_folders_delete_selected(self, paths),
        )
        return self.empty_folders_page

    def _build_page_large_files(self, parent) -> ctk.CTkFrame:
        self.large_files_page = LargeFilesPage(
            parent,
            on_choose_folder=lambda: actions.large_files_choose_folder(self),
            on_refresh=lambda min_mb: actions.large_files_refresh(self, min_mb),
            on_delete_selected=lambda paths: actions.large_files_delete_selected(self, paths),
        )
        return self.large_files_page

    def _build_page_settings(self, parent) -> ctk.CTkFrame:
        self.settings_page = SettingsPage(parent, settings=self.settings, on_save=lambda: actions.settings_save(self))
        return self.settings_page

    def _build_page_about(self, parent) -> ctk.CTkFrame:
        info = get_project_info()
        self.about_page = AboutPage(
            parent,
            project_info=info,
            on_open_github=lambda url: actions.open_github(self, url)
        )
        return self.about_page

    def switch_page(self, page_name: str) -> None:
        if page_name not in self.pages: return
        if self._current_page: self.pages[self._current_page].grid_forget()
        self.pages[page_name].grid(row=0, column=0, sticky="nsew")
        self._current_page = page_name
        self.topbar_view.set_title(page_name if page_name != "Organizer" else "Organizer")

    def toggle_sidebar(self) -> None:
        """Disabled."""
        pass

    def set_status(self, s: str) -> None:
        self.topbar_view.set_status(s)

    def log(self, s: str, level: str = "INFO") -> None:
        if hasattr(self, "logs_view"): self.logs_view.log(s, level=level)

    @staticmethod
    def human_bytes(n: int) -> str:
        step = 1024.0
        for u in ["B", "KB", "MB", "GB", "TB"]:
            if n < step: return f"{n:.1f} {u}"
            n /= step
        return f"{n:.1f} PB"