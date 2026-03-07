from pathlib import Path
from PIL import Image

def convert_images_to_pdf(image_paths: list[Path], delete_original: bool = False) -> tuple[int, list[str]]:
    """
    Convertit une liste d'images en fichiers PDF individuels.
    Retourne le nombre de succès et une liste d'erreurs.
    """
    success_count = 0
    errors = []

    for path in image_paths:
        try:
            img = Image.open(path)
            pdf_path = path.with_suffix('.pdf')
            
            counter = 1
            while pdf_path.exists():
                pdf_path = path.with_name(f"{path.stem}_{counter}.pdf")
                counter += 1
            
            # CORRECTION : on force la conversion en string "str(pdf_path)"
            img.convert('RGB').save(str(pdf_path), "PDF", resolution=100.0)
            success_count += 1
            
            if delete_original:
                path.unlink()
                
        except Exception as e:
            errors.append(f"{path.name}: {e}")

    return success_count, errors