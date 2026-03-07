from __future__ import annotations
from pathlib import Path
import customtkinter as ctk

from ..theme import DR_BG, DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED, DR_ACCENT, DR_ACCENT_HOVER, DR_PURPLE

class UnzipperPage(ctk.CTkFrame):
    def __init__(self, master, on_choose_folder, on_refresh, on_extract_selected):
        super().__init__(master, corner_radius=0, fg_color=DR_BG)
        
        self._on_choose_folder = on_choose_folder
        self._on_refresh = on_refresh
        self._on_extract_selected = on_extract_selected
        
        self.selection_vars: dict[Path, ctk.BooleanVar] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Bulk Archive Extractor", font=ctk.CTkFont(size=20, weight="bold"), text_color=DR_TEXT).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Find all ZIP/TAR archives and extract them instantly", font=ctk.CTkFont(size=12), text_color=DR_MUTED).grid(row=1, column=0, sticky="w", pady=(6, 0))

        # Folder selection
        folder_row = ctk.CTkFrame(self, fg_color="transparent")
        folder_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))

        self.btn_choose = ctk.CTkButton(
            folder_row, text="Choose folder", command=self._on_choose_folder,
            fg_color=DR_SURFACE, hover_color=DR_BORDER, text_color=DR_TEXT, border_color=DR_BORDER, border_width=1, width=120
        )
        self.btn_choose.pack(side="left", padx=(0, 10))

        self.lbl_path = ctk.CTkLabel(folder_row, text="No folder selected", text_color=DR_MUTED)
        self.lbl_path.pack(side="left")

        # Controls Row
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))
        
        self.btn_refresh = ctk.CTkButton(
            controls, text="Scan for Archives", command=self._on_refresh,
            fg_color=DR_SURFACE, hover_color=DR_BORDER, border_width=1, text_color=DR_TEXT, width=160
        )
        self.btn_refresh.pack(side="left")

        self.chk_select_all = ctk.CTkCheckBox(
            controls, text="Select All", command=self._toggle_select_all, 
            fg_color=DR_PURPLE, hover_color=DR_ACCENT, text_color=DR_TEXT
        )
        self.chk_select_all.pack(side="left", padx=(30, 20))

        self.switch_delete = ctk.CTkSwitch(
            controls, text="Delete archives after extraction", progress_color=DR_PURPLE
        )
        self.switch_delete.pack(side="left", padx=(0, 20))

        self.btn_extract_selected = ctk.CTkButton(
            controls, text="Extract Selected", command=self._handle_extract_selected,
            fg_color=DR_ACCENT, hover_color=DR_ACCENT_HOVER, text_color=DR_TEXT, width=160, state="disabled"
        )
        self.btn_extract_selected.pack(side="left")

        # Preview list
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=DR_SURFACE, corner_radius=12, border_width=1, border_color=DR_BORDER)
        self.scroll.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.scroll.grid_columnconfigure(0, weight=1)

    def set_folder(self, path: str):
        self.lbl_path.configure(text=path)

    def _update_extract_btn_state(self):
        has_selection = any(var.get() for var in self.selection_vars.values())
        self.btn_extract_selected.configure(state="normal" if has_selection else "disabled")

    def _toggle_select_all(self):
        state = self.chk_select_all.get()
        for var in self.selection_vars.values():
            var.set(state)
        self._update_extract_btn_state()

    def _handle_extract_selected(self):
        paths_to_extract = [p for p, var in self.selection_vars.items() if var.get()]
        if paths_to_extract:
            self._on_extract_selected(paths_to_extract)

    def render_archives(self, archives: list[Path]):
        for widget in self.scroll.winfo_children():
            widget.destroy()
            
        self.selection_vars.clear()
        self.chk_select_all.deselect()
        self._update_extract_btn_state()

        if not archives:
            ctk.CTkLabel(self.scroll, text="No ZIP or TAR archives found in this directory.", text_color=DR_MUTED).pack(pady=40)
            return

        for path in archives:
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", pady=4, padx=8)
            row.grid_columnconfigure(1, weight=1)
            
            var = ctk.BooleanVar(value=True) # Checked by default
            self.selection_vars[path] = var
            
            chk = ctk.CTkCheckBox(row, text="", variable=var, width=20, 
                                  fg_color=DR_PURPLE, hover_color=DR_ACCENT, 
                                  command=self._update_extract_btn_state)
            chk.grid(row=0, column=0, sticky="w", padx=(5, 10))

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="w")
            
            size_mb = path.stat().st_size / (1024 * 1024)
            
            ctk.CTkLabel(info_frame, text=f"🗜️ {path.name}  —  {size_mb:.1f} MB", font=ctk.CTkFont(weight="bold"), text_color=DR_TEXT).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=str(path.parent), font=ctk.CTkFont(size=11), text_color=DR_MUTED).pack(anchor="w")

            sep = ctk.CTkFrame(self.scroll, height=1, fg_color=DR_BORDER)
            sep.pack(fill="x", padx=4, pady=(4, 0))

        self.chk_select_all.select()
        self._update_extract_btn_state()