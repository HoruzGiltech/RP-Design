from decimal import Decimal
from unittest.mock import patch
from urllib.parse import unquote

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.throttling import ScopedRateThrottle

from quotes.models import Quote, QuoteItem
from site_content.models import SiteSettings


class QuoteCreateApiTests(TestCase):
    """El formulario desde specs-008: tipo en texto libre, m² opcionales y sin precios."""

    def setUp(self):
        cache.clear()
        self.url = reverse("quote-create")

    def form_data(self, **fields):
        data = {
            "name": "Ana Pérez",
            "email": "ana@mail.com",
            "phone": "+58 412-1234567",
            "remodel_type": "cocina y baño",
            "location": "Chacao, Caracas",
            "square_meters": "45.5",
            "message": "Quiero cambiar los gabinetes.",
            "website": "",
            "privacy_accepted": True,
        }
        data.update(fields)
        return data

    def post(self, **fields):
        return self.client.post(
            self.url, self.form_data(**fields), content_type="application/json"
        )

    # --- Envío correcto ---

    def test_valid_quote_is_saved_with_status_new(self):
        response = self.post()

        quote = Quote.objects.get()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(quote.status, Quote.NEW)
        self.assertEqual(quote.name, "Ana Pérez")
        self.assertEqual(quote.phone, "+584121234567")
        self.assertEqual(quote.remodel_type, "cocina y baño")
        self.assertEqual(quote.location, "Chacao, Caracas")
        self.assertEqual(quote.square_meters, Decimal("45.5"))

    def test_new_quote_has_no_price_category_or_items(self):
        self.post()

        quote = Quote.objects.get()
        self.assertIsNone(quote.estimated_price)
        self.assertIsNone(quote.category)
        self.assertEqual(quote.category_name, "")
        self.assertEqual(QuoteItem.objects.count(), 0)

    def test_response_has_the_id_and_the_whatsapp_link_but_no_price(self):
        data = self.post().json()

        self.assertEqual(set(data), {"id", "whatsapp_url"})
        self.assertEqual(data["id"], Quote.objects.get().pk)
        self.assertTrue(data["whatsapp_url"].startswith("https://wa.me/584127305964?text="))

    def test_link_carries_exactly_the_message_saved_in_the_database(self):
        whatsapp_url = self.post().json()["whatsapp_url"]

        quote = Quote.objects.get()
        sent_message = unquote(whatsapp_url.split("?text=")[1])
        self.assertEqual(sent_message, quote.whatsapp_message)
        for expected in [
            "Ana Pérez",
            "ana@mail.com",
            "+584121234567",
            "- Tipo de remodelación: cocina y baño",
            "- Ubicación: Chacao, Caracas",
            "- Metros cuadrados: 45,5 m²",
            "Quiero cambiar los gabinetes.",
        ]:
            self.assertIn(expected, quote.whatsapp_message)
        self.assertNotIn("USD", quote.whatsapp_message)

    def test_link_uses_the_number_configured_in_the_panel(self):
        settings = SiteSettings.load()
        settings.whatsapp_number = "584140000000"
        settings.save()

        whatsapp_url = self.post().json()["whatsapp_url"]

        self.assertTrue(whatsapp_url.startswith("https://wa.me/584140000000?text="))

    def test_fields_the_form_does_not_have_are_ignored(self):
        self.post(estimated_price="1.00", status="closed", category_name="Residencial")

        quote = Quote.objects.get()
        self.assertIsNone(quote.estimated_price)
        self.assertEqual(quote.status, Quote.NEW)
        self.assertEqual(quote.category_name, "")

    # --- Metros cuadrados y visita ---

    def test_square_meters_are_optional(self):
        for value in [None, "omitido"]:
            with self.subTest(square_meters=value):
                data = self.form_data()
                if value is None:
                    data["square_meters"] = None
                else:
                    del data["square_meters"]

                response = self.client.post(self.url, data, content_type="application/json")

                self.assertEqual(response.status_code, 201)

        self.assertTrue(all(quote.square_meters is None for quote in Quote.objects.all()))
        self.assertNotIn("Metros cuadrados", Quote.objects.first().whatsapp_message)

    def test_visit_request_ignores_the_square_meters_that_arrive(self):
        self.post(needs_visit=True, square_meters="40")

        quote = Quote.objects.get()
        self.assertTrue(quote.needs_visit)
        self.assertIsNone(quote.square_meters)
        self.assertIn("quiero agendar una visita", quote.whatsapp_message)
        self.assertNotIn("Metros cuadrados", quote.whatsapp_message)

    def test_photos_and_visit_are_optional(self):
        self.post()

        quote = Quote.objects.get()
        self.assertFalse(quote.has_photos)
        self.assertFalse(quote.needs_visit)

    def test_photos_checkbox_is_saved_and_goes_in_the_message(self):
        self.post(has_photos=True)

        quote = Quote.objects.get()
        self.assertTrue(quote.has_photos)
        self.assertIn("- Tengo fotos del espacio", quote.whatsapp_message)

    def test_message_is_optional(self):
        response = self.post(message="")

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("Mensaje", Quote.objects.get().whatsapp_message)

    # --- Validaciones ---

    def assert_field_error(self, response, field, text):
        self.assertEqual(response.status_code, 400)
        self.assertIn(text, " ".join(response.json()[field]))
        self.assertEqual(Quote.objects.count(), 0)

    def test_required_fields(self):
        response = self.client.post(self.url, {}, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            set(response.json()),
            {"name", "email", "phone", "remodel_type", "location", "privacy_accepted"},
        )
        self.assertIn("requerido", response.json()["name"][0])

    def test_remodel_type_is_required(self):
        for value in ["", "   ", None]:
            with self.subTest(remodel_type=value):
                response = self.post(remodel_type=value)

                self.assert_field_error(response, "remodel_type", "qué quieres remodelar")

    def test_location_is_required(self):
        for value in ["", "   ", None]:
            with self.subTest(location=value):
                self.assert_field_error(self.post(location=value), "location", "ubicación")

    def test_invalid_email(self):
        self.assert_field_error(self.post(email="no-es-correo"), "email", "válid")

    def test_invalid_phone(self):
        self.assert_field_error(self.post(phone="123"), "phone", "teléfono válido")

    def test_square_meters_must_be_greater_than_zero(self):
        for value in ["0", "-5"]:
            with self.subTest(square_meters=value):
                response = self.post(square_meters=value)

                self.assert_field_error(response, "square_meters", "mayores que 0")

    def test_square_meters_that_are_not_a_number_are_rejected(self):
        self.assert_field_error(self.post(square_meters="muchos"), "square_meters", "número válido")

    def test_text_fields_have_a_maximum_length(self):
        for field, length in [("remodel_type", 121), ("location", 161), ("message", 1001)]:
            with self.subTest(field=field):
                response = self.post(**{field: "a" * length})

                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json())

    # --- Política de privacidad ---

    def test_acceptance_date_is_saved_with_the_quote(self):
        self.post()

        self.assertIsNotNone(Quote.objects.get().privacy_accepted_at)

    def test_quote_is_rejected_without_accepting_the_privacy_policy(self):
        for value in [False, None]:
            with self.subTest(privacy_accepted=value):
                response = self.post(privacy_accepted=value)

                self.assertEqual(response.status_code, 400)
                self.assertIn("privacy_accepted", response.json())

        self.assertEqual(Quote.objects.count(), 0)

    def test_message_explains_that_the_policy_must_be_accepted(self):
        response = self.post(privacy_accepted=False)

        self.assert_field_error(response, "privacy_accepted", "política de privacidad")

    # --- Honeypot ---

    def test_bot_gets_a_fake_success_and_nothing_is_saved(self):
        response = self.post(website="http://spam.example")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.json()), {"id", "whatsapp_url"})
        self.assertNotIn("584127305964", response.json()["whatsapp_url"])
        self.assertEqual(Quote.objects.count(), 0)

    def test_bot_with_invalid_data_also_gets_the_fake_success(self):
        response = self.post(website="spam", email="malo", remodel_type="")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Quote.objects.count(), 0)

    # --- Otros métodos y direcciones que ya no existen ---

    def test_quotes_cannot_be_read_through_the_api(self):
        self.post()

        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_quote_categories_endpoint_no_longer_exists(self):
        # specs-008: el formulario ya no pide áreas por categoría
        self.assertEqual(self.client.get("/api/quote-categories/").status_code, 404)


