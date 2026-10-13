from django.test import SimpleTestCase

from projects.services import (
    build_base_slug,
    build_media_alt,
    make_unique_slug,
    match_category_name,
)

CATEGORY_NAMES = ["Comercial", "Residencial", "Corporativo"]


class BuildBaseSlugTests(SimpleTestCase):
    def test_title_with_several_words(self):
        self.assertEqual(build_base_slug("Remodelación de cocina"), "remodelacion-de-cocina")

    def test_single_word_title_gets_the_word_proyecto_first(self):
        self.assertEqual(build_base_slug("Casa"), "proyecto-casa")
        self.assertEqual(build_base_slug("  Baño  "), "proyecto-bano")

    def test_title_that_is_already_the_word_proyecto(self):
        self.assertEqual(build_base_slug("Proyecto"), "proyecto")

    def test_title_without_letters_or_numbers(self):
        self.assertEqual(build_base_slug("¿?"), "proyecto")
        self.assertEqual(build_base_slug(""), "proyecto")

    def test_symbols_and_capital_letters_are_cleaned(self):
        self.assertEqual(build_base_slug("Casa #2 (El Hatillo)"), "casa-2-el-hatillo")


class MakeUniqueSlugTests(SimpleTestCase):
    def test_free_slug_is_kept(self):
        self.assertEqual(make_unique_slug("proyecto-casa", set()), "proyecto-casa")

    def test_taken_slug_gets_a_number(self):
        self.assertEqual(make_unique_slug("proyecto-casa", {"proyecto-casa"}), "proyecto-casa-2")

    def test_number_grows_until_a_free_slug_is_found(self):
        existing = {"proyecto-casa", "proyecto-casa-2", "proyecto-casa-3"}

        self.assertEqual(make_unique_slug("proyecto-casa", existing), "proyecto-casa-4")


class MatchCategoryNameTests(SimpleTestCase):
    """La usa la migración que convierte el texto antiguo de categoría en una relación."""

    def test_finds_the_category_inside_a_longer_text(self):
        self.assertEqual(
            match_category_name("Fachada · Residencial", CATEGORY_NAMES), "Residencial"
        )

    def test_ignores_capital_letters_and_accents(self):
        self.assertEqual(match_category_name("OBRA COMERCIAL", CATEGORY_NAMES), "Comercial")
        self.assertEqual(match_category_name("corporatívo", CATEGORY_NAMES), "Corporativo")

    def test_text_without_any_category_gives_none(self):
        self.assertIsNone(match_category_name("Diseño · Interior", CATEGORY_NAMES))
        self.assertIsNone(match_category_name("", CATEGORY_NAMES))
        self.assertIsNone(match_category_name(None, CATEGORY_NAMES))


class MediaAltTests(SimpleTestCase):
    """Texto alternativo automático de la galería (specs-007, RF-57)."""

    def test_project_name_and_a_three_digit_number(self):
        self.assertEqual(build_media_alt("Apto La Guaira", 1), "Apto La Guaira 001")
        self.assertEqual(build_media_alt("Apto La Guaira", 12), "Apto La Guaira 012")
        self.assertEqual(build_media_alt("Casa", 120), "Casa 120")
