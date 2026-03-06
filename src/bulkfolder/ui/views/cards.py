from __future__ import annotations
import customtkinter as ctk
from ..theme import DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED

class StatCard(ctk.CTkFrame):
    def __init__(self, master, title: str, value: str = "—"):
        super().__init__(master, corner_radius=16, fg_color=DR_SURFACE, border_color=DR_BORDER, border_width=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color=DR_MUTED)
        self.title_lbl.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 2))

        self.value_lbl = ctk.CTkLabel(self, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color=DR_TEXT)
        self.value_lbl.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 12))

    def set_value(self, v: str) -> None:
        self.value_lbl.configure(text=v)

class CardsRow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)

        self.card_scanned = StatCard(self, "Files scanned")
        self.card_planned = StatCard(self, "Planned actions")
        self.card_conflicts = StatCard(self, "Conflicts")
        self.card_size = StatCard(self, "Total size")

        self.card_scanned.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.card_planned.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.card_conflicts.grid(row=0, column=2, sticky="ew", padx=(0, 10))
        self.card_size.grid(row=0, column=3, sticky="ew")

    def set_values(self, scanned: str, planned: str, conflicts: str, total_size: str) -> None:
        self.card_scanned.set_value(scanned)
        self.card_planned.set_value(planned)
        self.card_conflicts.set_value(conflicts)
        self.card_size.set_value(total_size)