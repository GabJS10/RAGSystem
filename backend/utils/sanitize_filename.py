import re

def sanitize_filename(filename: str) -> str:
    # Reemplazar espacios por guiones bajos
    filename = filename.replace(" ", "_")
    # Quitar acentos y caracteres especiales
    filename = re.sub(r"[^a-zA-Z0-9._-]", "", filename)
    return filename
