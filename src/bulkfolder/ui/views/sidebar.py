from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw
import customtkinter as ctk

# Importing theme colors to maintain a consistent look across the app.
from ..theme import DR_PANEL, DR_TEXT, DR_MUTED, DR_BORDER, DR_SURFACE

class SidebarView(ctk.CTkFrame):
    """
    The SidebarView represents the left navigation menu.
    Permanently collapsed with a centralized, stable tooltip system.
    """
    def __init__(self, project_info: dict, master, on_page, logo_path=None):
        super().__init__(master, corner_radius=0, fg_color=DR_PANEL)

        self._on_page = on_page
        self._fixed_width = 74
        self.configure(width=self._fixed_width)
        self.grid_propagate(False)

        # --- Initialize the Permanent Tooltip Window ---
        self._tooltip_window = None
        self._create_tooltip_window()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(99, weight=1)

        # --- Logo ---
        self.logo_img = None
        if logo_path and logo_path.exists():
            self.logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path), 
                dark_image=Image.open(logo_path), 
                size=(32, 32)
            )
        self.title_icon = ctk.CTkLabel(self, text="", image=self.logo_img)
        self.title_icon.grid(row=0, column=0, pady=(20, 30))

        # Buttons container
        self.pages_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pages_frame.grid(row=3, column=0, sticky="ew", padx=10)
        self.pages_frame.grid_columnconfigure(0, weight=1)

        self.icons_dir = logo_path.parent / "icons" if logo_path else Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icons"

        self._pages = [
            ("Organizer", "Organizer", "home.png", "Group files by type and extension"),
            ("Mass Renamer", "Renamer", "edit.png", "Advanced renaming with patterns"),
            ("Folder Splitter", "Chunker", "pie-chart.png", "Split data into smaller subfolders"),
            ("Folder Flattener", "Flattener", "flatten.png", "Pull all files out of subfolders"),
            ("Archive Extractor", "Unzipper", "unlock.png", "Unpack multiple zip/rar archives"), 
            ("Image to PDF", "PdfConverter", "pdf.png", "Merge images into a single document"), 
            ("Date Organizer", "DateOrg", "calendar.png", "Organize files by creation time"),
            ("Empty Folders", "EmptyFolders", "clean.png", "Clean up useless empty directories"), 
            ("Large Files", "LargeFiles", "box.png", "Identify large storage consumers"),
            ("Settings", "Settings", "settings.png", "Customize app behavior"),
            ("About", "About", "info.png", "Project info and version"),
        ]

        for idx, (label, page_name, icon_filename, desc) in enumerate(self._pages):
            icon_path = self.icons_dir / icon_filename
            self._ensure_dummy_icon(icon_path) 
            
            ctk_icon = None
            if icon_path.exists():
                img = Image.open(icon_path).convert("RGBA")
                white_img = Image.new("RGBA", img.size, (255, 255, 255, 255))
                white_img.putalpha(img.split()[3])
                ctk_icon = ctk.CTkImage(light_image=white_img, dark_image=white_img, size=(22, 22))

            btn = ctk.CTkButton(
                self.pages_frame, text="", image=ctk_icon, width=44, height=44,
                fg_color="transparent", hover_color=DR_BORDER,
                command=lambda p=page_name: self._handle_click(p)
            )
            btn.grid(row=idx, column=0, pady=4)
            
            # Optimized hover bindings
            btn.bind("<Enter>", lambda e, l=label, d=desc, b=btn: self._update_tooltip(l, d, b))
            btn.bind("<Leave>", lambda e: self._hide_tooltip())

    def _create_tooltip_window(self):
        """Creates the hidden tooltip window with proper sizing."""
        self._tooltip_window = ctk.CTkToplevel(self)
        self._tooltip_window.withdraw()
        self._tooltip_window.wm_overrideredirect(True)
        self._tooltip_window.attributes("-topmost", True)
        self._tooltip_window.configure(fg_color=DR_BORDER)

        # Main container with a minimum width to avoid "small" appearance
        self._tooltip_container = ctk.CTkFrame(
            self._tooltip_window, 
            fg_color=DR_SURFACE, 
            corner_radius=6, 
            border_width=1, 
            border_color=DR_BORDER,
            width=200 # Enforce a minimum width
        )
        self._tooltip_container.pack(padx=1, pady=1, fill="both", expand=True)

        # Title: Larger and bold
        self._tooltip_label = ctk.CTkLabel(
            self._tooltip_container, 
            text="", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=DR_TEXT,
            justify="left"
        )
        self._tooltip_label.pack(anchor="w", padx=12, pady=(8, 2))

        # Description: Multi-line support
        self._tooltip_desc = ctk.CTkLabel(
            self._tooltip_container, 
            text="", 
            font=ctk.CTkFont(size=12), 
            text_color=DR_MUTED,
            justify="left",
            wraplength=180 # Automatically wraps text after 180 pixels
        )
        self._tooltip_desc.pack(anchor="w", padx=12, pady=(0, 8))

    def _update_tooltip(self, label, description, button):
        """Updates text, forces geometry recalculation, and shows the tooltip."""
        self._tooltip_label.configure(text=label)
        self._tooltip_desc.configure(text=description)
        
        # Force the UI to calculate the size of labels before positioning
        self._tooltip_window.update_idletasks()
        
        # Position calculation
        x = button.winfo_rootx() + 72
        y = button.winfo_rooty()
        self._tooltip_window.wm_geometry(f"+{x}+{y}")
        
        self._tooltip_window.deiconify()
        self._tooltip_window.lift()

    def _hide_tooltip(self):
        """Hides the tooltip window."""
        if self._tooltip_window:
            self._tooltip_window.withdraw()

    def _handle_click(self, page_name):
        """Clears tooltip and switches page."""
        self._hide_tooltip()
        self._on_page(page_name)

    def _ensure_dummy_icon(self, path: Path):
        """Fallback icon generation."""
        if path.exists(): return
        img = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([(12, 12), (52, 52)], radius=8, outline=DR_MUTED, width=4)
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, "PNG")

    def toggle(self) -> None: pass
    def set_collapsed(self, collapsed: bool) -> None: pass