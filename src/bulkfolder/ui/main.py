from __future__ import annotations
import sys
from .app import App

def main() -> None:
    # --- CORRECTION DE L'ICÔNE POUR LA BARRE DES TÂCHES WINDOWS ---
    # Permet de dissocier l'application de l'exécutable Python standard
    # et d'afficher correctement votre logo personnalisé.
    if sys.platform.startswith("win"):
        import ctypes
        try:
            myappid = "achrafkhabar.bulkfolder.app.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass
    # ---------------------------------------------------------------

    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()