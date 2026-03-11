from __future__ import annotations
import customtkinter as ctk
from ..theme import DR_SURFACE, DR_BORDER, DR_TEXT

class TopbarView(ctk.CTkFrame):
    def __init__(self, master, on_toggle_sidebar=None):
        super().__init__(
            master,
            corner_radius=16,
            fg_color=DR_SURFACE,
            border_color=DR_BORDER,
            border_width=1,
        )
        self.grid_columnconfigure(1, weight=1)

        # Page Title
        self.h1 = ctk.CTkLabel(
            self,
            text="Organizer",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=DR_TEXT,
        )
        self.h1.grid(row=0, column=0, sticky="w", padx=20, pady=14)

    def set_title(self, title: str) -> None:
        self.h1.configure(text=title)

    def set_status(self, s: str) -> None:
        """ Method kept for compatibility, status labels are now in tooltips """
        pass