from __future__ import annotations
import customtkinter as ctk
from datetime import datetime
from ..theme import DR_SURFACE, DR_TEXT, DR_MUTED, DR_BORDER, DR_PURPLE, DR_BG

class LogsView(ctk.CTkFrame):
    """
    A terminal-like log console with a black background and colored output.
    Optimized for fluidity.
    """
    def __init__(self, master, on_close=None, **kwargs):
        super().__init__(master, fg_color="#000000", corner_radius=8, border_width=1, border_color=DR_BORDER, **kwargs)
        self.on_close = on_close

        # Header bar
        self.header = ctk.CTkFrame(self, fg_color="#1a1b26", height=30, corner_radius=0)
        self.header.pack(fill="x", padx=0, pady=0)
        
        self.title_label = ctk.CTkLabel(
            self.header, 
            text=" SYSTEM TERMINAL ", 
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), 
            text_color="#7aa2f7"
        )
        self.title_label.pack(side="left", padx=10)

        self.close_btn = ctk.CTkButton(
            self.header,
            text="Collapse _",
            width=80,
            height=22,
            fg_color="#343b58",
            hover_color="#444b6a",
            text_color="#c0caf5",
            font=ctk.CTkFont(family="Consolas", size=10),
            command=self.on_close
        )
        self.close_btn.pack(side="right", padx=5, pady=4)

        # Text area
        self.text_area = ctk.CTkTextbox(
            self,
            fg_color="#000000",
            text_color="#c0caf5",
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
            border_width=0,
            height=160
        )
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.text_area.tag_config("timestamp", foreground="#565f89")
        self.text_area.tag_config("INFO", foreground="#7dcfff")
        self.text_area.tag_config("SUCCESS", foreground="#9ece6a") 
        self.text_area.tag_config("WARNING", foreground="#e0af68") 
        self.text_area.tag_config("ERROR", foreground="#f7768e")   
        self.text_area.tag_config("DEBUG", foreground="#bb9af7")   
        
        self.text_area.configure(state="disabled")

    def log(self, message: str, level: str = "INFO") -> None:
        """Appends a new log entry with buffer management for performance."""
        self.text_area.configure(state="normal")
        
        # OPTIMISATION: Limiter le nombre de lignes pour maintenir la fluidité
        line_count = int(self.text_area.index('end-1c').split('.')[0])
        if line_count > 500:
            self.text_area.delete("1.0", "2.0")

        timestamp = datetime.now().strftime("%H:%M:%S")
        level = level.upper()

        self.text_area.insert("end", f"[{timestamp}] ", "timestamp")
        self.text_area.insert("end", f"[{level}] ", level)
        self.text_area.insert("end", f"{message}\n")
            
        self.text_area.see("end")
        self.text_area.configure(state="disabled")

    def clear(self) -> None:
        """Clears the terminal."""
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.configure(state="disabled")