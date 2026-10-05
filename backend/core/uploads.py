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


def file_has_changed(instance, field_name):
    """
    Dice si el archivo de un campo es nuevo o distinto del que está guardado.

    Sirve para procesar las imágenes solo al subirlas, y no cada vez que
    se guarda el registro por otro motivo (por ejemplo, al reordenar).
    """
    new_file = getattr(instance, field_name)
    if not new_file:
        return False
    if instance.pk is None:
        return True

    saved_name = (
        type(instance)
        .objects.filter(pk=instance.pk)
        .values_list(field_name, flat=True)
        .first()
    )
    return new_file.name != saved_name
