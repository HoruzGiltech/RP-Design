"""
Procesamiento de imágenes con Pillow.

Las fotos del cliente suelen venir del celular: pesan mucho, a veces están
giradas y guardan datos como la ubicación GPS. Aquí se dejan listas para la web.
"""
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

OPTIMIZED_MAX_SIDE = 1920
THUMBNAIL_MAX_SIDE = 600
QUALITY = 82

# Extensión con la que se guarda cada formato
EXTENSION_BY_FORMAT = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}


def resize_image(file, max_side):
    """
    Devuelve una copia de la imagen cuyo lado mayor mide como máximo `max_side`.

    El resultado es un ContentFile listo para guardar en un ImageField.
    Su nombre es solo provisional ("image.jpg"): el nombre definitivo lo pone
    el campo del modelo con `upload_to`.
    """
    file.seek(0)
    image = Image.open(file)
    image_format = image.format

    # Aplica el giro que indica el celular y descarta ese dato
    image = ImageOps.exif_transpose(image)

    # thumbnail() solo achica: una imagen pequeña no se agranda
    image.thumbnail((max_side, max_side))

    # JPEG no admite transparencia ni paletas de color
    if image_format == "JPEG" and image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    # Al guardar sin pasar los metadatos, se pierden (incluida la ubicación GPS)
    buffer = BytesIO()
    image.save(buffer, format=image_format, quality=QUALITY, optimize=True)
    file.seek(0)

    extension = EXTENSION_BY_FORMAT[image_format]
    return ContentFile(buffer.getvalue(), name=f"image.{extension}")


def build_optimized(file):
    """Versión para mostrar en grande (máx. 1920 px)."""
    return resize_image(file, OPTIMIZED_MAX_SIDE)


def build_thumbnail(file):
    """Miniatura para las cuadrículas (máx. 600 px)."""
    return resize_image(file, THUMBNAIL_MAX_SIDE)
