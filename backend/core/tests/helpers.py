"""Archivos de prueba que se crean en memoria (no hace falta guardar fotos en el repo)."""
import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

# Comienzo de un archivo MP4 real: tamaño de la caja, "ftyp" y la marca "isom"
MP4_HEADER = b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2"
# Comienzo de un programa de Windows (.exe)
EXE_HEADER = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff"


class TempMediaMixin:
    """
    Hace que los tests guarden los archivos en una carpeta temporal,
    que se borra al terminar. Así no se ensucia la carpeta media/ real.
    """

    @classmethod
    def setUpClass(cls):
        cls._media_dir = tempfile.mkdtemp()
        cls._media_override = override_settings(MEDIA_ROOT=cls._media_dir)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls._media_dir, ignore_errors=True)


def make_image_file(name="foto.jpg", size=(800, 600), image_format="JPEG", exif=None):
    """Crea una imagen de un solo color del tamaño pedido."""
    buffer = BytesIO()
    image = Image.new("RGB", size, color=(120, 90, 60))
    options = {"exif": exif} if exif else {}
    image.save(buffer, format=image_format, **options)
    return SimpleUploadedFile(name, buffer.getvalue())


def make_video_file(name="video.mp4", extra_bytes=1024):
    """Crea un archivo que empieza como un MP4 real, relleno con ceros."""
    return SimpleUploadedFile(name, MP4_HEADER + b"\x00" * extra_bytes)


def make_fake_file(name):
    """Crea un .exe con el nombre que se le pida (para simular un archivo disfrazado)."""
    return SimpleUploadedFile(name, EXE_HEADER + b"\x00" * 1024)


def make_font_file(name="fuente.woff2", signature=b"wOF2", extra_bytes=1024):
    """Crea un archivo que empieza con la firma de una fuente real, relleno con ceros."""
    return SimpleUploadedFile(name, signature + b"\x00" * extra_bytes)
