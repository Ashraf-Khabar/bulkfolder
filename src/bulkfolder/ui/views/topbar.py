from __future__ import annotations
import customtkinter as ctk
from ..theme import DR_TEXT, DR_MUTED, DR_BORDER, DR_SURFACE

class TopbarView(ctk.CTkFrame):
    """
    The TopbarView displays the current page title and application status.
    Menu button removed since sidebar is fixed.
    """
    def __init__(self, master, on_toggle_sidebar=None):
        super().__init__(master, fg_color="transparent")
        
        self.grid_columnconfigure(1, weight=1)

        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid(row=0, column=1, sticky="w")

        self.title_label = ctk.CTkLabel(
            self.info_frame, 
            text="Dashboard", 
            font=ctk.CTkFont(size=22, weight="bold"), 
            text_color=DR_TEXT
        )
        self.title_label.pack(side="top", anchor="w")

        self.status_label = ctk.CTkLabel(
            self.info_frame, 
            text="Ready to organize", 
            font=ctk.CTkFont(size=13), 
            text_color=DR_MUTED
        )
        self.status_label.pack(side="top", anchor="w")

    def set_title(self, title: str) -> None:
        self.title_label.configure(text=title)

    def set_status(self, status: str) -> None:
        self.status_label.configure(text=status)