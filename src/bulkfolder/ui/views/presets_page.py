from __future__ import annotations

import customtkinter as ctk

from ...presets import load_presets
from ..theme import DR_BG, DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED, DR_ACCENT, DR_ACCENT_HOVER, DR_PURPLE


class PresetsPage(ctk.CTkFrame):
    def __init__(self, master, on_refresh, on_apply, on_save, on_delete):
        super().__init__(master, corner_radius=0, fg_color=DR_BG)

        self._on_refresh = on_refresh
        self._on_apply = on_apply
        self._on_save = on_save
        self._on_delete = on_delete

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Presets", font=ctk.CTkFont(size=20, weight="bold"), text_color=DR_TEXT).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(header, text="Save and reuse your rules", font=ctk.CTkFont(size=12), text_color=DR_MUTED).grid(
            row=1, column=0, sticky="w", pady=(6, 0)
        )

        self.card = ctk.CTkFrame(self, corner_radius=16, fg_color=DR_SURFACE, border_color=DR_BORDER, border_width=1)
        self.card.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_rowconfigure(3, weight=1)

        # chooser row
        row = ctk.CTkFrame(self.card, fg_color="transparent")
        row.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row, text="Preset", text_color=DR_MUTED).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.preset_var = ctk.StringVar(value="")
        self.preset_menu = ctk.CTkOptionMenu(row, values=[""], variable=self.preset_var)
        self.preset_menu.grid(row=0, column=1, sticky="ew")

        # smaller button
        self.btn_refresh = ctk.CTkButton(
            row,
            text="Refresh",
            command=self._on_refresh,
            fg_color=DR_SURFACE,
            hover_color=DR_BORDER,
            text_color=DR_TEXT,
            border_color=DR_BORDER,
            border_width=1,
            width=110,
            height=32,
        )
        self.btn_refresh.grid(row=0, column=2, sticky="e", padx=(10, 0))

        # buttons row (NOT stretched)
        row2 = ctk.CTkFrame(self.card, fg_color="transparent")
        row2.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 10))

        self.btn_apply = ctk.CTkButton(
            row2,
            text="Apply",
            command=self._on_apply,
            fg_color=DR_ACCENT,
            hover_color=DR_ACCENT_HOVER,
            text_color=DR_TEXT,
            width=120,
            height=32,
        )
        self.btn_apply.pack(side="left", padx=(0, 8))

        self.btn_delete = ctk.CTkButton(
            row2,
            text="Delete",
            command=self._on_delete,
            fg_color=DR_SURFACE,
            hover_color=DR_BORDER,
            text_color=DR_TEXT,
            border_color=DR_BORDER,
            border_width=1,
            width=120,
            height=32,
        )
        self.btn_delete.pack(side="left", padx=(0, 8))

        self.btn_save = ctk.CTkButton(
            row2,
            text="Save current",
            command=self._on_save,
            fg_color=DR_PURPLE,
            hover_color=DR_PURPLE,
            text_color=DR_TEXT,
            width=140,
            height=32,
        )
        self.btn_save.pack(side="left")

        # details box (read-only + console font + colors)
        self.details = ctk.CTkTextbox(self.card, fg_color=DR_SURFACE, border_color=DR_BORDER, text_color=DR_TEXT, corner_radius=12)
        self.details.grid(row=3, column=0, sticky="nsew", padx=16, pady=(0, 16))

        try:
            self.details.configure(font=("Cascadia Mono", 13))
        except Exception:
            self.details.configure(font=("Consolas", 13))

        self._text = self.details._textbox
        self._text.tag_configure("KEY", foreground="#bd93f9")     # purple
        self._text.tag_configure("VAL", foreground=DR_TEXT)
        self._text.tag_configure("MUTED", foreground=DR_MUTED)

        self._set_read_only(True)

        # update details when user changes selection
        self.preset_var.trace_add("write", lambda *_: self._render_details())

        self.refresh()

    def _set_read_only(self, ro: bool) -> None:
        self.details.configure(state="disabled" if ro else "normal")

    def refresh(self) -> None:
        presets = load_presets()
        names = [p.name for p in presets] or [""]
        current = self.preset_var.get()
        self.preset_menu.configure(values=names)

        if current not in names:
            self.preset_var.set(names[0])

        self._render_details()

    def _render_details(self) -> None:
        name = self.preset_var.get().strip()
        presets = {p.name: p for p in load_presets()}
        p = presets.get(name)

        self.details.configure(state="normal")
        self.details.delete("1.0", "end")

        if not p:
            self._text.insert("end", "No preset selected.\n", "MUTED")
            self.details.configure(state="disabled")
            return

        def line(k: str, v: str):
            self._text.insert("end", f"{k}: ", "KEY")
            self._text.insert("end", f"{v}\n", "VAL")

        line("Name", p.name)
        line("Include subfolders", str(p.include_subfolders))
        line("Move by extension", str(p.move_by_extension))
        line("Find text", p.find_text or "—")
        line("Replace with", p.replace_text or "—")

        self.details.configure(state="disabled")

    def get_selected_name(self) -> str:
        return self.preset_var.get().strip()