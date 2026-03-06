from __future__ import annotations

import customtkinter as ctk
from ..theme import DR_PANEL, DR_TEXT, DR_MUTED, DR_BORDER, DR_SURFACE


class SidebarView(ctk.CTkFrame):
    def __init__(self, master, on_page):
        super().__init__(master, corner_radius=0, fg_color=DR_PANEL)

        self._on_page = on_page
        self._expanded = True
        self._expanded_width = 280
        self._collapsed_width = 74
        self.configure(width=self._expanded_width)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(99, weight=1)

        self.title = ctk.CTkLabel(self, text="BulkFolder", font=ctk.CTkFont(size=20, weight="bold"), text_color=DR_TEXT)
        self.title.grid(row=0, column=0, sticky="w", padx=16, pady=(18, 6))

        self.subtitle = ctk.CTkLabel(self, text="Organize & Rename safely", font=ctk.CTkFont(size=12), text_color=DR_MUTED)
        self.subtitle.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 14))

        self.pages_lbl = ctk.CTkLabel(self, text="Pages", font=ctk.CTkFont(size=13, weight="bold"), text_color=DR_TEXT)
        self.pages_lbl.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 10))

        self.pages_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pages_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 12))
        self.pages_frame.grid_columnconfigure(0, weight=1)

        self._pages = [
            ("Organizer", "Organizer", "🏠"),
            ("Presets", "Presets", "⭐"),
            ("Large files", "LargeFiles", "📦"),
            ("Settings", "Settings", "⚙"),
            ("About", "About", "ℹ"),
        ]

        self._page_buttons: list[ctk.CTkButton] = []
        for idx, (label, page_name, icon) in enumerate(self._pages):
            btn = ctk.CTkButton(
                self.pages_frame,
                text=label,
                command=lambda p=page_name: self._on_page(p),
                fg_color=DR_SURFACE,
                hover_color=DR_BORDER,
                text_color=DR_TEXT,
                border_color=DR_BORDER,
                border_width=1,
            )
            btn.grid(row=idx, column=0, sticky="ew", pady=(0, 8 if idx < len(self._pages) - 1 else 0))
            self._page_buttons.append(btn)

        self._collapse_hide = [self.subtitle, self.pages_lbl]

    def toggle(self) -> None:
        self.set_collapsed(self._expanded)

    def set_collapsed(self, collapsed: bool) -> None:
        self._expanded = not collapsed

        if collapsed:
            self.configure(width=self._collapsed_width)
            self.title.configure(text="BF")

            for w in self._collapse_hide:
                try:
                    w.grid_remove()
                except Exception:
                    pass

            for btn, (_, _, icon) in zip(self._page_buttons, self._pages):
                btn.configure(text=icon, width=52)

            self.pages_frame.grid_configure(padx=10)
        else:
            self.configure(width=self._expanded_width)
            self.title.configure(text="BulkFolder")

            for w in self._collapse_hide:
                try:
                    w.grid()
                except Exception:
                    pass

            for btn, (label, _, _) in zip(self._page_buttons, self._pages):
                btn.configure(text=label, width=0)

            self.pages_frame.grid_configure(padx=10)