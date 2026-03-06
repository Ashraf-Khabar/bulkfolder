from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


def app_dir() -> Path:
    d = Path.home() / ".bulkfolder"
    d.mkdir(parents=True, exist_ok=True)
    return d


def presets_path() -> Path:
    return app_dir() / "presets.json"


def settings_path() -> Path:
    return app_dir() / "settings.json"


def read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@dataclass
class AppSettings:
    appearance_mode: str = "dark"          # "dark" | "light" | "system"
    autoscan_on_folder_select: bool = False
    duplicate_min_size_kb: int = 1         # ignore duplicates smaller than this
    default_page: str = "Organizer"        # Organizer/Presets/LargeFiles/Settings/About

    @staticmethod
    def from_dict(d: dict) -> "AppSettings":
        s = AppSettings()
        if isinstance(d, dict):
            s.appearance_mode = str(d.get("appearance_mode", s.appearance_mode))
            s.autoscan_on_folder_select = bool(d.get("autoscan_on_folder_select", s.autoscan_on_folder_select))
            s.duplicate_min_size_kb = int(d.get("duplicate_min_size_kb", s.duplicate_min_size_kb))
            s.default_page = str(d.get("default_page", s.default_page))
        return s

    def to_dict(self) -> dict:
        return asdict(self)


def load_settings() -> AppSettings:
    data = read_json(settings_path(), default={})
    return AppSettings.from_dict(data)


def save_settings(settings: AppSettings) -> None:
    write_json(settings_path(), settings.to_dict())