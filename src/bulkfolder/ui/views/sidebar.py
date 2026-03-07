from __future__ import annotations

from PIL import Image
import customtkinter as ctk
from ..theme import DR_PANEL, DR_TEXT, DR_MUTED, DR_BORDER, DR_SURFACE

class SidebarView(ctk.CTkFrame):
    def __init__(self, master, on_page, logo_path=None):
        super().__init__(master, corner_radius=0, fg_color=DR_PANEL)

        self._on_page = on_page
        self._expanded = True
        self._expanded_width = 280
        self._collapsed_width = 74
        
        self.configure(width=self._expanded_width)
        self.grid_propagate(False) 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(99, weight=1)

        self.logo_img = None
        if logo_path and logo_path.exists():
            self.logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(32, 32)
            )

        self.title = ctk.CTkLabel(
            self, 
            text=" BulkFolder", 
            image=self.logo_img, 
            compound="left",
            font=ctk.CTkFont(size=20, weight="bold"), 
            text_color=DR_TEXT
        )
        self.title.grid(row=0, column=0, sticky="w", padx=16, pady=(18, 6))

        self.subtitle = ctk.CTkLabel(self, text="Organize & Rename safely", font=ctk.CTkFont(size=12), text_color=DR_MUTED)
        self.subtitle.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 14))

        self.pages_lbl = ctk.CTkLabel(self, text="Pages", font=ctk.CTkFont(size=13, weight="bold"), text_color=DR_TEXT)
        self.pages_lbl.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 10))

        self.pages_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pages_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 12))
        self.pages_frame.grid_columnconfigure(0, weight=1)

        self._pages = [
            ("Organizer", "Organizer", "🏠"),
            ("Mass Renamer", "Renamer", "📝"),
            ("Folder Flattener", "Flattener", "📥"),
            ("Archive Extractor", "Unzipper", "🔓"), 
            ("Image to PDF", "PdfConverter", "📄"), # Le nouveau bouton PDF !
            ("Date Organizer", "DateOrg", "📅"),
            ("Empty Folders", "EmptyFolders", "🧹"), 
            ("Large Files", "LargeFiles", "📦"),
            ("Settings", "Settings", "⚙"),
            ("About", "About", "ℹ"),
        ]

        self._page_buttons: list[ctk.CTkButton] = []
        for idx, (label, page_name, icon) in enumerate(self._pages):
            btn = ctk.CTkButton(
                self.pages_frame,
                text=f"  {icon}   {label}",
                anchor="w",
                command=lambda p=page_name: self._on_page(p),
                fg_color=DR_SURFACE,
                hover_color=DR_BORDER,
                text_color=DR_TEXT,
                border_color=DR_BORDER,
                border_width=1,
            )
            btn.grid(row=idx, column=0, sticky="ew", pady=(0, 8 if idx < len(self._pages) - 1 else 0))
            self._page_buttons.append(btn)

        self._collapse_hide = [self.subtitle, self.pages_lbl]

    def toggle(self) -> None:
        self.set_collapsed(self._expanded)

    def set_collapsed(self, collapsed: bool) -> None:
        self._expanded = not collapsed
        
        if collapsed:
            self.configure(width=self._collapsed_width)
            self.title.configure(text="")
            for w in self._collapse_hide:
                try: w.grid_remove()
                except Exception: pass
            for btn, (_, _, icon) in zip(self._page_buttons, self._pages):
                btn.configure(text=icon, anchor="center")
        else:
            self.configure(width=self._expanded_width)
            self.title.configure(text=" BulkFolder")
            for w in self._collapse_hide:
                try: w.grid()
                except Exception: pass
            for btn, (label, _, icon) in zip(self._page_buttons, self._pages):
                btn.configure(text=f"  {icon}   {label}", anchor="w")