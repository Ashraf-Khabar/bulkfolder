from __future__ import annotations

import customtkinter as ctk

from ...config import AppSettings
from ..theme import DR_BG, DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED, DR_ACCENT, DR_ACCENT_HOVER


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, settings: AppSettings, on_save):
        super().__init__(master, corner_radius=0, fg_color=DR_BG)

        self._on_save = on_save
        self._current_settings = settings

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # En-tête
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Paramètres", font=ctk.CTkFont(size=20, weight="bold"), text_color=DR_TEXT).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(header, text="Préférences de l'application", font=ctk.CTkFont(size=12), text_color=DR_MUTED).grid(
            row=1, column=0, sticky="w", pady=(6, 0)
        )

        # Conteneur principal avec ascenseur (si vous ajoutez beaucoup de sections à l'avenir)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll.grid_columnconfigure(0, weight=1)

        # --- SECTION 1 : GÉNÉRAL ---
        self._build_section_title(self.scroll, "Général", row=0)
        card_general = ctk.CTkFrame(self.scroll, corner_radius=16, fg_color=DR_SURFACE, border_color=DR_BORDER, border_width=1)
        card_general.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 18))
        card_general.grid_columnconfigure(0, weight=1)

        # Default page
        row_page = ctk.CTkFrame(card_general, fg_color="transparent")
        row_page.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        row_page.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row_page, text="Page de démarrage par défaut", text_color=DR_MUTED).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.default_page_var = ctk.StringVar(value=settings.default_page)
        self.default_page_menu = ctk.CTkOptionMenu(
            row_page,
            values=["Organizer", "Presets", "LargeFiles", "Settings", "About"],
            variable=self.default_page_var
        )
        self.default_page_menu.grid(row=0, column=1, sticky="w")

        # Autoscan
        self.autoscan_var = ctk.BooleanVar(value=settings.autoscan_on_folder_select)
        self.autoscan_sw = ctk.CTkSwitch(card_general, text="Scanner automatiquement lors de la sélection d'un dossier", variable=self.autoscan_var)
        self.autoscan_sw.grid(row=1, column=0, sticky="w", padx=16, pady=(10, 16))

        # --- SECTION 2 : FICHIERS & DOUBLONS ---
        self._build_section_title(self.scroll, "Fichiers & Doublons", row=2)
        card_files = ctk.CTkFrame(self.scroll, corner_radius=16, fg_color=DR_SURFACE, border_color=DR_BORDER, border_width=1)
        card_files.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 18))
        card_files.grid_columnconfigure(0, weight=1)

        # Duplicate min size
        row_dup = ctk.CTkFrame(card_files, fg_color="transparent")
        row_dup.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 16))
        row_dup.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row_dup, text="Taille minimale des doublons ignorés (KB)", text_color=DR_MUTED).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.min_dup_var = ctk.StringVar(value=str(settings.duplicate_min_size_kb))
        self.min_dup_entry = ctk.CTkEntry(row_dup, textvariable=self.min_dup_var, width=120)
        self.min_dup_entry.grid(row=0, column=1, sticky="w")

        # --- BOUTON DE SAUVEGARDE ---
        btn_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_row.grid(row=4, column=0, sticky="w", padx=8, pady=(10, 16))

        self.btn_save = ctk.CTkButton(
            btn_row,
            text="Sauvegarder les paramètres",
            command=self._on_save,
            fg_color=DR_ACCENT,
            hover_color=DR_ACCENT_HOVER,
            text_color=DR_TEXT,
            width=180,
            height=32,
        )
        self.btn_save.pack(side="left")

    def _build_section_title(self, parent, title: str, row: int):
        lbl = ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color=DR_TEXT)
        lbl.grid(row=row, column=0, sticky="w", padx=12, pady=(10, 8))

    def read_settings_from_form(self) -> AppSettings:
        # On conserve le thème actuel car on ne le modifie plus ici
        mode = self._current_settings.appearance_mode 

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