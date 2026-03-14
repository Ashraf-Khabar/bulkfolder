import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import os

def get_project_info() -> dict:
    """
    Retrieves project metadata from project_info.xml.
    Resolves paths correctly for development and PyInstaller environments.
    """
    # Fallback dictionary
    info = {
        "name": "BulkFolder",
        "version": "v1.7.10",
        "description": "Organize & Rename safely",
        "author": "Achraf KHABAR",
        "repository": "https://github.com/ZylosCore/bulkfolder"
    }
    
    try:
        # sys._MEIPASS is the temporary extraction folder for PyInstaller
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys._MEIPASS)
        else:
            # Development path
            base_dir = Path(__file__).resolve().parent.parent.parent

        xml_path = base_dir / "project_info.xml"
        
        if xml_path.exists():
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for child in root:
                info[child.tag] = child.text
        else:
            print(f"Project info file not found: {xml_path}")
            
    except Exception as error:
        print(f"Error while parsing metadata: {error}")
        
    return info