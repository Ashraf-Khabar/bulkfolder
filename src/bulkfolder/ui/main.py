from __future__ import annotations
import sys
import ctypes
from .app import App

def main() -> None:
    """
    Main entry point for the BulkFolder application.
    Includes Windows-specific fixes for taskbar icons and app identification.
    """
    # --- WINDOWS APP USER MODEL ID ---
    # This helps Windows distinguish the app from a generic Python process.
    # Format: CompanyName.ProductName.SubProduct.Version
    if sys.platform.startswith("win"):
        try:
            myappid = "Zyloscore.BulkFolder.Organizer.1.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass
    # ----------------------------------

    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()