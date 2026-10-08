from decimal import Decimal

from django.test import SimpleTestCase

from projects.models import ProjectCategory
from quotes.models import Quote, RemodelArea
from quotes.services import (
    area_belongs_to_category,
    build_whatsapp_link,
    build_whatsapp_message,
    calculate_estimate,
    clean_phone,
    format_square_meters,
    format_usd,
)

# Estos tests no tocan la base de datos: los modelos se crean en memoria, sin guardarlos.


def make_quote(**fields):
    area = fields.pop("area", RemodelArea(name="Cocina", price_per_m2=Decimal("100")))
    values = {
        "name": "Ana Pérez",
        "email": "ana@mail.com",
        "phone": "+584121234567",
        "category_name": "Residencial",
        "area": area,
        "square_meters": Decimal("12.5"),
        "estimated_price": Decimal("1250.00"),
        "message": "Quiero cambiar los gabinetes.",
    }
    values.update(fields)
    return Quote(**values)


class CalculateEstimateTests(SimpleTestCase):
    def test_multiplies_square_meters_by_the_area_price(self):
        area = RemodelArea(name="Cocina", price_per_m2=Decimal("100"))

        estimate = calculate_estimate(area, Decimal("12.5"))

        self.assertEqual(estimate, Decimal("1250.00"))
        self.assertEqual(format_usd(estimate), "USD 1.250,00")

    def test_result_is_rounded_to_two_decimals(self):
        area = RemodelArea(name="Baño", price_per_m2=Decimal("33.33"))

        self.assertEqual(calculate_estimate(area, Decimal("3.33")), Decimal("110.99"))

    def test_area_without_price_has_no_estimate(self):
        area = RemodelArea(name="Otro", price_per_m2=None, is_other=True)

        estimate = calculate_estimate(area, Decimal("20"))

        self.assertIsNone(estimate)
        self.assertEqual(format_usd(estimate), "A cotizar")


class AreaBelongsToCategoryTests(SimpleTestCase):
    def test_area_of_the_same_category(self):
        category = ProjectCategory(pk=1, name="Residencial")
        area = RemodelArea(name="Cocina", category=category)

        self.assertTrue(area_belongs_to_category(area, category))

    def test_area_of_another_category(self):
        residential = ProjectCategory(pk=1, name="Residencial")
        corporate = ProjectCategory(pk=2, name="Corporativo")
        area = RemodelArea(name="Cocina", category=residential)

        self.assertFalse(area_belongs_to_category(area, corporate))

    def test_area_without_category_belongs_to_every_type(self):
        corporate = ProjectCategory(pk=2, name="Corporativo")
        other = RemodelArea(name="Otro", is_other=True)

        self.assertTrue(area_belongs_to_category(other, corporate))


class FormatTests(SimpleTestCase):
    def test_format_usd(self):
        self.assertEqual(format_usd(Decimal("1250.5")), "USD 1.250,50")
        self.assertEqual(format_usd(Decimal("0.5")), "USD 0,50")
        self.assertEqual(format_usd(Decimal("999")), "USD 999,00")
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
    def test_message_includes_every_field(self):
        message = build_whatsapp_message(make_quote())

        self.assertEqual(
            message,
            "Hola RP Design, quiero una cotización:\n"
            "\n"
            "👤 Nombre: Ana Pérez\n"
            "📧 Correo: ana@mail.com\n"
            "📱 Teléfono: +584121234567\n"
            "🏗️ Tipo: Residencial\n"
            "🏠 Área: Cocina\n"
            "📐 Metros cuadrados: 12,5 m²\n"
            "💲 Estimado: USD 1.250,00\n"
            "\n"
            "💬 Mensaje: Quiero cambiar los gabinetes.",
        )

    def test_type_line_is_left_out_in_quotes_without_type(self):
        # Las cotizaciones anteriores a specs-002 no tienen tipo de remodelación
        message = build_whatsapp_message(make_quote(category_name=""))

        self.assertNotIn("Tipo", message)
        self.assertIn("📱 Teléfono: +584121234567\n🏠 Área: Cocina", message)

    def test_message_line_is_left_out_when_empty(self):
        message = build_whatsapp_message(make_quote(message=""))

        self.assertNotIn("Mensaje", message)
        self.assertTrue(message.endswith("💲 Estimado: USD 1.250,00"))

    def test_other_area_shows_what_the_person_wrote(self):
        other = RemodelArea(name="Otro", is_other=True)
        quote = make_quote(area=other, area_other="Terraza", estimated_price=None)

        message = build_whatsapp_message(quote)

        self.assertIn("🏠 Área: Otro: Terraza", message)
        self.assertIn("💲 Estimado: A cotizar", message)


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
