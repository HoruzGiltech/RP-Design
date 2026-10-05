"""Nombres de los archivos subidos."""
import uuid
from pathlib import Path

from django.utils import timezone


def build_unique_path(folder, filename):
    """
    Devuelve una ruta nueva para el archivo: '<folder>/<año>/<uuid>.<ext>'.

    Nunca se usa el nombre original: puede traer espacios, caracteres raros
    o repetirse, y además dice cosas del cliente que no hace falta publicar.
    """
    extension = Path(filename).suffix.lower()
    year = timezone.now().year
    return f"{folder}/{year}/{uuid.uuid4().hex}{extension}"
