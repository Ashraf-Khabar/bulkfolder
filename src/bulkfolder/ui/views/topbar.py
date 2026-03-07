from __future__ import annotations
import customtkinter as ctk
from ..theme import DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED


class TopbarView(ctk.CTkFrame):
    # Suppression de on_toggle_theme des arguments
    def __init__(self, master, on_toggle_sidebar):
        super().__init__(
            master,
            corner_radius=16,
            fg_color=DR_SURFACE,
            border_color=DR_BORDER,
            border_width=1,
        )
        self.grid_columnconfigure(2, weight=1)

        self.sidebar_btn = ctk.CTkButton(
            self,
            text="☰",
            width=44,
            command=on_toggle_sidebar,
            fg_color=DR_SURFACE,
            hover_color=DR_BORDER,
            text_color=DR_TEXT,
            border_color=DR_BORDER,
            border_width=1,
        )
        self.sidebar_btn.grid(row=0, column=0, sticky="w", padx=(12, 8), pady=12)

        self.h1 = ctk.CTkLabel(
            self,
            text="Organizer",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=DR_TEXT,
        )
        self.h1.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=14)

        self.status_lbl = ctk.CTkLabel(self, text="—", text_color=DR_MUTED)
        self.status_lbl.grid(row=0, column=2, sticky="w", padx=10, pady=14)

        # Le bouton de changement de thème a été supprimé d'ici

    def set_status(self, s: str) -> None:
        self.status_lbl.configure(text=s)

    def set_title(self, title: str) -> None:
        self.h1.configure(text=title)