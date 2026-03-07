from __future__ import annotations
import customtkinter as ctk

from ..theme import DR_BG, DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED, DR_ACCENT, DR_ACCENT_HOVER, DR_PURPLE


class DateOrgPage(ctk.CTkFrame):
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

        ctk.CTkLabel(header, text="Date Organizer", font=ctk.CTkFont(size=20, weight="bold"), text_color=DR_TEXT).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Automatically group your files into folders based on their creation date", font=ctk.CTkFont(size=12), text_color=DR_MUTED).grid(row=1, column=0, sticky="w", pady=(6, 0))

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

        # Controls
        card = ctk.CTkFrame(self, corner_radius=12, fg_color=DR_SURFACE, border_color=DR_BORDER, border_width=1)
        card.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))
        
        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.pack(fill="x", padx=16, pady=16)

        ctk.CTkLabel(controls, text="Folder Structure:", text_color=DR_TEXT).pack(side="left", padx=(0, 10))
        
        self.mode_var = ctk.StringVar(value="Year/Month (2024/01)")
        self.opt_mode = ctk.CTkOptionMenu(
            controls, variable=self.mode_var,
            values=["Year (2024)", "Year/Month (2024/01)", "Year/Month/Day (2024/01/15)"],
            fg_color=DR_SURFACE, button_color=DR_BORDER, text_color=DR_TEXT
        )
        self.opt_mode.pack(side="left", padx=(0, 20))

        self.btn_apply = ctk.CTkButton(controls, text="Apply Sorting", state="disabled", command=self._on_apply, fg_color=DR_ACCENT, hover_color=DR_ACCENT_HOVER, text_color=DR_TEXT)
        self.btn_apply.pack(side="right")
        
        self.btn_preview = ctk.CTkButton(controls, text="Preview", command=self._on_preview, fg_color=DR_SURFACE, hover_color=DR_BORDER, border_width=1, text_color=DR_TEXT)
        self.btn_preview.pack(side="right", padx=(0, 10))

        # Preview list
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=DR_SURFACE, corner_radius=12, border_width=1, border_color=DR_BORDER)
        self.scroll.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.scroll.grid_columnconfigure(0, weight=1)
        self.scroll.grid_columnconfigure(1, weight=0)
        self.scroll.grid_columnconfigure(2, weight=1)

    def set_folder(self, path: str):
        self.lbl_path.configure(text=path)

    def set_apply_enabled(self, enabled: bool):
        self.btn_apply.configure(state="normal" if enabled else "disabled")

    def clear_preview(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()
        self.set_apply_enabled(False)

    def render_preview(self, files: list[tuple[str, str]]):
        self.clear_preview()

        if not files:
            ctk.CTkLabel(self.scroll, text="No files found to organize.", text_color=DR_MUTED).grid(row=0, column=0, columnspan=3, pady=40)
            return

        for idx, (old_name, new_dest) in enumerate(files):
            ctk.CTkLabel(self.scroll, text=old_name, text_color=DR_MUTED).grid(row=idx, column=0, sticky="e", padx=10, pady=4)
            ctk.CTkLabel(self.scroll, text="➔", text_color=DR_PURPLE).grid(row=idx, column=1, padx=10, pady=4)
            ctk.CTkLabel(self.scroll, text=new_dest, text_color=DR_TEXT, font=ctk.CTkFont(weight="bold")).grid(row=idx, column=2, sticky="w", padx=10, pady=4)
            
        self.set_apply_enabled(True)