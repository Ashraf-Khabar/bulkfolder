from __future__ import annotations

import customtkinter as ctk
from ..theme import DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED


class LogsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.box = ctk.CTkTextbox(
            self,
            fg_color=DR_SURFACE,
            border_color=DR_BORDER,
            text_color=DR_TEXT,
            corner_radius=12,
        )
        self.box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Bigger monospace font
        self._set_console_font(self.box, size=13)

        # Underlying tk.Text for tags
        self._text = self.box._textbox

        # Sophisticated colors
        self._text.tag_configure("DEBUG", foreground=DR_MUTED)
        self._text.tag_configure("INFO", foreground=DR_TEXT)
        self._text.tag_configure("WARN", foreground="#f1fa8c")
        self._text.tag_configure("ERROR", foreground="#ff5555")
        self._text.tag_configure("SUCCESS", foreground="#50fa7b")

        self.set_read_only(True)

    @staticmethod
    def _set_console_font(widget: ctk.CTkTextbox, size: int = 13) -> None:
        try:
            widget.configure(font=("Cascadia Mono", size))
        except Exception:
            widget.configure(font=("Consolas", size))

    def set_read_only(self, read_only: bool) -> None:
        self.box.configure(state="disabled" if read_only else "normal")

    def clear(self) -> None:
        self.box.configure(state="normal")
        self.box.delete("1.0", "end")
        self.box.configure(state="disabled")

    def log(self, message: str, level: str = "INFO") -> None:
        level = (level or "INFO").upper()
        if level not in {"INFO", "DEBUG", "WARN", "ERROR", "SUCCESS"}:
            level = "INFO"

        self.box.configure(state="normal")
        self._text.insert("end", f"[{level}] ", level)
        self._text.insert("end", message + "\n", level)
        self._text.see("end")
        self.box.configure(state="disabled")