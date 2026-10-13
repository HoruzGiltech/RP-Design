from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from projects.models import ProjectCategory
from quotes.models import Quote, QuoteItem, RemodelArea


def create_quote(**fields):
    """Cotización como las que llegan desde specs-008: tipo escrito y m² en un campo."""
    values = {
        "name": "Ana Pérez",
        "email": "ana@mail.com",
        "phone": "+584121234567",
        "remodel_type": "cocina y baño",
        "location": "Chacao, Caracas",
        "square_meters": Decimal("45.5"),
        "whatsapp_message": "Hola RP Design, quiero una cotización",
    }
    values.update(fields)
    return Quote.objects.create(**values)


def create_old_quote(**fields):
    """
    Cotización anterior a specs-008: con categoría, un área con su precio y un
    estimado. 12,5 m² de cocina a USD 100 el m².
    """
    values = {
        "remodel_type": "",
        "square_meters": None,
        "category_name": "Residencial",
        "estimated_price": Decimal("1250"),
    }
    values.update(fields)
    quote = create_quote(**values)
    QuoteItem.objects.create(
        quote=quote,
        area=RemodelArea.objects.get(slug="cocina"),
        square_meters=Decimal("12.5"),
        price_per_m2_snapshot=Decimal("100"),
        subtotal=Decimal("1250"),
    )
    return quote


class InitialAreasTests(TestCase):
    """Las áreas iniciales las crean las migraciones de datos 0002 y 0005."""

    def names(self, **filters):
        return list(RemodelArea.objects.filter(**filters).values_list("name", flat=True))

    def test_residential_keeps_the_original_areas(self):
        self.assertEqual(
            self.names(category__slug="residencial"),
            ["Baño", "Cocina", "Sala", "Patio", "Piscina"],
        )

    def test_corporate_and_commercial_get_the_example_areas(self):
        self.assertEqual(self.names(category__slug="corporativo"), ["Oficina", "Sala de reuniones"])
        self.assertEqual(self.names(category__slug="comercial"), ["Showroom"])

    def test_other_has_no_category_so_it_appears_in_every_type(self):
        other = RemodelArea.objects.get(is_other=True)

        self.assertEqual(other.slug, "otro")
        self.assertIsNone(other.category)

    def test_every_area_starts_active_and_without_price(self):
        areas = RemodelArea.objects.all()

        self.assertEqual(areas.count(), 9)
        self.assertTrue(all(area.price_per_m2 is None for area in areas))
        self.assertTrue(all(area.is_active for area in areas))


class AreaSlugTests(TestCase):
    """El identificador del área se genera solo (specs-002)."""

    def test_slug_is_created_from_the_name(self):
        area = RemodelArea.objects.create(name="Sala de espera")

        self.assertEqual(area.slug, "sala-de-espera")

    def test_same_name_in_another_category_gets_a_different_slug(self):
        corporate = ProjectCategory.objects.get(slug="corporativo")

        # Ya existe "Sala" en Residencial
        area = RemodelArea.objects.create(name="Sala", category=corporate)

        self.assertEqual(area.slug, "sala-2")

    def test_slug_does_not_change_when_the_name_is_edited(self):
        area = RemodelArea.objects.get(slug="cocina")

        area.name = "Cocina integral"
        area.save()

        self.assertEqual(area.slug, "cocina")

    def test_category_with_areas_cannot_be_deleted(self):
        residential = ProjectCategory.objects.get(slug="residencial")

        with self.assertRaises(ProtectedError):
            residential.delete()


class QuoteModelTests(TestCase):
    def test_new_quote_has_status_new(self):
        self.assertEqual(create_quote().status, Quote.NEW)

    def test_newest_quote_goes_first(self):
        create_quote(name="Primera")
        create_quote(name="Segunda")

        self.assertEqual(Quote.objects.first().name, "Segunda")

    def test_area_with_old_quotes_cannot_be_deleted(self):
        quote = create_old_quote()

        with self.assertRaises(ProtectedError):
            quote.items.get().area.delete()

    def test_deleting_a_quote_deletes_its_items(self):
        create_old_quote().delete()

        self.assertEqual(QuoteItem.objects.count(), 0)


class QuotesAdminTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("dev", password="clave-de-prueba")
        self.client.force_login(user)

    def get_detail(self, quote):
        return self.client.get(reverse("admin:quotes_quote_change", args=[quote.pk]))

    def test_quote_list_shows_the_type_and_the_location(self):
        create_quote()

        response = self.client.get(reverse("admin:quotes_quote_changelist"))

        self.assertContains(response, "cocina y baño")
        self.assertContains(response, "Chacao, Caracas")

    def test_quote_list_shows_the_category_of_an_old_quote_as_its_type(self):
        create_old_quote()

        response = self.client.get(reverse("admin:quotes_quote_changelist"))

        self.assertContains(response, "Residencial")

    def test_quotes_cannot_be_added_from_the_panel(self):
        response = self.client.get(reverse("admin:quotes_quote_add"))

        self.assertEqual(response.status_code, 403)

    def test_quote_detail_shows_the_message_and_the_whatsapp_link(self):
        response = self.get_detail(create_quote())

        self.assertContains(response, "Hola RP Design, quiero una cotización")
        self.assertContains(response, "https://wa.me/584121234567")

    def test_new_quote_detail_shows_its_fields_and_no_price(self):
        response = self.get_detail(create_quote(has_photos=True))

        self.assertContains(response, "cocina y baño")
        self.assertContains(response, "Chacao, Caracas")
        self.assertContains(response, "45,50")
        self.assertContains(response, "Tiene fotos del espacio")
        # Una cotización nueva no tiene áreas ni estimado
        self.assertNotContains(response, "Áreas cotizadas")
        self.assertNotContains(response, "Estimado total")

    def test_old_quote_detail_still_shows_its_areas_and_estimate(self):
        # specs-008, RF-63.4: el historial se conserva
        response = self.get_detail(create_old_quote())

        self.assertContains(response, "Áreas cotizadas")
        self.assertContains(response, "Cocina")
        self.assertContains(response, "12,50")
        self.assertContains(response, "Estimado total")
        self.assertContains(response, "USD 1.250,00")
        # Las áreas solo se leen: no hay campos para cambiarlas
        self.assertNotContains(response, 'name="items-0-square_meters"')

    def test_only_the_status_can_be_changed(self):
        quote = create_quote()
        url = reverse("admin:quotes_quote_change", args=[quote.pk])

        # Se intenta cambiar también el nombre y el tipo
        self.client.post(
            url, {"status": Quote.CONTACTED, "name": "Otro nombre", "remodel_type": "otra cosa"}
        )

        quote.refresh_from_db()
        self.assertEqual(quote.status, Quote.CONTACTED)
        self.assertEqual(quote.name, "Ana Pérez")
        self.assertEqual(quote.remodel_type, "cocina y baño")

    def test_status_of_an_old_quote_can_be_changed(self):
        quote = create_old_quote()
        url = reverse("admin:quotes_quote_change", args=[quote.pk])

        self.client.post(
            url, {"status": Quote.CLOSED, "items-TOTAL_FORMS": 1, "items-INITIAL_FORMS": 1}
        )

        quote.refresh_from_db()
        self.assertEqual(quote.status, Quote.CLOSED)
        self.assertEqual(quote.items.count(), 1)

    def test_areas_and_prices_are_no_longer_in_the_panel(self):
        # specs-008: el formulario ya no pide áreas ni calcula precios
        index = self.client.get(reverse("admin:index"))

        self.assertNotContains(index, "Áreas y precios")
        self.assertNotContains(index, "/quotes/remodelarea/")
