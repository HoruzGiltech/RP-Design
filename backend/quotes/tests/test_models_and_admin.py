from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from quotes.models import Quote, RemodelArea


def create_quote(**fields):
    values = {
        "name": "Ana Pérez",
        "email": "ana@mail.com",
        "phone": "+584121234567",
        "area": RemodelArea.objects.get(slug="cocina"),
        "square_meters": Decimal("12.5"),
        "price_per_m2_snapshot": Decimal("100"),
        "estimated_price": Decimal("1250"),
        "whatsapp_message": "Hola RP Design, quiero una cotización",
    }
    values.update(fields)
    return Quote.objects.create(**values)


class InitialAreasTests(TestCase):
    """Las áreas iniciales las crea una migración de datos."""

    def test_six_areas_exist_in_order_and_without_price(self):
        areas = RemodelArea.objects.all()

        self.assertEqual(
            [area.name for area in areas],
            ["Baño", "Cocina", "Sala", "Patio", "Piscina", "Otro"],
        )
        self.assertTrue(all(area.price_per_m2 is None for area in areas))
        self.assertTrue(all(area.is_active for area in areas))

    def test_only_the_last_one_is_other(self):
        other_areas = RemodelArea.objects.filter(is_other=True)

        self.assertEqual([area.slug for area in other_areas], ["otro"])


class QuoteModelTests(TestCase):
    def test_new_quote_has_status_new(self):
        self.assertEqual(create_quote().status, Quote.NEW)

    def test_newest_quote_goes_first(self):
        create_quote(name="Primera")
        create_quote(name="Segunda")

        self.assertEqual(Quote.objects.first().name, "Segunda")

    def test_area_with_quotes_cannot_be_deleted(self):
        quote = create_quote()

        with self.assertRaises(ProtectedError):
            quote.area.delete()


class QuotesAdminTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("dev", password="clave-de-prueba")
        self.client.force_login(user)

    def test_area_list_and_quote_list_load(self):
        create_quote()

        areas = self.client.get(reverse("admin:quotes_remodelarea_changelist"))
        quotes = self.client.get(reverse("admin:quotes_quote_changelist"))

        self.assertContains(areas, "Piscina")
        self.assertContains(quotes, "USD 1.250,00")

    def test_quotes_cannot_be_added_from_the_panel(self):
        response = self.client.get(reverse("admin:quotes_quote_add"))

        self.assertEqual(response.status_code, 403)

    def test_quote_detail_shows_the_message_and_the_whatsapp_link(self):
        quote = create_quote()

        response = self.client.get(reverse("admin:quotes_quote_change", args=[quote.pk]))

        self.assertContains(response, "Hola RP Design, quiero una cotización")
        self.assertContains(response, "https://wa.me/584121234567")

    def test_only_the_status_can_be_changed(self):
        quote = create_quote()
        url = reverse("admin:quotes_quote_change", args=[quote.pk])

        # Se intenta cambiar también el nombre y el estimado
        self.client.post(
            url, {"status": Quote.CONTACTED, "name": "Otro nombre", "estimated_price": "1"}
        )

        quote.refresh_from_db()
        self.assertEqual(quote.status, Quote.CONTACTED)
        self.assertEqual(quote.name, "Ana Pérez")
        self.assertEqual(quote.estimated_price, Decimal("1250"))
