from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw
import customtkinter as ctk
from ..theme import DR_PANEL, DR_TEXT, DR_MUTED, DR_BORDER, DR_SURFACE

class SidebarView(ctk.CTkFrame):
    def __init__(self, project_info:dict, master, on_page, logo_path=None):
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

        if logo_path:
            self.icons_dir = logo_path.parent / "icons"
        else:
            self.icons_dir = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icons"
            
        self.icons_dir.mkdir(parents=True, exist_ok=True)

        self._pages = [
            ("Organizer", "Organizer", "home.png"),
            ("Mass Renamer", "Renamer", "edit.png"),
            ("Folder Splitter", "Chunker", "pie-chart.png"),
            ("Folder Flattener", "Flattener", "flatten.png"),
            ("Archive Extractor", "Unzipper", "unlock.png"), 
            ("Image to PDF", "PdfConverter", "pdf.png"), 
            ("Date Organizer", "DateOrg", "calendar.png"),
            ("Empty Folders", "EmptyFolders", "clean.png"), 
            ("Large Files", "LargeFiles", "box.png"),
            ("Settings", "Settings", "settings.png"),
            ("About", "About", "info.png"),
        ]

        self._page_buttons: list[ctk.CTkButton] = []
        self._page_labels: list[str] = []

        for idx, (label, page_name, icon_filename) in enumerate(self._pages):
            icon_path = self.icons_dir / icon_filename
            self._ensure_dummy_icon(icon_path) 
            
            ctk_icon = None
            if icon_path.exists():
                original_img = Image.open(icon_path).convert("RGBA")
                r, g, b, a = original_img.split()
                white_img = Image.new("RGBA", original_img.size, (255, 255, 255, 255))
                white_img.putalpha(a)
                ctk_icon = ctk.CTkImage(light_image=white_img, dark_image=white_img, size=(20, 20))

            btn = ctk.CTkButton(
                self.pages_frame,
                text=f"  {label}",
                image=ctk_icon,      
                compound="left",     
                anchor="w",
                command=lambda p=page_name: self._on_page(p),
                fg_color=DR_SURFACE,
                hover_color=DR_BORDER,
                text_color=DR_TEXT,
                border_color=DR_BORDER,
                border_width=1,
                height=36            
            )
            btn.grid(row=idx, column=0, sticky="ew", pady=(0, 8 if idx < len(self._pages) - 1 else 0))
            self._page_buttons.append(btn)
            self._page_labels.append(label)

        self._collapse_hide = [self.subtitle, self.pages_lbl]

        # display the verion

        version = project_info.get("version", "1.0.0")
        self.version_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.version_frame.grid(row=6, column=0, sticky="w", padx=2, pady=(0, 14))

        self.version_display = ctk.CTkLabel(self.version_frame, text=f"version {version}", justify="center", text_color=DR_MUTED)
        self.version_display.grid(row=6, column=0, padx=16)
        

    def _ensure_dummy_icon(self, path: Path):
        if path.exists(): return
        try:
            img = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([(12, 12), (52, 52)], radius=8, outline=DR_MUTED, width=4)
            path.parent.mkdir(parents=True, exist_ok=True)
            img.save(path, "PNG")
        except Exception:
            pass

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
            
            for btn in self._page_buttons:
                btn.configure(text="", anchor="center")
        else:
            self.configure(width=self._expanded_width)
            self.title.configure(text=" BulkFolder")
            for w in self._collapse_hide:
                try: w.grid()
                except Exception: pass
            
            for btn, label in zip(self._page_buttons, self._page_labels):
                btn.configure(text=f"  {label}", anchor="w")
