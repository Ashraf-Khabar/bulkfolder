from __future__ import annotations
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageOps
from ..theme import DR_SURFACE, DR_TEXT, DR_MUTED, DR_PURPLE

class SidebarView(ctk.CTkFrame):
    """
    Sidebar de navigation latérale. 
    Optimisée avec mise en cache et icônes blanches agrandies.
    """
    def __init__(self, project_info, master, on_page, logo_path, **kwargs):
        super().__init__(master, width=220, corner_radius=0, fg_color=DR_SURFACE, border_width=1, border_color="#1e1e2e", **kwargs)
        self.on_page = on_page
        self.grid_propagate(False)
        
        # Cache pour les icônes (évite le lag lors du changement d'écran)
        self._icon_cache = {}

        # Section Logo
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.pack(fill="x", pady=25, padx=20)
        
        if logo_path.exists():
            img = Image.open(logo_path)
            # Logo légèrement plus grand (36x36 au lieu de 32x32)
            self.logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(36, 36))
            self.logo_label = ctk.CTkLabel(self.logo_frame, text=" BulkFolder", image=self.logo_img, compound="left", font=ctk.CTkFont(size=18, weight="bold"))
            self.logo_label.pack(side="left")

        # Conteneur de menu
        self.menu_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.menu_container.pack(fill="both", expand=True, padx=10, pady=5)

        self._add_section("TOOLS")
        self._add_item("Organizer", "home.png")
        self._add_item("Renamer", "edit.png")
        self._add_item("DateOrg", "calendar.png")
        
        self._add_section("UTILITIES")
        self._add_item("Chunker", "box.png")
        self._add_item("Flattener", "flatten.png")
        self._add_item("Unzipper", "unlock.png")
        self._add_item("PdfConverter", "pdf.png")
        
        self._add_section("CLEANUP")
        self._add_item("EmptyFolders", "clean.png")
        self._add_item("LargeFiles", "pie-chart.png")

        # Section Basse
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=15)
        
        self._add_item("Settings", "settings.png", parent=self.bottom_frame)
        self._add_item("About", "info.png", parent=self.bottom_frame)

    def _get_icon(self, name: str):
        """Récupère, blanchit et met en cache l'icône."""
        if name in self._icon_cache:
            return self._icon_cache[name]
            
        icon_path = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icons" / name
        if icon_path.exists():
            img = Image.open(icon_path).convert("RGBA")
            
            # OPTIMISATION VISUELLE : Transformation de l'icône en blanc
            # On sépare l'alpha pour ne colorer que les pixels visibles
            r, g, b, alpha = img.split()
            white_img = Image.merge("RGBA", (alpha.point(lambda x: 255), 
                                             alpha.point(lambda x: 255), 
                                             alpha.point(lambda x: 255), 
                                             alpha))
            
            # Taille augmentée à 22x22 (au lieu de 18x18) pour plus de visibilité
            icon = ctk.CTkImage(light_image=white_img, dark_image=white_img, size=(22, 22))
            self._icon_cache[name] = icon
            return icon
        return None

    def _add_section(self, text: str):
        label = ctk.CTkLabel(self.menu_container, text=text, font=ctk.CTkFont(size=10, weight="bold"), text_color=DR_MUTED)
        label.pack(anchor="w", padx=15, pady=(15, 5))

    def _add_item(self, name: str, icon_name: str, parent=None):
        target = parent if parent else self.menu_container
        icon = self._get_icon(icon_name)
        
        btn = ctk.CTkButton(
            target,
            text=f"  {name}", # Un peu plus d'espace après l'icône
            image=icon,
            compound="left",
            anchor="w",
            height=40, # Hauteur augmentée pour accommoder les icônes plus grandes
            fg_color="transparent",
            text_color=DR_TEXT,
            hover_color="#2d2d3d",
            font=ctk.CTkFont(size=13),
            command=lambda: self.on_page(name)
        )
        btn.pack(fill="x", pady=2)