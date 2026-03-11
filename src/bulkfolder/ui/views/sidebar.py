from __future__ import annotations
from pathlib import Path
from PIL import Image
import customtkinter as ctk
import tkinter as tk

from ..theme import DR_PANEL, DR_TEXT, DR_MUTED, DR_BORDER, DR_SURFACE, DR_BG

class Tooltip:
    """ Floating 'Post-it' window for icon hover events """
    def __init__(self, widget, text, description):
        self.widget = widget
        self.text = text
        self.description = description
        self.tip_window = None

    def show_tip(self):
        if self.tip_window: return
        x = self.widget.winfo_rootx() + 65
        y = self.widget.winfo_rooty() + 10
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        
        frame = tk.Frame(tw, background="#2d2d2d", padx=10, pady=8, highlightthickness=1, highlightbackground=DR_BORDER)
        frame.pack()
        
        tk.Label(frame, text=self.text, foreground="white", background="#2d2d2d", 
                 font=("Segoe UI", 10, "bold"), justify="left").pack(anchor="w")
        tk.Label(frame, text=self.description, foreground="#aaaaaa", background="#2d2d2d", 
                 font=("Segoe UI", 9), justify="left").pack(anchor="w")

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class SidebarView(ctk.CTkFrame):
    def __init__(self, project_info: dict, master, on_page, logo_path=None):
        super().__init__(master, corner_radius=0, fg_color=DR_PANEL, width=74)
        self.grid_propagate(False)
        self._on_page = on_page

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(99, weight=1)

        if logo_path and logo_path.exists():
            img = Image.open(logo_path)
            self.logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(32, 32))
            ctk.CTkLabel(self, text="", image=self.logo_img).grid(row=0, column=0, pady=(20, 20))

        self.icons_dir = logo_path.parent / "icons" if logo_path else Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icons"

        # Menu items in English with hover descriptions
        self._pages = [
            ("Organizer", "Organizer", "home.png", "Auto-sort files by extension."),
            ("Mass Renamer", "Renamer", "edit.png", "Rename thousands of files at once."),
            ("Folder Splitter", "Chunker", "pie-chart.png", "Split folders by size or count."),
            ("Folder Flattener", "Flattener", "flatten.png", "Move all nested files to root."),
            ("Archive Extractor", "Unzipper", "unlock.png", "Bulk extract ZIP/RAR archives."), 
            ("Image to PDF", "PdfConverter", "pdf.png", "Convert JPG/PNG images to PDF."), 
            ("Date Organizer", "DateOrg", "calendar.png", "Organize files by Year/Month."),
            ("Empty Folders", "EmptyFolders", "clean.png", "Find and remove empty directories."), 
            ("Large Files", "LargeFiles", "box.png", "Locate the heaviest files."),
            ("Settings", "Settings", "settings.png", "Configure app preferences."),
            ("About", "About", "info.png", "Version info and credits."),
        ]

        for idx, (label, name, icon, desc) in enumerate(self._pages):
            icon_path = self.icons_dir / icon
            ctk_icon = None
            if icon_path.exists():
                img = Image.open(icon_path).convert("RGBA")
                _, _, _, a = img.split()
                white_img = Image.new("RGBA", img.size, (255, 255, 255, 255))
                white_img.putalpha(a)
                ctk_icon = ctk.CTkImage(light_image=white_img, dark_image=white_img, size=(22, 22))

            btn = ctk.CTkButton(
                self, text="", image=ctk_icon, width=50, height=44,
                fg_color="transparent", hover_color=DR_BORDER,
                command=lambda p=name: self._on_page(p)
            )
            btn.grid(row=idx+1, column=0, pady=1)

            tip = Tooltip(btn, label, desc)
            btn.bind("<Enter>", lambda e, t=tip: t.show_tip())
            btn.bind("<Leave>", lambda e, t=tip: t.hide_tip())

    def toggle(self): pass