from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ReplaceTextRule:
    find: str
    replace: str

    def apply_name(self, name: str) -> str:
        if not self.find:
            return name
        return name.replace(self.find, self.replace)

@dataclass(frozen=True)
class MoveByExtensionRule:
    mapping: dict[str, str]
    default_folder: str = "Other"

    def target_subfolder(self, path: Path) -> str:
        ext = path.suffix.lower().lstrip(".")
        if not ext:
            return self.default_folder
        return self.mapping.get(ext, self.default_folder)
