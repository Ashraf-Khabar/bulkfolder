import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import os

def get_project_info() -> dict:
    """
    Reads project_info.xml from the project root to retrieve version and configuration.
    Supports both development environment and compiled executable paths.
    """
    # Default fallback information
    info = {
        "name": "BulkFolder",
        "version": "v1.7.10",
        "description": "Organize & Rename safely",
        "author": "Achraf KHABAR",
        "repository": "https://github.com/ZylosCore/bulkfolder"
    }
    
    try:
        # Check if the application is running as a bundled executable
        if getattr(sys, 'frozen', False):
            # If frozen, the base path is the temporary folder created by the executable
            base_path = Path(sys._MEIPASS)
        else:
            # If in development, move up from src/bulkfolder/info.py to the root
            base_path = Path(__file__).resolve().parent.parent.parent

        xml_path = base_path / "project_info.xml"
        
        if xml_path.exists():
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for child in root:
                info[child.tag] = child.text
        else:
            print(f"Warning: project_info.xml not found at {xml_path}")
            
    except Exception as e:
        print(f"Error reading XML file: {e}")
        
    return info