"""
Lleva los archivos subidos (fotos, videos y fuentes) de un servidor a otro
usando la base de datos como medio de transporte (specs-006, RF-54).

Hace falta porque al volumen de Railway no se le pueden copiar archivos
directamente desde una computadora. Se usa en dos pasos:

  1. En la computadora de origen, apuntando a la base de datos de destino:
         python manage.py transfer_media pack
     Empaqueta la carpeta media/ y la guarda en una tabla temporal.

  2. En el servidor de destino:
         python manage.py transfer_media unpack
     Saca los archivos a su carpeta media/ y borra la tabla temporal.

Es una herramienta de un solo uso: no forma parte del sitio.
"""
import io
import tarfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

TABLE = "media_transfer"
BYTES_PER_MB = 1024 * 1024


class Command(BaseCommand):
    help = "Lleva los archivos de media/ a otro servidor a través de la base de datos."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["pack", "unpack"])

    def handle(self, *args, **options):
        if options["action"] == "pack":
            self.pack()
        else:
            self.unpack()

    def pack(self):
        media_root = Path(settings.MEDIA_ROOT)
        files = [path for path in media_root.rglob("*") if path.is_file()]
        if not files:
            raise CommandError(f"No hay archivos en {media_root}.")

        # Todos los archivos van en un solo paquete comprimido, en memoria
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            for path in files:
                archive.add(path, arcname=path.relative_to(media_root).as_posix())
        package = buffer.getvalue()

        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {TABLE}")
            cursor.execute(f"CREATE TABLE {TABLE} (package bytea NOT NULL)")
            cursor.execute(f"INSERT INTO {TABLE} (package) VALUES (%s)", [package])

        size = len(package) / BYTES_PER_MB
        self.stdout.write(
            self.style.SUCCESS(f"{len(files)} archivos empaquetados ({size:.1f} MB) y enviados.")
        )

    def unpack(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass(%s)", [TABLE])
            if cursor.fetchone()[0] is None:
                raise CommandError(
                    "No hay ningún paquete esperando. Ejecuta primero "
                    '"transfer_media pack" en la computadora de origen.'
                )
            cursor.execute(f"SELECT package FROM {TABLE}")
            package = bytes(cursor.fetchone()[0])

        media_root = Path(settings.MEDIA_ROOT)
        media_root.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(package), mode="r:gz") as archive:
            count = len(archive.getmembers())
            # filter="data": no permite que el paquete escriba fuera de la carpeta
            archive.extractall(media_root, filter="data")

        # El paquete ya cumplió su función: no se deja ocupando sitio en la base
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE {TABLE}")

        self.stdout.write(self.style.SUCCESS(f"{count} archivos copiados a {media_root}."))
