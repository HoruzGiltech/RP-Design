from django.test import SimpleTestCase

from site_content.services import format_whatsapp_number


class FormatWhatsappNumberTests(SimpleTestCase):
    def test_venezuelan_number_is_grouped(self):
        self.assertEqual(format_whatsapp_number("584127305964"), "+58 412 730 5964")

    def test_number_from_another_country_is_not_grouped(self):
        # No se inventa una agrupación que no se conoce
        self.assertEqual(format_whatsapp_number("34600111222"), "+34600111222")
        self.assertEqual(format_whatsapp_number("12125550123"), "+12125550123")

    def test_spaces_and_symbols_are_ignored(self):
        self.assertEqual(format_whatsapp_number("+58 412-730.5964"), "+58 412 730 5964")

    def test_empty_number_gives_empty_text(self):
        self.assertEqual(format_whatsapp_number(""), "")
        self.assertEqual(format_whatsapp_number(None), "")
