from decimal import Decimal

from django.test import SimpleTestCase

from projects.models import ProjectCategory
from quotes.models import Quote, QuoteItem, RemodelArea
from quotes.services import (
    area_belongs_to_category,
    build_whatsapp_link,
    build_whatsapp_message,
    calculate_estimate,
    calculate_total,
    clean_phone,
    describe_item,
    format_square_meters,
    format_usd,
)

# Estos tests no tocan la base de datos: los modelos se crean en memoria, sin guardarlos.


KITCHEN = RemodelArea(name="Cocina", price_per_m2=Decimal("100"))
BATHROOM = RemodelArea(name="Baño", price_per_m2=Decimal("50"))
OTHER = RemodelArea(name="Otro", is_other=True)


def make_quote(**fields):
    values = {
        "name": "Ana Pérez",
        "email": "ana@mail.com",
        "phone": "+584121234567",
        "category_name": "Residencial",
        "estimated_price": Decimal("1250.00"),
        "message": "Quiero cambiar los gabinetes.",
    }
    values.update(fields)
    return Quote(**values)


def make_item(area=KITCHEN, square_meters=Decimal("12.5"), area_other=""):
    """Un renglón con su subtotal ya calculado, como lo arma la vista."""
    return QuoteItem(
        area=area,
        area_other=area_other,
        square_meters=square_meters,
        subtotal=calculate_estimate(area, square_meters),
    )


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

    def test_without_square_meters_there_is_no_estimate(self):
        # La persona pidió una visita porque no sabe los metros
        self.assertIsNone(calculate_estimate(KITCHEN, None))


class CalculateTotalTests(SimpleTestCase):
    """El estimado es la suma de todas las áreas (specs-003, RF-27)."""

    def test_adds_every_subtotal(self):
        total = calculate_total([Decimal("1000.00"), Decimal("400.50")])

        self.assertEqual(total, Decimal("1400.50"))

    def test_one_area_to_be_quoted_makes_the_whole_total_to_be_quoted(self):
        self.assertIsNone(calculate_total([Decimal("1000.00"), None]))

    def test_without_areas_there_is_no_total(self):
        self.assertIsNone(calculate_total([]))


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


class DescribeItemTests(SimpleTestCase):
    def test_area_with_meters_and_price(self):
        self.assertEqual(describe_item(make_item()), "Cocina: 12,5 m² (USD 1.250,00)")

    def test_other_area_shows_what_the_person_wrote(self):
        item = make_item(area=OTHER, square_meters=Decimal("8"), area_other="Terraza")

        self.assertEqual(describe_item(item), "Otro (Terraza): 8 m² (A cotizar)")

    def test_price_is_left_out_when_the_estimate_is_hidden(self):
        self.assertEqual(describe_item(make_item(), show_estimate=False), "Cocina: 12,5 m²")

    def test_without_meters_only_the_name_is_shown(self):
        self.assertEqual(describe_item(make_item(square_meters=None)), "Cocina")


class WhatsappMessageTests(SimpleTestCase):
    def test_message_includes_every_field(self):
        quote = make_quote(location="Chacao, Caracas", has_photos=True)

        message = build_whatsapp_message(quote, [make_item()])

        self.assertEqual(
            message,
            "Hola RP Design, quiero una cotización:\n"
            "\n"
            "- Nombre: Ana Pérez\n"
            "- Correo: ana@mail.com\n"
            "- Teléfono: +584121234567\n"
            "- Ubicación: Chacao, Caracas\n"
            "- Tipo: Residencial\n"
            "- Áreas:\n"
            "  - Cocina: 12,5 m² (USD 1.250,00)\n"
            "- Estimado total: USD 1.250,00\n"
            "- Tengo fotos del espacio\n"
            "\n"
            "- Mensaje: Quiero cambiar los gabinetes.",
        )

    def test_message_has_no_emojis(self):
        # specs-003, RF-28: algunos WhatsApp los mostraban como "?"
        quote = make_quote(location="Chacao", has_photos=True, needs_visit=True)

        message = build_whatsapp_message(quote, [make_item(), make_item(area=OTHER)])

        # Todos los caracteres están en el plano básico de Unicode, donde no hay emojis
        self.assertTrue(all(ord(character) < 0x2000 for character in message))

    def test_every_area_has_its_own_line(self):
        items = [
            make_item(),
            make_item(area=BATHROOM, square_meters=Decimal("4")),
            make_item(area=OTHER, square_meters=Decimal("8"), area_other="Terraza"),
        ]

        message = build_whatsapp_message(make_quote(estimated_price=None), items)

        self.assertIn(
            "- Áreas:\n"
            "  - Cocina: 12,5 m² (USD 1.250,00)\n"
            "  - Baño: 4 m² (USD 200,00)\n"
            "  - Otro (Terraza): 8 m² (A cotizar)\n"
            "- Estimado total: A cotizar",
            message,
        )

    def test_optional_lines_are_left_out_when_empty(self):
        quote = make_quote(category_name="", message="")

        message = build_whatsapp_message(quote, [make_item()])

        for text in ["Ubicación", "Tipo", "fotos", "visita", "Mensaje"]:
            self.assertNotIn(text, message)
        self.assertIn("- Teléfono: +584121234567\n- Áreas:", message)
        self.assertTrue(message.endswith("- Estimado total: USD 1.250,00"))

    def test_hidden_estimate_leaves_no_price_in_the_message(self):
        # specs-003, RF-30: el cliente apagó el estimado en el panel
        message = build_whatsapp_message(make_quote(), [make_item()], show_estimate=False)

        self.assertIn("  - Cocina: 12,5 m²\n", message)
        self.assertNotIn("USD", message)
        self.assertNotIn("Estimado", message)
        self.assertNotIn("A cotizar", message)

    def test_visit_request_lists_the_areas_without_meters(self):
        quote = make_quote(needs_visit=True, estimated_price=None, message="")
        items = [make_item(square_meters=None), make_item(area=BATHROOM, square_meters=None)]

        message = build_whatsapp_message(quote, items)

        self.assertIn("- Áreas:\n  - Cocina\n  - Baño\n", message)
        self.assertIn("- Estimado total: A cotizar", message)
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
