from __future__ import annotations

import customtkinter as ctk
from ..theme import DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED


class DuplicatesView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Duplicate files",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=DR_TEXT,
        ).grid(row=0, column=0, sticky="w")

        self.sub = ctk.CTkLabel(
            header,
            text="Same content (SHA-256), grouped",
            font=ctk.CTkFont(size=11),
            text_color=DR_MUTED,
        )
        self.sub.grid(row=0, column=1, sticky="e")

        self.box = ctk.CTkTextbox(
            self,
            fg_color=DR_SURFACE,
            border_color=DR_BORDER,
            text_color=DR_TEXT,
            corner_radius=12
        )
        self.box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Console font bigger
        try:
            self.box.configure(font=("Cascadia Mono", 13))
        except Exception:
            self.box.configure(font=("Consolas", 13))

        self._text = self.box._textbox
        self._text.tag_configure("GROUP", foreground="#bd93f9")  # purple
        self._text.tag_configure("PATH", foreground=DR_TEXT)
        self._text.tag_configure("MUTED", foreground=DR_MUTED)

        self._set_read_only(True)

    def _set_read_only(self, ro: bool) -> None:
        self.box.configure(state="disabled" if ro else "normal")

    def render(self, groups: list[list[str]]) -> None:
        self.box.configure(state="normal")
        self.box.delete("1.0", "end")

        if not groups:
            self.sub.configure(text="No duplicates found")
            self._text.insert("end", "No duplicates found.\n", "MUTED")
            self.box.configure(state="disabled")
            return

        self.sub.configure(text=f"{len(groups)} duplicate group(s) found")

        for i, group in enumerate(groups, start=1):
            self._text.insert("end", f"Group {i} ({len(group)} files)\n", "GROUP")
            for p in group:
                self._text.insert("end", f"  • {p}\n", "PATH")
            self._text.insert("end", "\n", "MUTED")

        self.box.configure(state="disabled")