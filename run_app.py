import sys
import os

# Ajoute le dossier src au chemin de recherche de Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Lance l'application proprement
from bulkfolder.ui.main import main
if __name__ == "__main__":
    main()