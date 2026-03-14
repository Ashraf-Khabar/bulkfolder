from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

@dataclass
class UIState:
    """
    Maintains the global state of the application UI and shared components.
    """
    root: Path | None = None
    include_subfolders: bool = True
    find_text: str = ""
    replace_text: str = ""
    move_by_ext: bool = True
    large_files_root: Path | None = None
    renamer_root: Path | None = None
    flattener_root: Path | None = None
    dateorg_root: Path | None = None
    empty_folders_root: Path | None = None
    unzipper_root: Path | None = None
    pdf_root: Path | None = None
    chunker_root: Path | None = None
    
    # Reference to the central log view component
    log_view: Optional[Any] = None

    def log(self, message: str, level: str = "INFO") -> None:
        """
        Helper method to send logs to the UI terminal if available.
        """
        if self.log_view and hasattr(self.log_view, "log"):
            self.log_view.log(message, level)