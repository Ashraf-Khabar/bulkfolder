from __future__ import annotations

import customtkinter as ctk

from ...config import AppSettings
from ..theme import DR_BG, DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED, DR_ACCENT, DR_ACCENT_HOVER


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, settings: AppSettings, on_save):
        super().__init__(master, corner_radius=0, fg_color=DR_BG)

        self._on_save = on_save

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Settings", font=ctk.CTkFont(size=20, weight="bold"), text_color=DR_TEXT).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(header, text="Basic preferences", font=ctk.CTkFont(size=12), text_color=DR_MUTED).grid(
            row=1, column=0, sticky="w", pady=(6, 0)
        )

        self.card = ctk.CTkFrame(self, corner_radius=16, fg_color=DR_SURFACE, border_color=DR_BORDER, border_width=1)
        self.card.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.card.grid_columnconfigure(0, weight=1)

        # Theme
        row1 = ctk.CTkFrame(self.card, fg_color="transparent")
        row1.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        row1.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row1, text="Theme", text_color=DR_MUTED).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.mode_var = ctk.StringVar(value=settings.appearance_mode)
        self.mode_menu = ctk.CTkOptionMenu(row1, values=["dark", "light", "system"], variable=self.mode_var)
        self.mode_menu.grid(row=0, column=1, sticky="w")

        # Autoscan
        self.autoscan_var = ctk.BooleanVar(value=settings.autoscan_on_folder_select)
        self.autoscan_sw = ctk.CTkSwitch(self.card, text="Auto-scan when selecting folder", variable=self.autoscan_var)
        self.autoscan_sw.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 10))

        # Duplicate min size
        row2 = ctk.CTkFrame(self.card, fg_color="transparent")
        row2.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
        row2.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row2, text="Duplicate min size (KB)", text_color=DR_MUTED).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.min_dup_var = ctk.StringVar(value=str(settings.duplicate_min_size_kb))
        self.min_dup_entry = ctk.CTkEntry(row2, textvariable=self.min_dup_var, width=120)
        self.min_dup_entry.grid(row=0, column=1, sticky="w")

        # Default page
        row3 = ctk.CTkFrame(self.card, fg_color="transparent")
        row3.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))
        row3.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row3, text="Default start page", text_color=DR_MUTED).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.default_page_var = ctk.StringVar(value=settings.default_page)
        self.default_page_menu = ctk.CTkOptionMenu(
            row3,
            values=["Organizer", "Presets", "LargeFiles", "Settings", "About"],
            variable=self.default_page_var
        )
        self.default_page_menu.grid(row=0, column=1, sticky="w")

        # small normal save button
        btn_row = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_row.grid(row=4, column=0, sticky="w", padx=16, pady=(0, 16))

        self.btn_save = ctk.CTkButton(
            btn_row,
            text="Save settings",
            command=self._on_save,
            fg_color=DR_ACCENT,
            hover_color=DR_ACCENT_HOVER,
            text_color=DR_TEXT,
            width=160,
            height=32,
        )
        self.btn_save.pack(side="left")

    def read_settings_from_form(self) -> AppSettings:
        mode = (self.mode_var.get() or "dark").lower()
        if mode not in {"dark", "light", "system"}:
            mode = "dark"

        try:
            min_kb = int(self.min_dup_var.get().strip())
        except Exception:
            min_kb = 1
        if min_kb < 0:
            min_kb = 0

        default_page = self.default_page_var.get() or "Organizer"

        return AppSettings(
            appearance_mode=mode,
            autoscan_on_folder_select=bool(self.autoscan_var.get()),
            duplicate_min_size_kb=min_kb,
            default_page=default_page,
        )