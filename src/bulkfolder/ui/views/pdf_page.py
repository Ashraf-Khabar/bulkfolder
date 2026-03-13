from __future__ import annotations
import datetime
from pathlib import Path
from PIL import Image
import customtkinter as ctk

from ..theme import DR_BG, DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED, DR_ACCENT, DR_ACCENT_HOVER, DR_PURPLE

class PdfPage(ctk.CTkFrame):
    def __init__(self, master, on_choose_folder, on_refresh, on_convert):
        # Initialize frame with background color
        super().__init__(master, corner_radius=0, fg_color=DR_BG)
        
        self._on_choose_folder = on_choose_folder
        self._on_refresh = on_refresh
        self._on_convert = on_convert
        self.selection_vars: dict[Path, ctk.BooleanVar] = {}

        # Main grid layout: 2 columns (List + Preview)
        self.grid_columnconfigure(0, weight=3) # Larger list area
        self.grid_columnconfigure(1, weight=1) # Preview panel area
        self.grid_rowconfigure(2, weight=1) # Adjusted row index

        # Folder selection row
        folder_row = ctk.CTkFrame(self, fg_color="transparent")
        folder_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(10, 10))
        self.btn_choose = ctk.CTkButton(folder_row, text="Choose folder", command=self._on_choose_folder, fg_color=DR_SURFACE, hover_color=DR_BORDER, text_color=DR_TEXT, border_color=DR_BORDER, border_width=1, width=120)
        self.btn_choose.pack(side="left", padx=(0, 10))
        self.lbl_path = ctk.CTkLabel(folder_row, text="No folder selected", text_color=DR_MUTED)
        self.lbl_path.pack(side="left")

        # Action controls
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 10))
        self.btn_refresh = ctk.CTkButton(controls, text="Scan for Images", command=self._on_refresh, fg_color=DR_SURFACE, hover_color=DR_BORDER, border_width=1, text_color=DR_TEXT, width=160)
        self.btn_refresh.pack(side="left")
        self.chk_select_all = ctk.CTkCheckBox(controls, text="Select All", command=self._toggle_select_all, fg_color=DR_PURPLE, hover_color=DR_ACCENT, text_color=DR_TEXT)
        self.chk_select_all.pack(side="left", padx=(30, 20))
        self.switch_delete = ctk.CTkSwitch(controls, text="Delete original images", progress_color=DR_PURPLE)
        self.switch_delete.pack(side="left", padx=(0, 20))
        self.btn_convert = ctk.CTkButton(controls, text="Convert to PDF", command=self._handle_convert, fg_color=DR_ACCENT, hover_color=DR_ACCENT_HOVER, text_color=DR_TEXT, width=160, state="disabled")
        self.btn_convert.pack(side="left")

        # LEFT PANEL: File list
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=DR_SURFACE, corner_radius=12, border_width=1, border_color=DR_BORDER)
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=(18, 9), pady=(0, 18))
        self.scroll.grid_columnconfigure(0, weight=1)

        # RIGHT PANEL: Preview
        self.preview_panel = ctk.CTkFrame(self, fg_color=DR_SURFACE, corner_radius=12, border_width=1, border_color=DR_BORDER, width=280)
        self.preview_panel.grid(row=2, column=1, sticky="nsew", padx=(9, 18), pady=(0, 18))
        self.preview_panel.grid_propagate(False) 
        
        self.preview_img_lbl = ctk.CTkLabel(self.preview_panel, text="")
        self.preview_img_lbl.pack(pady=(20, 10))
        
        self.preview_info_lbl = ctk.CTkLabel(self.preview_panel, text="Select a file to preview", text_color=DR_MUTED, justify="left", wraplength=240)
        self.preview_info_lbl.pack(padx=20, fill="x")

        self._current_preview_img = None

    def set_folder(self, path: str) -> None:
        """Update the displayed folder path."""
        self.lbl_path.configure(text=path)

    def _update_btn_state(self) -> None:
        """Update the convert button state based on selection."""
        has_selection = any(var.get() for var in self.selection_vars.values())
        self.btn_convert.configure(state="normal" if has_selection else "disabled")

    def _toggle_select_all(self) -> None:
        """Toggle selection for all items."""
        state = self.chk_select_all.get()
        for var in self.selection_vars.values(): var.set(state)
        self._update_btn_state()

    def _handle_convert(self) -> None:
        """Trigger the conversion process for selected paths."""
        paths = [p for p, var in self.selection_vars.items() if var.get()]
        if paths: self._on_convert(paths)

    def _show_preview(self, path: Path) -> None:
        """Display image preview and metadata."""
        try:
            size_mb = path.stat().st_size / (1024 * 1024)
            mod_time = datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            
            img = Image.open(path)
            img.thumbnail((220, 220)) 
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.preview_img_lbl.configure(image=ctk_img)
            self._current_preview_img = ctk_img
            
            info_text = f"Name: {path.name}\n\nSize: {size_mb:.2f} MB\nDimensions: {img.width}x{img.height} px\nModified: {mod_time}"
            self.preview_info_lbl.configure(text=info_text, text_color=DR_TEXT)
        except Exception:
            self.preview_img_lbl.configure(image=None)
            self.preview_info_lbl.configure(text="Preview not available", text_color=DR_MUTED)

    def render_files(self, files: list[Path]) -> None:
        """Render the list of images found in the folder."""
        for widget in self.scroll.winfo_children(): widget.destroy()
        self.selection_vars.clear()
        self.chk_select_all.deselect()
        self._update_btn_state()
        
        self.preview_img_lbl.configure(image=None)
        self.preview_info_lbl.configure(text="Select a file to preview", text_color=DR_MUTED)

        if not files:
            ctk.CTkLabel(self.scroll, text="No compatible images found.", text_color=DR_MUTED).pack(pady=40)
            return

        for path in files:
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", pady=4, padx=8)
            row.grid_columnconfigure(1, weight=1)
            
            var = ctk.BooleanVar(value=True)
            self.selection_vars[path] = var
            chk = ctk.CTkCheckBox(row, text="", variable=var, width=20, fg_color=DR_PURPLE, hover_color=DR_ACCENT, command=self._update_btn_state)
            chk.grid(row=0, column=0, sticky="w", padx=(5, 10))

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="w")
            
            lbl_name = ctk.CTkLabel(info_frame, text=f"🖼️ {path.name}", font=ctk.CTkFont(weight="bold"), text_color=DR_TEXT)
            lbl_name.pack(anchor="w")
            lbl_path = ctk.CTkLabel(info_frame, text=str(path.parent), font=ctk.CTkFont(size=11), text_color=DR_MUTED)
            lbl_path.pack(anchor="w")

            # Bind click events for preview
            click_handler = lambda e, p=path: self._show_preview(p)
            row.bind("<Button-1>", click_handler)
            info_frame.bind("<Button-1>", click_handler)
            lbl_name.bind("<Button-1>", click_handler)
            lbl_path.bind("<Button-1>", click_handler)

            sep = ctk.CTkFrame(self.scroll, height=1, fg_color=DR_BORDER)
            sep.pack(fill="x", padx=4, pady=(4, 0))

        self.chk_select_all.select()
        self._update_btn_state()