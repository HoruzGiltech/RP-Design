import re

from django.test import SimpleTestCase
from PIL import Image

from core.images import build_optimized, build_thumbnail
from core.tests.helpers import make_image_file
from core.uploads import build_unique_path

# Etiquetas EXIF: 0x0112 = orientación, 0x8825 = datos GPS
EXIF_ORIENTATION = 0x0112
EXIF_GPS = 0x8825
ROTATED_90 = 6


class ImageProcessingTests(SimpleTestCase):
    def test_big_image_is_reduced_to_1920(self):
        optimized = build_optimized(make_image_file(size=(4000, 3000)))

        self.assertEqual(Image.open(optimized).size, (1920, 1440))

    def test_thumbnail_is_reduced_to_600(self):
        thumbnail = build_thumbnail(make_image_file(size=(4000, 3000)))

        self.assertEqual(Image.open(thumbnail).size, (600, 450))

    def test_small_image_is_not_enlarged(self):
        optimized = build_optimized(make_image_file(size=(300, 200)))

        self.assertEqual(Image.open(optimized).size, (300, 200))

    def test_format_is_kept(self):
        png = build_optimized(make_image_file("foto.png", image_format="PNG"))
        webp = build_thumbnail(make_image_file("foto.webp", image_format="WEBP"))

        self.assertEqual(Image.open(png).format, "PNG")
        self.assertTrue(png.name.endswith(".png"))
        self.assertEqual(Image.open(webp).format, "WEBP")
        self.assertTrue(webp.name.endswith(".webp"))

    def test_exif_rotation_is_applied_and_metadata_is_removed(self):
        exif = Image.Exif()
        exif[EXIF_ORIENTATION] = ROTATED_90
        exif[EXIF_GPS] = {1: "N"}
        photo = make_image_file(size=(800, 600), exif=exif)

        optimized = Image.open(build_optimized(photo))

        # La foto estaba "acostada": al aplicar el giro queda de pie
        self.assertEqual(optimized.size, (600, 800))
        self.assertEqual(len(optimized.getexif()), 0)

    def test_original_file_can_be_read_again(self):
        photo = make_image_file()

        build_thumbnail(photo)

        self.assertEqual(photo.tell(), 0)


class UniquePathTests(SimpleTestCase):
    def test_path_has_folder_year_and_uuid(self):
        path = build_unique_path("projects", "Mi Foto (final).JPG")

        self.assertRegex(path, r"^projects/\d{4}/[0-9a-f]{32}\.jpg$")

    def test_original_name_is_not_used(self):
        path = build_unique_path("projects", "casa-de-ana.jpg")

        self.assertNotIn("casa", path)

    def test_two_files_with_the_same_name_get_different_paths(self):
        first = build_unique_path("projects", "foto.jpg")
        second = build_unique_path("projects", "foto.jpg")

        self.assertNotEqual(first, second)
        self.assertTrue(re.search(r"\.jpg$", second))
