from decimal import Decimal

from django.test import SimpleTestCase

from quotes.models import Quote
from quotes.services import (
    build_whatsapp_link,
    build_whatsapp_message,
    clean_phone,
    format_square_meters,
    format_usd,
)

# Estos tests no tocan la base de datos: los modelos se crean en memoria, sin guardarlos.


def make_quote(**fields):
    values = {
        "name": "Ana Pérez",
        "email": "ana@mail.com",
        "phone": "+584121234567",
        "remodel_type": "cocina y baño",
        "location": "Chacao, Caracas",
        "square_meters": Decimal("45.5"),
        "message": "Quiero cambiar los gabinetes.",
    }
    values.update(fields)
    return Quote(**values)


class FormatTests(SimpleTestCase):
    def test_format_usd(self):
        # Se usa en el panel para el estimado de las cotizaciones anteriores
        self.assertEqual(format_usd(Decimal("1250.5")), "USD 1.250,50")
        self.assertEqual(format_usd(Decimal("0.5")), "USD 0,50")
        self.assertEqual(format_usd(Decimal("1234567.89")), "USD 1.234.567,89")
        self.assertEqual(format_usd(None), "A cotizar")

    def test_format_square_meters(self):
        self.assertEqual(format_square_meters(Decimal("12.50")), "12,5")
        self.assertEqual(format_square_meters(Decimal("30.00")), "30")
        self.assertEqual(format_square_meters(Decimal("7.25")), "7,25")
        self.assertEqual(format_square_meters(Decimal("1500")), "1.500")

    def test_clean_phone(self):
        self.assertEqual(clean_phone("+58 412-123 45 67"), "+584121234567")
        self.assertEqual(clean_phone("(0412) 123.45.67"), "04121234567")


class WhatsappMessageTests(SimpleTestCase):
    """El mensaje desde specs-008: tipo escrito por la persona, sin precios."""

    def test_message_includes_every_field(self):
        quote = make_quote(has_photos=True)

        self.assertEqual(
            build_whatsapp_message(quote),
            "Hola RP Design, quiero una cotización:\n"
            "\n"
            "- Nombre: Ana Pérez\n"
            "- Correo: ana@mail.com\n"
            "- Teléfono: +584121234567\n"
            "- Tipo de remodelación: cocina y baño\n"
            "- Ubicación: Chacao, Caracas\n"
            "- Metros cuadrados: 45,5 m²\n"
            "- Tengo fotos del espacio\n"
            "\n"
            "- Mensaje: Quiero cambiar los gabinetes.",
        )

    def test_message_has_no_price(self):
        message = build_whatsapp_message(make_quote())

        for text in ["USD", "Estimado", "A cotizar"]:
            self.assertNotIn(text, message)

    def test_message_has_no_emojis(self):
        quote = make_quote(has_photos=True, needs_visit=True)

        message = build_whatsapp_message(quote)

        # Todos los caracteres están en el plano básico de Unicode, donde no hay emojis
        self.assertTrue(all(ord(character) < 0x2000 for character in message))

    def test_optional_lines_are_left_out_when_empty(self):
        quote = make_quote(square_meters=None, message="")

        message = build_whatsapp_message(quote)

        for text in ["Metros", "fotos", "visita", "Mensaje"]:
            self.assertNotIn(text, message)
        self.assertTrue(message.endswith("- Ubicación: Chacao, Caracas"))

    def test_visit_request_goes_without_square_meters(self):
        quote = make_quote(square_meters=None, needs_visit=True, message="")

        message = build_whatsapp_message(quote)

        self.assertNotIn("Metros cuadrados", message)
        self.assertTrue(message.endswith("- No sé los m²: quiero agendar una visita"))


class WhatsappLinkTests(SimpleTestCase):
    def test_link_uses_the_number_and_encodes_the_message(self):
        link = build_whatsapp_link("584127305964", "Hola, ¿qué tal?\nSegunda línea & más")

        self.assertEqual(
            link,
            "https://wa.me/584127305964"
            "?text=Hola%2C%20%C2%BFqu%C3%A9%20tal%3F%0ASegunda%20l%C3%ADnea%20%26%20m%C3%A1s",
        )

    def test_number_is_cleaned(self):
        link = build_whatsapp_link("+58 412-730 5964", "Hola")

        self.assertEqual(link, "https://wa.me/584127305964?text=Hola")
