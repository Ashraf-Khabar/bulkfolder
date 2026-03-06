from __future__ import annotations

import customtkinter as ctk
from ..theme import DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED


class PreviewView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.box = ctk.CTkTextbox(
            self,
            fg_color=DR_SURFACE,
            border_color=DR_BORDER,
            text_color=DR_TEXT,
            corner_radius=12
        )
        self.box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Console font bigger
        try:
            self.box.configure(font=("Cascadia Mono", 13))
        except Exception:
            self.box.configure(font=("Consolas", 13))

        self._text = self.box._textbox

        # Tags colors
        self._text.tag_configure("MOVE", foreground="#50fa7b")       # green
        self._text.tag_configure("RENAME", foreground="#8be9fd")     # cyan
        self._text.tag_configure("SKIP", foreground=DR_MUTED)        # muted
        self._text.tag_configure("CONFLICT", foreground="#ff5555")   # red
        self._text.tag_configure("PATH", foreground=DR_TEXT)

        self._set_read_only(True)

    def _set_read_only(self, ro: bool) -> None:
        self.box.configure(state="disabled" if ro else "normal")

    def render(self, plan) -> None:
        """
        plan.items expected
        Each item may have:
          - action (Enum or str) -> action.value or str(action)
          - src or src_path
          - dst or dst_path
          - conflict (bool)
          - conflict_reason (str) optional
        """
        items = getattr(plan, "items", []) or []

        self.box.configure(state="normal")
        self.box.delete("1.0", "end")

        if not items:
            self._text.insert("end", "No planned operations.\n", "SKIP")
            self.box.configure(state="disabled")
            return

        for it in items:
            action = getattr(it, "action", "skip")
            if hasattr(action, "value"):
                action = action.value
            action = str(action).lower()

            src = getattr(it, "src", None) or getattr(it, "src_path", None) or getattr(it, "source", "")
            dst = getattr(it, "dst", None) or getattr(it, "dst_path", None) or getattr(it, "target", "")

            conflict = bool(getattr(it, "conflict", False))
            reason = str(getattr(it, "conflict_reason", "") or "")

            if conflict:
                self._text.insert("end", "[CONFLICT] ", "CONFLICT")
                self._text.insert("end", f"{src} -> {dst}\n", "PATH")
                if reason:
                    self._text.insert("end", f"  reason: {reason}\n", "CONFLICT")
                continue

            if action == "move":
                self._text.insert("end", "[MOVE] ", "MOVE")
                self._text.insert("end", f"{src} -> {dst}\n", "PATH")
            elif action == "rename":
                self._text.insert("end", "[RENAME] ", "RENAME")
                self._text.insert("end", f"{src} -> {dst}\n", "PATH")
            elif action == "skip":
                self._text.insert("end", "[SKIP] ", "SKIP")
                self._text.insert("end", f"{src}\n", "PATH")
            else:
                self._text.insert("end", f"[{action.upper()}] ", "INFO")
                self._text.insert("end", f"{src} -> {dst}\n", "PATH")

        self.box.configure(state="disabled")