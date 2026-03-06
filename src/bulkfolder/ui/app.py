from __future__ import annotations
import customtkinter as ctk

from .theme import DR_BG, DR_TEXT, DR_MUTED, DR_SURFACE, DR_BORDER
from .state import UIState
from . import actions

from ..config import load_settings, AppSettings

from .views.sidebar import SidebarView
from .views.topbar import TopbarView
from .views.cards import CardsRow
from .views.dashboard import DashboardView
from .views.preview import PreviewView
from .views.logs import LogsView
from .views.duplicates import DuplicatesView
from .views.organizer_panel import OrganizerPanel
from .views.presets_page import PresetsPage
from .views.settings_page import SettingsPage


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load settings early
        self.settings: AppSettings = load_settings()

        # Apply appearance
        mode = (self.settings.appearance_mode or "dark").lower()
        if mode not in {"dark", "light", "system"}:
            mode = "dark"
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")

        self.title("BulkFolder")
        self.geometry("1200x720")
        self.minsize(1020, 640)
        self.configure(fg_color=DR_BG)

        self.ui_state = UIState()
        self.last_plan = None
        self.last_scan = None

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar = Pages only
        self.sidebar_view = SidebarView(self, on_page=self.switch_page)
        self.sidebar_view.grid(row=0, column=0, sticky="nsw")

        # Main
        self.main = ctk.CTkFrame(self, corner_radius=0, fg_color=DR_BG)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        self.topbar_view = TopbarView(
            self.main,
            on_toggle_theme=self.toggle_theme,
            on_toggle_sidebar=self.toggle_sidebar,
        )
        self.topbar_view.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))

        # Container for pages
        self.page_container = ctk.CTkFrame(self.main, corner_radius=0, fg_color=DR_BG)
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        self.pages: dict[str, ctk.CTkFrame] = {}

        self.pages["Organizer"] = self._build_page_organizer(self.page_container)
        self.pages["Presets"] = self._build_page_presets(self.page_container)
        self.pages["LargeFiles"] = self._build_page_placeholder(self.page_container, "Large files", "Coming soon: find + move big files.")
        self.pages["Settings"] = self._build_page_settings(self.page_container)
        self.pages["About"] = self._build_page_placeholder(self.page_container, "About", "BulkFolder — your safe bulk organizer.")

        self._current_page = ""

        # start page from settings
        start_page = self.settings.default_page if self.settings.default_page in self.pages else "Organizer"
        self.switch_page(start_page)

        self.log("App started.", level="DEBUG")
        self.set_status("Ready.")

    # -------------------------
    # Page builders
    # -------------------------
    def _build_page_organizer(self, parent) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, corner_radius=0, fg_color=DR_BG)
        frame.grid_columnconfigure(0, weight=0)   # left panel
        frame.grid_columnconfigure(1, weight=1)   # main content
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

        tab_dash = self.tabs.add("Dashboard")
        tab_preview = self.tabs.add("Preview")
        tab_dups = self.tabs.add("Duplicates")
        tab_logs = self.tabs.add("Logs")

        self.dashboard_view = DashboardView(tab_dash)
        self.dashboard_view.pack(fill="both", expand=True)

        self.preview_view = PreviewView(tab_preview)
        self.preview_view.pack(fill="both", expand=True)

        self.duplicates_view = DuplicatesView(tab_dups)
        self.duplicates_view.pack(fill="both", expand=True)

        self.logs_view = LogsView(tab_logs)
        self.logs_view.pack(fill="both", expand=True)

        return frame

    def _build_page_presets(self, parent) -> ctk.CTkFrame:
        self.presets_page = PresetsPage(
            parent,
            on_refresh=lambda: actions.presets_refresh(self),
            on_apply=lambda: actions.presets_apply_selected(self),
            on_save=lambda: actions.presets_save_current(self),
            on_delete=lambda: actions.presets_delete_selected(self),
        )
        return self.presets_page

    def _build_page_settings(self, parent) -> ctk.CTkFrame:
        self.settings_page = SettingsPage(
            parent,
            settings=self.settings,
            on_save=lambda: actions.settings_save(self),
        )
        return self.settings_page

    def _build_page_placeholder(self, parent, title: str, subtitle: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, corner_radius=16, fg_color=DR_SURFACE, border_color=DR_BORDER, border_width=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)

        ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=20, weight="bold"), text_color=DR_TEXT).pack(anchor="w")
        ctk.CTkLabel(inner, text=subtitle, font=ctk.CTkFont(size=12), text_color=DR_MUTED).pack(anchor="w", pady=(8, 0))

        return frame

    # -------------------------
    # Page switching
    # -------------------------
    def switch_page(self, page_name: str) -> None:
        if page_name not in self.pages:
            return

        if self._current_page:
            self.pages[self._current_page].grid_forget()

        page = self.pages[page_name]
        page.grid(row=0, column=0, sticky="nsew")
        self._current_page = page_name

        title = "Organizer" if page_name == "Organizer" else page_name
        self.topbar_view.set_title(title)

    def toggle_sidebar(self) -> None:
        self.sidebar_view.toggle()

    # -------------------------
    # status / logs
    # -------------------------
    def set_status(self, s: str) -> None:
        self.topbar_view.set_status(s)

    def log(self, s: str, level: str = "INFO") -> None:
        if hasattr(self, "logs_view"):
            self.logs_view.log(s, level=level)

    # -------------------------
    # theme (quick toggle)
    # -------------------------
    def toggle_theme(self) -> None:
        current = ctk.get_appearance_mode().lower()
        ctk.set_appearance_mode("light" if current == "dark" else "dark")

    @staticmethod
    def human_bytes(n: int) -> str:
        step = 1024.0
        units = ["B", "KB", "MB", "GB", "TB"]
        v = float(n)
        for u in units:
            if v < step:
                return f"{v:.1f} {u}"
            v /= step
        return f"{v:.1f} PB"