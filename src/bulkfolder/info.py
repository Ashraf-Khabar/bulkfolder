import xml.etree.ElementTree as ET
from pathlib import Path

def get_project_info() -> dict:
    """Lit le fichier project_info.xml à la racine pour récupérer la version et la config."""
    info = {
        "name": "BulkFolder",
        "version": "v1.5.0",
        "description": "Organize & Rename safely",
        "author": "Achraf KHABAR",
        "repository": "https://github.com/Ashraf-Khabar/bulkfolder"
    }
    
    try:
        # On remonte de src/bulkfolder/info.py jusqu'à la racine du projet
        xml_path = Path(__file__).resolve().parent.parent.parent / "project_info.xml"
        
        if xml_path.exists():
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for child in root:
                info[child.tag] = child.text
    except Exception as e:
        print(f"Erreur de lecture du XML : {e}")
        
    return info