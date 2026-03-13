from __future__ import annotations
import customtkinter as ctk
from ..theme import DR_TEXT, DR_MUTED, DR_PURPLE, DR_BG, DR_SURFACE, DR_BORDER

class TopbarView(ctk.CTkFrame):
    """
    Top bar containing the page title, status indicator, and terminal toggle.
    """
    def __init__(self, master, on_toggle_sidebar=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_toggle_sidebar = on_toggle_sidebar

        # Left: Page Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="Dashboard", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=DR_TEXT
        )
        self.title_label.pack(side="left")

        # Right Area
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.pack(side="right", fill="y")

        # Terminal Toggle Button
        self.term_btn = ctk.CTkButton(
            self.right_container,
            text=">_ Terminal",
            width=100,
            height=32,
            fg_color=DR_SURFACE,
            hover_color=DR_BORDER,
            text_color=DR_PURPLE,
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            command=self.on_toggle_sidebar # Link to the toggle function
        )
        self.term_btn.pack(side="right", padx=(15, 0))

        # Status Indicator
        self.status_label = ctk.CTkLabel(
            self.right_container,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color=DR_MUTED
        )
        self.status_label.pack(side="right", padx=10)

    def set_title(self, title: str) -> None:
        """Updates the main page title."""
        self.title_label.configure(text=title)

    def set_status(self, status: str) -> None:
        """Updates the status message."""
        self.status_label.configure(text=status)