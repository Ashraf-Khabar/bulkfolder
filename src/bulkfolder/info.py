import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import os

def get_project_info() -> dict:
    """
    Retrieves project metadata from project_info.xml.
    Handles path resolution for both development and PyInstaller environments.
    """
    # Default metadata fallback
    info = {
        "name": "BulkFolder",
        "version": "v1.5.0",
        "description": "Organize & Rename safely",
        "author": "Achraf KHABAR",
        "repository": "https://github.com/Ashraf-Khabar/bulkfolder"
    }
    
    try:
        # Determine the base directory
        # sys._MEIPASS is used by PyInstaller for bundled resources
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys._MEIPASS)
        else:
            # Navigate up from src/bulkfolder/info.py to the root
            base_dir = Path(__file__).resolve().parent.parent.parent

        xml_path = base_dir / "project_info.xml"
        
        if xml_path.exists():
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for child in root:
                info[child.tag] = child.text
        else:
            print(f"File not found: {xml_path}")
            
    except Exception as error:
        print(f"Failed to parse project_info.xml: {error}")
        
    return info