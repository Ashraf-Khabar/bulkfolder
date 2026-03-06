from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .config import presets_path, read_json, write_json


@dataclass
class Preset:
    name: str
    include_subfolders: bool = True
    move_by_extension: bool = True
    find_text: str = ""
    replace_text: str = ""

    @staticmethod
    def from_dict(d: dict) -> "Preset":
        return Preset(
            name=str(d.get("name", "Unnamed")),
            include_subfolders=bool(d.get("include_subfolders", True)),
            move_by_extension=bool(d.get("move_by_extension", True)),
            find_text=str(d.get("find_text", "")),
            replace_text=str(d.get("replace_text", "")),
        )

    def to_dict(self) -> dict:
        return asdict(self)


def load_presets() -> list[Preset]:
    raw = read_json(presets_path(), default=[])
    if not isinstance(raw, list):
        return []
    out: list[Preset] = []
    for x in raw:
        if isinstance(x, dict):
            out.append(Preset.from_dict(x))
    return out


def save_presets(presets: list[Preset]) -> None:
    write_json(presets_path(), [p.to_dict() for p in presets])


def upsert_preset(preset: Preset) -> None:
    presets = load_presets()
    key = preset.name.strip().lower()
    presets = [p for p in presets if p.name.strip().lower() != key]
    presets.append(preset)
    presets.sort(key=lambda p: p.name.lower())
    save_presets(presets)


def delete_preset(name: str) -> bool:
    name = (name or "").strip()
    if not name:
        return False
    key = name.lower()

    presets = load_presets()
    new_list = [p for p in presets if p.name.strip().lower() != key]
    if len(new_list) == len(presets):
        return False
    save_presets(new_list)
    return True


def get_preset(name: str) -> Preset | None:
    key = (name or "").strip().lower()
    if not key:
        return None
    for p in load_presets():
        if p.name.strip().lower() == key:
            return p
    return None