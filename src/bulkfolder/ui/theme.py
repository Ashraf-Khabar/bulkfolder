import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".bulkfolder_config.json"

# Fonction pour lire le thème choisi par l'utilisateur
def _get_theme_name():
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("theme_name", "Dracula")
    except Exception:
        pass
    return "Dracula"

# Le dictionnaire contenant tous vos thèmes !
THEMES = {
    "Dracula": {"bg": "#282a36", "panel": "#282a36", "surface": "#1e1f29", "border": "#44475a", "text": "#f8f8f2", "muted": "#9aa0a6", "accent": "#6272a4", "accent_hover": "#7082b6", "purple": "#bd93f9"},
    "Tokyo Night": {"bg": "#1a1b26", "panel": "#16161e", "surface": "#24283b", "border": "#414868", "text": "#c0caf5", "muted": "#565f89", "accent": "#7aa2f7", "accent_hover": "#8db0f8", "purple": "#bb9af7"},
    "Catppuccin Mocha": {"bg": "#1e1e2e", "panel": "#181825", "surface": "#313244", "border": "#45475a", "text": "#cdd6f4", "muted": "#a6adc8", "accent": "#89b4fa", "accent_hover": "#b4befe", "purple": "#cba6f7"},
    "Obsidian Minimal": {"bg": "#0a0a0a", "panel": "#000000", "surface": "#111111", "border": "#333333", "text": "#ededed", "muted": "#888888", "accent": "#0070f3", "accent_hover": "#3291ff", "purple": "#7928ca"},
    "Nord": {"bg": "#2E3440", "panel": "#242933", "surface": "#3B4252", "border": "#4C566A", "text": "#ECEFF4", "muted": "#96A0B1", "accent": "#5E81AC", "accent_hover": "#81A1C1", "purple": "#B48EAD"},
    "Rosé Pine": {"bg": "#191724", "panel": "#12101B", "surface": "#1F1D2E", "border": "#26233A", "text": "#E0DEF4", "muted": "#908CAA", "accent": "#31748F", "accent_hover": "#9CCFD8", "purple": "#C4A7E7"},
    "Gruvbox Material": {"bg": "#282828", "panel": "#1D2021", "surface": "#32302F", "border": "#504945", "text": "#EBDBB2", "muted": "#A89984", "accent": "#458588", "accent_hover": "#83A598", "purple": "#D3869B"},
    "Midnight Executive": {"bg": "#0F1419", "panel": "#0B0E14", "surface": "#171D24", "border": "#2B3640", "text": "#E6EBF0", "muted": "#7A8C9E", "accent": "#C69F68", "accent_hover": "#E0BC84", "purple": "#8E729E"},
    "Monokai Pro": {"bg": "#2D2A2E", "panel": "#221F22", "surface": "#403E41", "border": "#5B595C", "text": "#FCFCFA", "muted": "#939293", "accent": "#FF6188", "accent_hover": "#FF8EAB", "purple": "#AB9DF2"},
    "Solarized Dark": {"bg": "#002b36", "panel": "#00212b", "surface": "#073642", "border": "#586e75", "text": "#839496", "muted": "#657b83", "accent": "#268bd2", "accent_hover": "#2aa198", "purple": "#d33682"}
}

# On sélectionne le thème actif
_active_theme = THEMES.get(_get_theme_name(), THEMES["Dracula"])

# On exporte les couleurs pour le reste de l'application
DR_BG = _active_theme["bg"]
DR_PANEL = _active_theme["panel"]
DR_SURFACE = _active_theme["surface"]
DR_BORDER = _active_theme["border"]
DR_TEXT = _active_theme["text"]
DR_MUTED = _active_theme["muted"]
DR_ACCENT = _active_theme["accent"]
DR_ACCENT_HOVER = _active_theme["accent_hover"]
DR_PURPLE = _active_theme["purple"]