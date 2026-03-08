from __future__ import annotations
import customtkinter as ctk

from ..theme import DR_BG, DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED, DR_ACCENT


class AboutPage(ctk.CTkFrame):
    def __init__(self, master, project_info: dict, on_open_github):
        super().__init__(master, corner_radius=0, fg_color=DR_BG)

        # On centre tout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # La carte principale
        card = ctk.CTkFrame(self, corner_radius=16, fg_color=DR_SURFACE, border_color=DR_BORDER, border_width=1)
        card.grid(row=0, column=0, sticky="nsew", padx=60, pady=60)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        # Le conteneur interne pour regrouper le texte au centre de la carte
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=0, column=0)

        # Nom de l'app
        app_name = project_info.get("name", "BulkFolder")
        ctk.CTkLabel(inner, text=app_name, font=ctk.CTkFont(size=36, weight="bold"), text_color=DR_TEXT).pack(pady=(0, 5))
        
        # Version (en couleur Accent pour ressortir)
        version = project_info.get("version", "1.0.0")
        ctk.CTkLabel(inner, text=f"Version {version}", font=ctk.CTkFont(size=14, weight="bold"), text_color=DR_ACCENT).pack(pady=(0, 24))

        # Description
        desc = project_info.get("description", "")
        ctk.CTkLabel(inner, text=desc, font=ctk.CTkFont(size=14), text_color=DR_MUTED, wraplength=400, justify="center").pack(pady=(0, 36))

        # Bouton GitHub (Avec l'emoji pieuvre ou un beau bouton sombre)
        repo_url = project_info.get("repository", "")
        self.btn_github = ctk.CTkButton(
            inner,
            text=" 🐙   View GitHub Repository",
            command=lambda: on_open_github(repo_url),
            fg_color="#24292e",          # Couleur officielle GitHub sombre
            hover_color="#1b1f23",       # Survol GitHub
            text_color="#ffffff",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            width=220,
            corner_radius=8
        )
        self.btn_github.pack(pady=(0, 30))

        # Crédits
        author = project_info.get("author", "Community")

        ctk.CTkLabel(inner, text=f"Developed by {author}", font=ctk.CTkFont(size=12), text_color=DR_MUTED).pack()
