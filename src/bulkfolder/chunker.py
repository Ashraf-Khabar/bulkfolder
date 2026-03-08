from pathlib import Path

def plan_chunks(source_folder: Path, mode: str, max_val: float) -> list[dict]:
    """
    Simule la découpe d'un dossier.
    Retourne une liste de chunks : [{"name": "Part_1", "files": [Path, Path], "size": 1024}]
    """
    files = [f for f in source_folder.iterdir() if f.is_file()]
    # On trie par nom pour garder une suite logique (ex: photo_01, photo_02 dans le même chunk)
    files.sort(key=lambda x: x.name)
    
    chunks = []
    current_chunk = []
    current_size = 0
    current_count = 0
    chunk_idx = 1
    
    for f in files:
        size = f.stat().st_size
        
        if mode == "size":
            max_bytes = max_val * 1024 * 1024
            # Si ajouter ce fichier dépasse la limite (et que le chunk n'est pas vide)
            if current_size + size > max_bytes and current_chunk:
                chunks.append({"name": f"Part_{chunk_idx}", "files": current_chunk, "size": current_size})
                chunk_idx += 1
                current_chunk = []
                current_size = 0
        else:  # mode "count"
            if current_count >= max_val and current_chunk:
                chunks.append({"name": f"Part_{chunk_idx}", "files": current_chunk, "size": current_size})
                chunk_idx += 1
                current_chunk = []
                current_size = 0
                current_count = 0
        
        current_chunk.append(f)
        current_size += size
        current_count += 1
        
    # Ajouter le dernier chunk restant
    if current_chunk:
        chunks.append({"name": f"Part_{chunk_idx}", "files": current_chunk, "size": current_size})
        
    return chunks

def apply_chunks(source_folder: Path, chunks: list[dict]) -> tuple[int, list[str]]:
    """Déplace physiquement les fichiers dans les sous-dossiers."""
    success = 0
    errors = []
    
    for chunk in chunks:
        chunk_dir = source_folder / chunk["name"]
        try:
            chunk_dir.mkdir(exist_ok=True)
            for f in chunk["files"]:
                try:
                    f.rename(chunk_dir / f.name)
                    success += 1
                except Exception as e:
                    errors.append(f"{f.name}: {e}")
        except Exception as e:
            errors.append(f"Folder {chunk['name']}: {e}")
            
    return success, errors