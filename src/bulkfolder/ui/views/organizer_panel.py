from __future__ import annotations

import customtkinter as ctk
from ..theme import (
    DR_PANEL, DR_TEXT, DR_MUTED, DR_BORDER,
    DR_ACCENT, DR_ACCENT_HOVER, DR_PURPLE, DR_SURFACE
)


class OrganizerPanel(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_choose_folder,
        on_scan,
        on_find_duplicates,
        on_apply,
        on_undo,
        on_toggle_subfolders,
        on_toggle_move_by_ext,
    ):
        super().__init__(master, corner_radius=16, fg_color=DR_PANEL, border_color=DR_BORDER, border_width=1)

        self._on_toggle_subfolders = on_toggle_subfolders
        self._on_toggle_move_by_ext = on_toggle_move_by_ext

        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Organizer", font=ctk.CTkFont(size=16, weight="bold"), text_color=DR_TEXT)
        title.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))

        sub = ctk.CTkLabel(self, text="Load a folder and organize safely", font=ctk.CTkFont(size=12), text_color=DR_MUTED)
        sub.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

        self.btn_choose = ctk.CTkButton(
            self, text="Choose folder", command=on_choose_folder,
            fg_color=DR_ACCENT, hover_color=DR_ACCENT_HOVER, text_color=DR_TEXT
        )
        self.btn_choose.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))

        self.lbl_path = ctk.CTkLabel(self, text="No folder selected", wraplength=260, justify="left", text_color=DR_MUTED)
        self.lbl_path.grid(row=3, column=0, sticky="w", padx=16, pady=(0, 12))

        self.sw_sub = ctk.CTkSwitch(
            self, text="Include subfolders",
            command=lambda: self._on_toggle_subfolders(bool(self.sw_sub.get())),
            progress_color=DR_PURPLE, button_color=DR_TEXT
        )
        self.sw_sub.select()
        self.sw_sub.grid(row=4, column=0, sticky="w", padx=16, pady=(0, 12))

        sep1 = ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=DR_BORDER)
        sep1.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 12))

        rules_lbl = ctk.CTkLabel(self, text="Rules", font=ctk.CTkFont(size=13, weight="bold"), text_color=DR_TEXT)
        rules_lbl.grid(row=6, column=0, sticky="w", padx=16, pady=(0, 10))

        self.sw_move = ctk.CTkSwitch(
            self, text="Move by extension",
            command=lambda: self._on_toggle_move_by_ext(bool(self.sw_move.get())),
            progress_color=DR_PURPLE, button_color=DR_TEXT
        )
        self.sw_move.select()
        self.sw_move.grid(row=7, column=0, sticky="w", padx=16, pady=(0, 10))

        self.entry_find = ctk.CTkEntry(self, placeholder_text="Find text (optional)",
                                       fg_color=DR_SURFACE, border_color=DR_BORDER, text_color=DR_TEXT)
        self.entry_find.grid(row=8, column=0, sticky="ew", padx=16, pady=(0, 8))

        self.entry_replace = ctk.CTkEntry(self, placeholder_text="Replace with",
                                          fg_color=DR_SURFACE, border_color=DR_BORDER, text_color=DR_TEXT)
        self.entry_replace.grid(row=9, column=0, sticky="ew", padx=16, pady=(0, 12))

        self.btn_scan = ctk.CTkButton(
            self, text="Scan & Preview", command=on_scan,
            fg_color=DR_ACCENT, hover_color=DR_ACCENT_HOVER, text_color=DR_TEXT
        )
        self.btn_scan.grid(row=10, column=0, sticky="ew", padx=16, pady=(0, 10))

        self.btn_dups = ctk.CTkButton(
            self, text="Find duplicates", command=on_find_duplicates,
            fg_color=DR_SURFACE, hover_color=DR_BORDER, text_color=DR_TEXT,
            border_color=DR_BORDER, border_width=1
        )
        self.btn_dups.grid(row=11, column=0, sticky="ew", padx=16, pady=(0, 10))

        self.btn_apply = ctk.CTkButton(
            self, text="Apply (disabled)", state="disabled", command=on_apply,
            fg_color=DR_PURPLE, hover_color=DR_PURPLE, text_color=DR_TEXT
        )
        self.btn_apply.grid(row=12, column=0, sticky="ew", padx=16, pady=(0, 10))

        self.btn_undo = ctk.CTkButton(
            self, text="Undo (disabled)", state="disabled", command=on_undo,
            fg_color=DR_SURFACE, hover_color=DR_BORDER, text_color=DR_TEXT,
            border_color=DR_BORDER, border_width=1
        )
        self.btn_undo.grid(row=13, column=0, sticky="ew", padx=16, pady=(0, 16))

    # -------- API used by actions/app --------

    def set_folder(self, path: str) -> None:
        self.lbl_path.configure(text=path)

    def get_find_text(self) -> str:
        return self.entry_find.get()

    def get_replace_text(self) -> str:
        return self.entry_replace.get()

    def set_apply_enabled(self, enabled: bool) -> None:
        if enabled:
            self.btn_apply.configure(state="normal", text="Apply")
        else:
            self.btn_apply.configure(state="disabled", text="Apply (disabled)")

    def set_undo_enabled(self, enabled: bool) -> None:
        if enabled:
            self.btn_undo.configure(state="normal", text="Undo last")
        else:
            self.btn_undo.configure(state="disabled", text="Undo (disabled)")

    # -------- NEW: setters for Presets --------

    def set_include_subfolders(self, enabled: bool) -> None:
        if enabled:
            self.sw_sub.select()
        else:
            self.sw_sub.deselect()
        self._on_toggle_subfolders(enabled)

    def set_move_by_extension(self, enabled: bool) -> None:
        if enabled:
            self.sw_move.select()
        else:
            self.sw_move.deselect()
        self._on_toggle_move_by_ext(enabled)

    def set_find_replace(self, find_text: str, replace_text: str) -> None:
        self.entry_find.delete(0, "end")
        self.entry_find.insert(0, find_text or "")
        self.entry_replace.delete(0, "end")
        self.entry_replace.insert(0, replace_text or "")