# Los límites se fijan aquí para que el test no dependa de lo que diga el archivo .env
TEST_RATES = {"public": "3/min", "quotes": "5/hour"}


@patch.object(ScopedRateThrottle, "THROTTLE_RATES", TEST_RATES)
class ThrottleTests(TestCase):
    def setUp(self):
        cache.clear()
        self.quote_data = {
            "name": "Ana",
            "email": "ana@mail.com",
            "phone": "+584121234567",
            "remodel_type": "cocina",
            "location": "Caracas",
            "privacy_accepted": True,
        }

    def post_quote(self, ip="10.0.0.1"):
        return self.client.post(
            reverse("quote-create"),
            self.quote_data,
            content_type="application/json",
            REMOTE_ADDR=ip,
        )

    def test_sixth_quote_in_an_hour_is_rejected(self):
        codes = [self.post_quote().status_code for _ in range(6)]

        self.assertEqual(codes, [201, 201, 201, 201, 201, 429])
        self.assertEqual(Quote.objects.count(), 5)

    def test_limit_is_per_ip(self):
        for _ in range(5):
            self.post_quote(ip="10.0.0.1")

        self.assertEqual(self.post_quote(ip="10.0.0.1").status_code, 429)
        self.assertEqual(self.post_quote(ip="10.0.0.2").status_code, 201)

    def test_bots_are_also_limited(self):
        self.quote_data["website"] = "spam"

        codes = [self.post_quote().status_code for _ in range(6)]

        self.assertEqual(codes[-1], 429)

    def test_public_api_has_its_own_limit(self):
        url = reverse("site-content")

        codes = [self.client.get(url).status_code for _ in range(4)]

        self.assertEqual(codes, [200, 200, 200, 429])

    def test_reading_does_not_use_up_the_quote_limit(self):
        for _ in range(3):
            self.client.get(reverse("site-content"), REMOTE_ADDR="10.0.0.1")

        self.assertEqual(self.post_quote(ip="10.0.0.1").status_code, 201)
