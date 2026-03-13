from __future__ import annotations
import datetime
from pathlib import Path
import customtkinter as ctk

from ..theme import DR_BG, DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED, DR_ACCENT, DR_ACCENT_HOVER, DR_PURPLE

class LargeFilesPage(ctk.CTkFrame):
    def __init__(self, master, on_choose_folder, on_refresh, on_delete_selected):
        # Initial setup
        super().__init__(master, corner_radius=0, fg_color=DR_BG)
        
        self._on_choose_folder = on_choose_folder
        self._on_refresh = on_refresh
        self._on_delete_selected = on_delete_selected
        self.selection_vars: dict[Path, ctk.BooleanVar] = {}

        self.grid_columnconfigure(0, weight=3) # Main list
        self.grid_columnconfigure(1, weight=1) # Side preview
        self.grid_rowconfigure(2, weight=1)

        # Path selection
        folder_row = ctk.CTkFrame(self, fg_color="transparent")
        folder_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(10, 10))
        self.btn_choose = ctk.CTkButton(folder_row, text="Choose folder", command=self._on_choose_folder, fg_color=DR_SURFACE, hover_color=DR_BORDER, text_color=DR_TEXT, border_color=DR_BORDER, border_width=1, width=120)
        self.btn_choose.pack(side="left", padx=(0, 10))
        self.lbl_path = ctk.CTkLabel(folder_row, text="No folder selected", text_color=DR_MUTED)
        self.lbl_path.pack(side="left")

        # Action bar
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 10))
        ctk.CTkLabel(controls, text="Min size (MB):", text_color=DR_TEXT).pack(side="left", padx=(0, 10))
        self.min_mb_var = ctk.StringVar(value="50")
        self.min_mb_entry = ctk.CTkEntry(controls, textvariable=self.min_mb_var, width=60, fg_color=DR_SURFACE, border_color=DR_BORDER, text_color=DR_TEXT)
        self.min_mb_entry.pack(side="left", padx=(0, 10))
        self.btn_refresh = ctk.CTkButton(controls, text="Scan & Filter", command=self._handle_refresh, fg_color=DR_ACCENT, hover_color=DR_ACCENT_HOVER, text_color=DR_TEXT, width=140)
        self.btn_refresh.pack(side="left")
        self.chk_select_all = ctk.CTkCheckBox(controls, text="Select All", command=self._toggle_select_all, fg_color=DR_PURPLE, hover_color=DR_ACCENT, text_color=DR_TEXT)
        self.chk_select_all.pack(side="left", padx=(30, 10))
        self.btn_del_selected = ctk.CTkButton(controls, text="Delete Selected", command=self._handle_delete_selected, fg_color="#ff5555", hover_color="#ff7777", text_color="#ffffff", width=140, state="disabled")
        self.btn_del_selected.pack(side="left")

        # Files list
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=DR_SURFACE, corner_radius=12, border_width=1, border_color=DR_BORDER)
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=(18, 9), pady=(0, 18))
        self.scroll.grid_columnconfigure(0, weight=1)

        # Right-side details panel
        self.preview_panel = ctk.CTkFrame(self, fg_color=DR_SURFACE, corner_radius=12, border_width=1, border_color=DR_BORDER, width=280)
        self.preview_panel.grid(row=2, column=1, sticky="nsew", padx=(9, 18), pady=(0, 18))
        self.preview_panel.grid_propagate(False) 
        
        self.preview_info_lbl = ctk.CTkLabel(self.preview_panel, text="Select a file to preview details", text_color=DR_MUTED, justify="left", wraplength=240)
        self.preview_info_lbl.pack(padx=20, pady=20, fill="x")

    def set_folder(self, path: str) -> None:
        """Update path label."""
        self.lbl_path.configure(text=path)

    def _handle_refresh(self) -> None:
        """Extract size limit and trigger scan."""
        try: min_mb = float(self.min_mb_var.get())
        except ValueError: min_mb = 0.0
        self._on_refresh(min_mb)

    def _update_delete_btn_state(self) -> None:
        """Update deletion button based on checkbox count."""
        has_selection = any(var.get() for var in self.selection_vars.values())
        self.btn_del_selected.configure(state="normal" if has_selection else "disabled")

    def _toggle_select_all(self) -> None:
        """Check or uncheck everything."""
        state = self.chk_select_all.get()
        for var in self.selection_vars.values(): var.set(state)
        self._update_delete_btn_state()

    def _handle_delete_selected(self) -> None:
        """Delete files marked as selected."""
        paths_to_delete = [p for p, var in self.selection_vars.items() if var.get()]
        if paths_to_delete: self._on_delete_selected(paths_to_delete)

    def _show_preview(self, path: Path) -> None:
        """Show file metadata in side panel."""
        try:
            size_mb = path.stat().st_size / (1024 * 1024)
            mod_time = datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            info_text = f"📄 Name: {path.name}\n\n📦 Size: {size_mb:.2f} MB\n🕒 Modified: {mod_time}\n⚙️ Type: {path.suffix.upper() or 'Unknown'}"
            self.preview_info_lbl.configure(text=info_text, text_color=DR_TEXT)
        except Exception:
            self.preview_info_lbl.configure(text="Preview not available", text_color=DR_MUTED)

    def render_files(self, files: list[tuple[Path, int]]) -> None:
        """Populate the list with heavy files."""
        for widget in self.scroll.winfo_children(): widget.destroy()
        self.selection_vars.clear()
        self.chk_select_all.deselect()
        self._update_delete_btn_state()
        self.preview_info_lbl.configure(text="Select a file to preview details", text_color=DR_MUTED)

        if not files:
            ctk.CTkLabel(self.scroll, text="No files match these criteria.", text_color=DR_MUTED).pack(pady=40)
            return

        for path, size in files:
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", pady=4, padx=8)
            row.grid_columnconfigure(1, weight=1)

            size_mb = size / (1024 * 1024)
            var = ctk.BooleanVar(value=False)
            self.selection_vars[path] = var
            chk = ctk.CTkCheckBox(row, text="", variable=var, width=20, fg_color=DR_PURPLE, hover_color=DR_ACCENT, command=self._update_delete_btn_state)
            chk.grid(row=0, column=0, sticky="w", padx=(5, 10))

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="w")
            lbl_name = ctk.CTkLabel(info_frame, text=f"{path.name}  —  {size_mb:.1f} MB", font=ctk.CTkFont(weight="bold"), text_color=DR_TEXT)
            lbl_name.pack(anchor="w")
            lbl_path = ctk.CTkLabel(info_frame, text=str(path.parent), font=ctk.CTkFont(size=11), text_color=DR_MUTED)
            lbl_path.pack(anchor="w")

            # Interaction binding
            click_handler = lambda e, p=path: self._show_preview(p)
            row.bind("<Button-1>", click_handler)
            info_frame.bind("<Button-1>", click_handler)
            lbl_name.bind("<Button-1>", click_handler)
            lbl_path.bind("<Button-1>", click_handler)

            sep = ctk.CTkFrame(self.scroll, height=1, fg_color=DR_BORDER)
            sep.pack(fill="x", padx=4, pady=(4, 0))