import json
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_PATH = Path.home() / ".bulkfolder_config.json"

@dataclass
class AppSettings:
    theme_name: str = "Dracula"
    ui_scaling: str = "100%"
    autoscan_on_folder_select: bool = True
    ask_confirmations: bool = True
    duplicate_min_size_kb: int = 1
    default_page: str = "Organizer"

def load_settings() -> AppSettings:
    if not CONFIG_PATH.exists():
        return AppSettings()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            valid_keys = {k for k in AppSettings.__dataclass_fields__}
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return AppSettings(**filtered_data)
    except Exception:
        return AppSettings()

def save_settings(settings: AppSettings):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(asdict(settings), f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des paramètres: {e}")