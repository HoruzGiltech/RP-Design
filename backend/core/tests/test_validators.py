from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, override_settings

from core.tests.helpers import make_fake_file, make_font_file, make_image_file, make_video_file
from core.validators import (
    validate_font_file,
    validate_image_file,
    validate_media_file,
    validate_video_file,
)


class ImageValidatorTests(SimpleTestCase):
    def test_valid_images_are_accepted(self):
        validate_image_file(make_image_file("foto.jpg", image_format="JPEG"))
        validate_image_file(make_image_file("foto.png", image_format="PNG"))
        validate_image_file(make_image_file("foto.webp", image_format="WEBP"))

    def test_extension_is_checked_without_caring_about_case(self):
        validate_image_file(make_image_file("FOTO.JPG"))

    def test_extension_not_allowed_is_rejected(self):
        with self.assertRaisesMessage(ValidationError, "Formato no permitido"):
            validate_image_file(make_image_file("foto.gif", image_format="GIF"))

    def test_exe_renamed_to_jpg_is_rejected(self):
        with self.assertRaisesMessage(ValidationError, "no es una imagen válida"):
            validate_image_file(make_fake_file("foto.jpg"))

    def test_image_with_wrong_real_format_is_rejected(self):
        # Un GIF real con extensión .jpg: es imagen, pero no de un formato permitido
        with self.assertRaisesMessage(ValidationError, "no es una imagen válida"):
            validate_image_file(make_image_file("foto.jpg", image_format="GIF"))

    @override_settings(MAX_IMAGE_MB=1)
    def test_too_big_image_is_rejected_with_the_limit_in_the_message(self):
        big_file = make_fake_file("foto.jpg")
        big_file.size = 2 * 1024 * 1024

        with self.assertRaisesMessage(ValidationError, "El máximo es 1 MB"):
            validate_image_file(big_file)

    def test_file_can_be_read_again_after_validation(self):
        image_file = make_image_file()

        validate_image_file(image_file)

        self.assertEqual(image_file.tell(), 0)


class VideoValidatorTests(SimpleTestCase):
    def test_valid_mp4_is_accepted(self):
        validate_video_file(make_video_file("video.mp4"))

    def test_exe_renamed_to_mp4_is_rejected(self):
        with self.assertRaisesMessage(ValidationError, "no es un video válido"):
            validate_video_file(make_fake_file("video.mp4"))

    def test_image_extension_is_rejected_as_video(self):
        with self.assertRaisesMessage(ValidationError, "Formato no permitido"):
            validate_video_file(make_image_file("foto.jpg"))

    @override_settings(MAX_VIDEO_MB=1)
    def test_too_big_video_is_rejected_with_the_limit_in_the_message(self):
        big_file = make_video_file(extra_bytes=2 * 1024 * 1024)

        with self.assertRaisesMessage(ValidationError, "El máximo es 1 MB"):
            validate_video_file(big_file)


class MediaValidatorTests(SimpleTestCase):
    """La galería acepta imágenes y videos en el mismo campo."""

    def test_accepts_image_and_video(self):
        validate_media_file(make_image_file("foto.png", image_format="PNG"))
        validate_media_file(make_video_file("video.mp4"))

    def test_rejects_other_extensions(self):
        with self.assertRaisesMessage(ValidationError, "Formato no permitido"):
            validate_media_file(make_fake_file("programa.exe"))

    def test_rejects_exe_renamed_to_video(self):
        with self.assertRaisesMessage(ValidationError, "no es un video válido"):
            validate_media_file(make_fake_file("video.webm"))


class FontValidatorTests(SimpleTestCase):
    """Fuentes que el cliente carga desde el panel (specs-003, RF-19)."""

    def test_every_allowed_format_is_accepted(self):
        validate_font_file(make_font_file("fuente.woff2", b"wOF2"))
        validate_font_file(make_font_file("fuente.woff", b"wOFF"))
        validate_font_file(make_font_file("fuente.otf", b"OTTO"))
        validate_font_file(make_font_file("fuente.ttf", b"\x00\x01\x00\x00"))
        validate_font_file(make_font_file("FUENTE.TTF", b"true"))

    def test_extension_not_allowed_is_rejected(self):
        with self.assertRaisesMessage(ValidationError, "Formato no permitido"):
            validate_font_file(make_font_file("fuente.eot", b"wOF2"))

    def test_exe_renamed_to_font_is_rejected(self):
        with self.assertRaisesMessage(ValidationError, "no es una fuente válida"):
            validate_font_file(make_fake_file("fuente.woff2"))

    @override_settings(MAX_FONT_MB=1)
    def test_too_big_font_is_rejected_with_the_limit_in_the_message(self):
        big_font = make_font_file(extra_bytes=2 * 1024 * 1024)

        with self.assertRaisesMessage(ValidationError, "El máximo es 1 MB"):
            validate_font_file(big_font)

    def test_file_can_be_read_again_after_validation(self):
        font = make_font_file()

        validate_font_file(font)

        self.assertEqual(font.tell(), 0)
