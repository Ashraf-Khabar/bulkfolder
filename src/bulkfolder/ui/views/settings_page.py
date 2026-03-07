from __future__ import annotations
import customtkinter as ctk

from ...config import AppSettings
from ..theme import DR_BG, DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED, DR_ACCENT, DR_ACCENT_HOVER, THEMES


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, settings: AppSettings, on_save):
        super().__init__(master, corner_radius=0, fg_color=DR_BG)

        self._on_save = on_save
        self._current_settings = settings

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Settings", font=ctk.CTkFont(size=20, weight="bold"), text_color=DR_TEXT).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Application preferences and behavior", font=ctk.CTkFont(size=12), text_color=DR_MUTED).grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll.grid_columnconfigure(0, weight=1)

        current_row = 0

        # --- SECTION: APPEARANCE ---
        self._build_section_title(self.scroll, "Appearance & Interface", row=current_row)
        current_row += 1
        card_app = ctk.CTkFrame(self.scroll, corner_radius=16, fg_color=DR_SURFACE, border_color=DR_BORDER, border_width=1)
        card_app.grid(row=current_row, column=0, sticky="nsew", padx=8, pady=(0, 18))
        card_app.grid_columnconfigure(1, weight=1)
        current_row += 1

        ctk.CTkLabel(card_app, text="Color Theme", text_color=DR_MUTED).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))
        self.theme_var = ctk.StringVar(value=settings.theme_name)
        # On liste dynamiquement tous les thèmes
        self.theme_menu = ctk.CTkOptionMenu(card_app, values=list(THEMES.keys()), variable=self.theme_var)
        self.theme_menu.grid(row=0, column=1, sticky="w", padx=16, pady=(16, 10))

        ctk.CTkLabel(card_app, text="UI Scaling (Zoom)", text_color=DR_MUTED).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 16))
        self.scaling_var = ctk.StringVar(value=settings.ui_scaling)
        self.scaling_menu = ctk.CTkOptionMenu(card_app, values=["80%", "90%", "100%", "110%", "120%"], variable=self.scaling_var)
        self.scaling_menu.grid(row=1, column=1, sticky="w", padx=16, pady=(0, 16))

        # --- SECTION: BEHAVIOR ---
        self._build_section_title(self.scroll, "Behavior", row=current_row)
        current_row += 1
        card_gen = ctk.CTkFrame(self.scroll, corner_radius=16, fg_color=DR_SURFACE, border_color=DR_BORDER, border_width=1)
        card_gen.grid(row=current_row, column=0, sticky="nsew", padx=8, pady=(0, 18))
        card_gen.grid_columnconfigure(1, weight=1)
        current_row += 1

        ctk.CTkLabel(card_gen, text="Default Startup Page", text_color=DR_MUTED).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))
        self.default_page_var = ctk.StringVar(value=settings.default_page)
        self.default_page_menu = ctk.CTkOptionMenu(card_gen, values=["Organizer", "Renamer", "Flattener", "Unzipper", "PdfConverter", "DateOrg", "EmptyFolders", "LargeFiles"], variable=self.default_page_var)
        self.default_page_menu.grid(row=0, column=1, sticky="w", padx=16, pady=(16, 10))

        self.autoscan_var = ctk.BooleanVar(value=settings.autoscan_on_folder_select)
        self.autoscan_sw = ctk.CTkSwitch(card_gen, text="Automatically scan when selecting a folder", variable=self.autoscan_var)
        self.autoscan_sw.grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 10))

        self.confirm_var = ctk.BooleanVar(value=settings.ask_confirmations)
        self.confirm_sw = ctk.CTkSwitch(card_gen, text="Ask for confirmation before applying irreversible changes", variable=self.confirm_var)
        self.confirm_sw.grid(row=2, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 16))

        # --- SECTION: FILES & DUPLICATES ---
        self._build_section_title(self.scroll, "Files & Duplicates", row=current_row)
        current_row += 1
        card_files = ctk.CTkFrame(self.scroll, corner_radius=16, fg_color=DR_SURFACE, border_color=DR_BORDER, border_width=1)
        card_files.grid(row=current_row, column=0, sticky="nsew", padx=8, pady=(0, 18))
        card_files.grid_columnconfigure(1, weight=1)
        current_row += 1

        ctk.CTkLabel(card_files, text="Ignore duplicates smaller than (KB)", text_color=DR_MUTED).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 16))
        self.min_dup_var = ctk.StringVar(value=str(settings.duplicate_min_size_kb))
        self.min_dup_entry = ctk.CTkEntry(card_files, textvariable=self.min_dup_var, width=120)
        self.min_dup_entry.grid(row=0, column=1, sticky="w", padx=16, pady=(16, 16))

        # --- SAVE BUTTON ---
        btn_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_row.grid(row=current_row, column=0, sticky="w", padx=8, pady=(10, 16))

        self.btn_save = ctk.CTkButton(
            btn_row, text="Save Settings", command=self._on_save,
            fg_color=DR_ACCENT, hover_color=DR_ACCENT_HOVER, text_color=DR_TEXT, width=180, height=32,
        )
        self.btn_save.pack(side="left")

    def _build_section_title(self, parent, title: str, row: int):
        lbl = ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color=DR_TEXT)
        lbl.grid(row=row, column=0, sticky="w", padx=12, pady=(10, 8))

    def read_settings_from_form(self) -> AppSettings:
        try: min_kb = int(self.min_dup_var.get().strip())
        except Exception: min_kb = 1

        return AppSettings(
            theme_name=self.theme_var.get(),
            ui_scaling=self.scaling_var.get(),
            autoscan_on_folder_select=bool(self.autoscan_var.get()),
            ask_confirmations=bool(self.confirm_var.get()),
            duplicate_min_size_kb=max(0, min_kb),
            default_page=self.default_page_var.get() or "Organizer",
        )