import shutil
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TestCase, override_settings


def table_exists():
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('media_transfer')")
        return cursor.fetchone()[0] is not None


class TransferMediaTests(TestCase):
    """Copia de los archivos subidos a través de la base de datos (specs-006, RF-54)."""

    def setUp(self):
        self.source = Path(tempfile.mkdtemp())
        self.destination = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.source, ignore_errors=True)
        self.addCleanup(shutil.rmtree, self.destination, ignore_errors=True)

    def run_command(self, action, media_root):
        with override_settings(MEDIA_ROOT=media_root):
            output = StringIO()
            call_command("transfer_media", action, stdout=output)
            return output.getvalue()

    def test_files_arrive_with_their_folders_and_content(self):
        (self.source / "projects" / "2026").mkdir(parents=True)
        (self.source / "projects" / "2026" / "foto.jpg").write_bytes(b"\xff\xd8 una foto")
        (self.source / "site").mkdir()
        (self.source / "site" / "video.mp4").write_bytes(b"un video")

        packed = self.run_command("pack", self.source)
        unpacked = self.run_command("unpack", self.destination)

        self.assertIn("2 archivos", packed)
        self.assertIn("2 archivos", unpacked)
        self.assertEqual(
            (self.destination / "projects" / "2026" / "foto.jpg").read_bytes(),
            b"\xff\xd8 una foto",
        )
        self.assertEqual((self.destination / "site" / "video.mp4").read_bytes(), b"un video")

    def test_package_is_removed_from_the_database_after_unpacking(self):
        (self.source / "foto.jpg").write_bytes(b"foto")

        self.run_command("pack", self.source)
        self.assertTrue(table_exists())
        self.run_command("unpack", self.destination)

        self.assertFalse(table_exists())

    def test_packing_twice_keeps_only_the_last_package(self):
        (self.source / "vieja.jpg").write_bytes(b"vieja")
        self.run_command("pack", self.source)
        (self.source / "vieja.jpg").unlink()
        (self.source / "nueva.jpg").write_bytes(b"nueva")
        self.run_command("pack", self.source)

        self.run_command("unpack", self.destination)

        self.assertEqual([path.name for path in self.destination.iterdir()], ["nueva.jpg"])

    def test_unpack_without_a_package_explains_what_to_do(self):
        with self.assertRaisesMessage(CommandError, "No hay ningún paquete esperando"):
            self.run_command("unpack", self.destination)

    def test_pack_without_files_does_not_send_anything(self):
        with self.assertRaisesMessage(CommandError, "No hay archivos"):
            self.run_command("pack", self.source)

        self.assertFalse(table_exists())
