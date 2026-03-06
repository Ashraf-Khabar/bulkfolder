# BulkFolder

BulkFolder is a desktop tool to **scan**, **preview**, **organize**, and **rename** files in bulk — safely.

## Features
- Scan folders (optional: include subfolders)
- Plan actions (move/rename) with preview
- Apply changes (safe)
- Undo last operations (journal-based)
- Dashboard with charts + top largest files
- Duplicate finder (SHA-256 grouping)

## Project structure
- `src/bulkfolder/` : backend (scanner/planner/executor/undo/duplicates)
- `src/bulkfolder/ui/` : CustomTkinter UI (dashboard app)
- `src/bulkfolder/ui/views/` : UI components

## Requirements
- Python 3.10+
- Windows recommended (works elsewhere too)

## Setup (dev)
```bash
python -m venv .venv
# Windows PowerShell:
. .venv\Scripts\Activate.ps1

pip install -r requirements.txt