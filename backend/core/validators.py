"""
Validación de los archivos que sube el cliente desde el panel.

Cada archivo pasa tres controles: extensión, tamaño y contenido real.
El tercero evita que alguien suba, por ejemplo, un .exe renombrado a .jpg.
"""
from pathlib import Path

import filetype
from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]
VIDEO_EXTENSIONS = ["mp4", "webm"]
FONT_EXTENSIONS = ["woff2", "woff", "ttf", "otf"]

# Formatos que Pillow debe reconocer al abrir una imagen permitida
IMAGE_FORMATS = ["JPEG", "PNG", "WEBP"]
# Tipos que la librería filetype debe reconocer en un video permitido
VIDEO_MIME_TYPES = ["video/mp4", "video/webm"]

# Primeros 4 bytes de cada formato de fuente. Es su "firma": con ella se sabe
# qué es el archivo de verdad, diga lo que diga su extensión.
FONT_SIGNATURES = [
    b"wOF2",  # woff2
    b"wOFF",  # woff
    b"OTTO",  # otf
    b"\x00\x01\x00\x00",  # ttf
    b"true",  # ttf de Apple
]

BYTES_PER_MB = 1024 * 1024
# filetype solo necesita el comienzo del archivo para reconocerlo
HEADER_BYTES = 8192


def get_extension(file):
    """Devuelve la extensión en minúsculas y sin punto: 'Foto.JPG' -> 'jpg'."""
    return Path(file.name).suffix.lower().lstrip(".")


def _check_extension(file, allowed_extensions):
    if get_extension(file) not in allowed_extensions:
        allowed = ", ".join(allowed_extensions)
        raise ValidationError(f"Formato no permitido. Usa uno de estos: {allowed}.")


def _check_size(file, max_mb):
    if file.size > max_mb * BYTES_PER_MB:
        raise ValidationError(f"El archivo es muy pesado. El máximo es {max_mb} MB.")


def _check_image_content(file):
    try:
        image = Image.open(file)
        image_format = image.format
        # verify() lee el archivo completo y falla si está dañado o no es una imagen
        image.verify()
    except Exception:
        raise ValidationError("El archivo no es una imagen válida.")
    finally:
        # Se vuelve al inicio para que quien use el archivo después lo lea completo
        file.seek(0)

    if image_format not in IMAGE_FORMATS:
        raise ValidationError("El archivo no es una imagen válida.")


def _check_video_content(file):
    header = file.read(HEADER_BYTES)
    file.seek(0)

    kind = filetype.guess(header)
    if kind is None or kind.mime not in VIDEO_MIME_TYPES:
        raise ValidationError("El archivo no es un video válido.")


def validate_image_file(file):
    """Valida una imagen: jpg, jpeg, png o webp, hasta MAX_IMAGE_MB."""
    _check_extension(file, IMAGE_EXTENSIONS)
    _check_size(file, settings.MAX_IMAGE_MB)
    _check_image_content(file)


def validate_video_file(file):
    """Valida un video: mp4 o webm, hasta MAX_VIDEO_MB."""
    _check_extension(file, VIDEO_EXTENSIONS)
    _check_size(file, settings.MAX_VIDEO_MB)
    _check_video_content(file)


def _check_font_content(file):
    signature = file.read(4)
    file.seek(0)
    if signature not in FONT_SIGNATURES:
        raise ValidationError("El archivo no es una fuente válida.")


def validate_font_file(file):
    """Valida una fuente: woff2, woff, ttf u otf, hasta MAX_FONT_MB."""
    _check_extension(file, FONT_EXTENSIONS)
    _check_size(file, settings.MAX_FONT_MB)
    _check_font_content(file)


def validate_media_file(file):
    """Valida un archivo de galería, que puede ser imagen o video."""
    if get_extension(file) in VIDEO_EXTENSIONS:
        validate_video_file(file)
    else:
        # Cualquier otra extensión cae aquí y falla con el mensaje de formatos
        _check_extension(file, IMAGE_EXTENSIONS + VIDEO_EXTENSIONS)
        validate_image_file(file)
