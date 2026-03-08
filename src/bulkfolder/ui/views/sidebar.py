from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw
import customtkinter as ctk

# Importing theme colors to maintain a consistent look across the app.
from ..theme import DR_PANEL, DR_TEXT, DR_MUTED, DR_BORDER, DR_SURFACE

class SidebarView(ctk.CTkFrame):
    """
    The SidebarView represents the left navigation menu of the application.
    It handles its own visual state (expanded/collapsed) and sends signals 
    to the main App when a navigation button is clicked.
    """
    def __init__(self, project_info: dict, master, on_page, logo_path=None):
        # Initialize the parent CTkFrame with a specific background color (DR_PANEL).
        super().__init__(master, corner_radius=0, fg_color=DR_PANEL)

        # 'on_page' is a callback function passed from app.py. 
        # We will call it when the user clicks a menu button.
        self._on_page = on_page
        self._expanded = True
        self._expanded_width = 280
        self._collapsed_width = 74
        
        # Set the initial width and prevent the frame from shrinking 
        # automatically to fit its content (grid_propagate(False)).
        self.configure(width=self._expanded_width)
        self.grid_propagate(False)

        # Configure the grid layout.
        # Column 0 takes all available width. Row 99 acts as a flexible spacer
        # to push everything else up and the version text down to the bottom.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(99, weight=1)

        # --- Logo & Headers ---
        self.logo_img = None
        if logo_path and logo_path.exists():
            self.logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(32, 32)
            )

        # App Title
        self.title = ctk.CTkLabel(
            self, 
            text=" BulkFolder", 
            image=self.logo_img, 
            compound="left", # Places the image to the left of the text
            font=ctk.CTkFont(size=20, weight="bold"), 
            text_color=DR_TEXT
        )
        self.title.grid(row=0, column=0, sticky="w", padx=16, pady=(18, 6))

        # Subtitle
        self.subtitle = ctk.CTkLabel(self, text="Organize & Rename safely", font=ctk.CTkFont(size=12), text_color=DR_MUTED)
        self.subtitle.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 14))

        # "Pages" section label
        self.pages_lbl = ctk.CTkLabel(self, text="Pages", font=ctk.CTkFont(size=13, weight="bold"), text_color=DR_TEXT)
        self.pages_lbl.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 10))

        # Container frame specifically for the navigation buttons.
        self.pages_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pages_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 12))
        self.pages_frame.grid_columnconfigure(0, weight=1)

        # --- Icon Directory Setup ---
        if logo_path:
            self.icons_dir = logo_path.parent / "icons"
        else:
            self.icons_dir = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icons"
            
        self.icons_dir.mkdir(parents=True, exist_ok=True)

        # List of all available pages in the app: (Display Name, Internal Name, Icon File)
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

        # --- Dynamic Menu Generation ---
        # We loop through the _pages list to create a button for each entry.
        for idx, (label, page_name, icon_filename) in enumerate(self._pages):
            icon_path = self.icons_dir / icon_filename
            self._ensure_dummy_icon(icon_path) 
            
            ctk_icon = None
            if icon_path.exists():
                # MAGIC PIL (Python Imaging Library): 
                # Converting dark icons downloaded from the internet into pure white icons dynamically.
                original_img = Image.open(icon_path).convert("RGBA")
                # 1. Split the image into Red, Green, Blue, and Alpha (Transparency) channels.
                r, g, b, a = original_img.split()
                # 2. Create a brand new, completely white image of the same size.
                white_img = Image.new("RGBA", original_img.size, (255, 255, 255, 255))
                # 3. Apply the original image's transparency mask to the solid white image.
                white_img.putalpha(a)
                # Now we have a perfectly white icon with smooth, anti-aliased edges!
                ctk_icon = ctk.CTkImage(light_image=white_img, dark_image=white_img, size=(20, 20))

            # Create the actual navigation button
            btn = ctk.CTkButton(
                self.pages_frame,
                text=f"  {label}",
                image=ctk_icon,      
                compound="left",     
                anchor="w", # Align text and icon to the West (left)
                # The lambda function captures the specific 'page_name' for this button
                command=lambda p=page_name: self._on_page(p),
                fg_color=DR_SURFACE,
                hover_color=DR_BORDER,
                text_color=DR_TEXT,
                border_color=DR_BORDER,
                border_width=1,
                height=36            
            )
            # Place the button in the grid. If it's the last button, don't add bottom padding.
            btn.grid(row=idx, column=0, sticky="ew", pady=(0, 8 if idx < len(self._pages) - 1 else 0))
            self._page_buttons.append(btn)
            self._page_labels.append(label)

        # --- Version Display ---
        # Fetch the version from the project_info dictionary (defaults to 1.0.0 if not found).
        version = project_info.get("version", "1.0.0")
        
        # Create a frame to hold the version text at the very bottom (row 6)
        self.version_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.version_frame.grid(row=6, column=0, sticky="w", padx=2, pady=(0, 14))

        # Create and place the version text inside its dedicated frame
        self.version_display = ctk.CTkLabel(self.version_frame, text=f"version {version}", justify="center", text_color=DR_MUTED)
        self.version_display.grid(row=0, column=0, padx=16)

        # --- Element Hiding Management ---
        # We store references to all elements that should DISAPPEAR when the sidebar is collapsed.
        self._collapse_hide = [self.subtitle, self.pages_lbl, self.version_frame]
        

    def _ensure_dummy_icon(self, path: Path):
        """Creates a placeholder icon file if the specific icon is missing."""
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
        """Helper method to flip the current state of the sidebar."""
        self.set_collapsed(self._expanded)

    def set_collapsed(self, collapsed: bool) -> None:
        """
        Handles the visual transformation between the expanded and collapsed states.
        Instead of destroying widgets, it temporarily hides them or alters their text.
        """
        self._expanded = not collapsed
        
        if collapsed:
            # 1. Shrink the main frame width
            self.configure(width=self._collapsed_width)
            self.title.configure(text="") # Remove the app title text next to the logo
            
            # 2. Hide specific elements using grid_remove() (keeps them in memory, but invisible)
            for w in self._collapse_hide:
                try: w.grid_remove()
                except Exception: pass
            
            # 3. Remove text from navigation buttons and center the remaining icons
            for btn in self._page_buttons:
                btn.configure(text="", anchor="center")
        else:
            # 1. Restore the main frame width
            self.configure(width=self._expanded_width)
            self.title.configure(text=" BulkFolder")
            
            # 2. Restore hidden elements using grid()
            for w in self._collapse_hide:
                try: w.grid()
                except Exception: pass
            
            # 3. Restore text and left-alignment for all navigation buttons
            for btn, label in zip(self._page_buttons, self._page_labels):
                btn.configure(text=f"  {label}", anchor="w")
