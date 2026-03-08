from __future__ import annotations
from pathlib import Path
import customtkinter as ctk

from ..theme import DR_BG, DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED, DR_ACCENT, DR_ACCENT_HOVER, DR_PURPLE

class ChunkerPage(ctk.CTkFrame):
    def __init__(self, master, on_choose_folder, on_preview, on_apply):
        super().__init__(master, corner_radius=0, fg_color=DR_BG)
        
        self._on_choose_folder = on_choose_folder
        self._on_preview = on_preview
        self._on_apply = on_apply

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Folder Splitter (Chunker)", font=ctk.CTkFont(size=20, weight="bold"), text_color=DR_TEXT).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Split large directories into smaller parts by Size or File Count", font=ctk.CTkFont(size=12), text_color=DR_MUTED).grid(row=1, column=0, sticky="w", pady=(6, 0))

        # Folder selection
        folder_row = ctk.CTkFrame(self, fg_color="transparent")
        folder_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))

        self.btn_choose = ctk.CTkButton(folder_row, text="Choose folder", command=self._on_choose_folder, fg_color=DR_SURFACE, hover_color=DR_BORDER, text_color=DR_TEXT, border_color=DR_BORDER, border_width=1, width=120)
        self.btn_choose.pack(side="left", padx=(0, 10))
        self.lbl_path = ctk.CTkLabel(folder_row, text="No folder selected", text_color=DR_MUTED)
        self.lbl_path.pack(side="left")

        # Controls Row
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))
        
        self.mode_var = ctk.StringVar(value="size")
        ctk.CTkRadioButton(controls, text="Max Size (MB)", variable=self.mode_var, value="size", fg_color=DR_PURPLE, text_color=DR_TEXT).pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(controls, text="Max File Count", variable=self.mode_var, value="count", fg_color=DR_PURPLE, text_color=DR_TEXT).pack(side="left", padx=(10, 20))

        ctk.CTkLabel(controls, text="Limit:", text_color=DR_TEXT).pack(side="left", padx=(0, 5))
        self.val_var = ctk.StringVar(value="2000") # 2000 MB (2GB) par défaut
        ctk.CTkEntry(controls, textvariable=self.val_var, width=80).pack(side="left", padx=(0, 20))

        self.btn_preview = ctk.CTkButton(controls, text="Preview Split", command=self._on_preview, fg_color=DR_SURFACE, hover_color=DR_BORDER, border_width=1, text_color=DR_TEXT, width=140)
        self.btn_preview.pack(side="left", padx=(0, 10))

        self.btn_apply = ctk.CTkButton(controls, text="Apply Split", command=self._on_apply, fg_color=DR_ACCENT, hover_color=DR_ACCENT_HOVER, text_color=DR_TEXT, width=140, state="disabled")
        self.btn_apply.pack(side="left")

        # Preview list
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=DR_SURFACE, corner_radius=12, border_width=1, border_color=DR_BORDER)
        self.scroll.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.scroll.grid_columnconfigure(0, weight=1)

    def set_folder(self, path: str):
        self.lbl_path.configure(text=path)

    def render_preview(self, chunks: list[dict]):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        self.btn_apply.configure(state="normal" if chunks else "disabled")

        if not chunks:
            ctk.CTkLabel(self.scroll, text="Click 'Preview Split' to calculate chunks.", text_color=DR_MUTED).pack(pady=40)
            return

        for chunk in chunks:
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", pady=6, padx=12)
            row.grid_columnconfigure(1, weight=1)
            
            size_mb = chunk["size"] / (1024 * 1024)
            files_count = len(chunk["files"])
            
            ctk.CTkLabel(row, text="🗂️", font=ctk.CTkFont(size=24)).grid(row=0, column=0, rowspan=2, padx=(0, 15), sticky="w")
            
            ctk.CTkLabel(row, text=chunk["name"], font=ctk.CTkFont(weight="bold", size=14), text_color=DR_TEXT).grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(row, text=f"{files_count} files  —  {size_mb:.2f} MB", font=ctk.CTkFont(size=12), text_color=DR_MUTED).grid(row=1, column=1, sticky="w")

            sep = ctk.CTkFrame(self.scroll, height=1, fg_color=DR_BORDER)
            sep.pack(fill="x", padx=4, pady=(4, 0))