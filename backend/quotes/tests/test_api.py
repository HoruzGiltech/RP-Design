from decimal import Decimal
from unittest.mock import patch
from urllib.parse import unquote

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.throttling import ScopedRateThrottle

from quotes.models import Quote, RemodelArea
from site_content.models import SiteSettings


class QuoteAreasApiTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_active_areas_are_listed_in_order_with_their_price(self):
        RemodelArea.objects.filter(slug="cocina").update(price_per_m2=Decimal("100"))
        RemodelArea.objects.filter(slug="patio").update(is_active=False)

        areas = self.client.get(reverse("quote-area-list")).json()

        self.assertEqual(
            [area["name"] for area in areas], ["Baño", "Cocina", "Sala", "Piscina", "Otro"]
        )
        self.assertEqual(set(areas[0]), {"id", "name", "price_per_m2", "is_other"})
        self.assertIsNone(areas[0]["price_per_m2"])
        self.assertEqual(areas[1]["price_per_m2"], "100.00")
        self.assertTrue(areas[-1]["is_other"])


class QuoteCreateApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("quote-create")
        self.kitchen = RemodelArea.objects.get(slug="cocina")
        self.kitchen.price_per_m2 = Decimal("100")
        self.kitchen.save()
        self.other = RemodelArea.objects.get(slug="otro")

    def form_data(self, **fields):
        data = {
            "name": "Ana Pérez",
            "email": "ana@mail.com",
            "phone": "+58 412-1234567",
            "area": self.kitchen.pk,
            "area_other": "",
            "square_meters": "12.5",
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
        self.assertEqual(quote.square_meters, Decimal("12.5"))
        self.assertEqual(quote.price_per_m2_snapshot, Decimal("100"))
        self.assertEqual(quote.estimated_price, Decimal("1250.00"))

    def test_response_has_the_estimate_and_the_whatsapp_link(self):
        data = self.post().json()

        self.assertEqual(data["id"], Quote.objects.get().pk)
        self.assertEqual(data["estimated_price"], "1250.00")
        self.assertEqual(data["estimated_price_display"], "USD 1.250,00")
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
            "Cocina",
            "12,5 m²",
            "USD 1.250,00",
            "Quiero cambiar los gabinetes.",
        ]:
            self.assertIn(expected, quote.whatsapp_message)

    def test_link_uses_the_number_configured_in_the_panel(self):
        settings = SiteSettings.load()
        settings.whatsapp_number = "584140000000"
        settings.save()

        whatsapp_url = self.post().json()["whatsapp_url"]

        self.assertTrue(whatsapp_url.startswith("https://wa.me/584140000000?text="))

    def test_price_sent_by_the_browser_is_ignored(self):
        response = self.post(
            estimated_price="1.00", price_per_m2_snapshot="0.01", status="closed"
        )

        quote = Quote.objects.get()
        self.assertEqual(response.json()["estimated_price"], "1250.00")
        self.assertEqual(quote.estimated_price, Decimal("1250.00"))
        self.assertEqual(quote.price_per_m2_snapshot, Decimal("100"))
        self.assertEqual(quote.status, Quote.NEW)
        self.assertIn("USD 1.250,00", quote.whatsapp_message)

    def test_area_without_price_is_to_be_quoted(self):
        bathroom = RemodelArea.objects.get(slug="bano")

        data = self.post(area=bathroom.pk).json()

        quote = Quote.objects.get()
        self.assertIsNone(data["estimated_price"])
        self.assertEqual(data["estimated_price_display"], "A cotizar")
        self.assertIsNone(quote.estimated_price)
        self.assertIn("A cotizar", quote.whatsapp_message)

    def test_other_area_saves_what_the_person_wrote(self):
        self.post(area=self.other.pk, area_other="  Terraza  ")

        quote = Quote.objects.get()
        self.assertEqual(quote.area_other, "Terraza")
        self.assertIn("Otro: Terraza", quote.whatsapp_message)

    def test_area_other_is_dropped_when_the_area_is_not_other(self):
        self.post(area_other="Texto que no aplica")

        self.assertEqual(Quote.objects.get().area_other, "")

    def test_message_is_optional(self):
        response = self.post(message="")

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("Mensaje", Quote.objects.get().whatsapp_message)

    def test_old_quotes_keep_their_price_when_the_area_price_changes(self):
        self.post()
        self.kitchen.price_per_m2 = Decimal("120")
        self.kitchen.save()

        new_estimate = self.post().json()["estimated_price_display"]

        old_quote = Quote.objects.order_by("created_at").first()
        self.assertEqual(new_estimate, "USD 1.500,00")
        self.assertEqual(old_quote.estimated_price, Decimal("1250.00"))

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
            {"name", "email", "phone", "area", "square_meters", "privacy_accepted"},
        )
        self.assertIn("requerido", response.json()["name"][0])

    def test_invalid_email(self):
        self.assert_field_error(self.post(email="no-es-correo"), "email", "válid")

    def test_invalid_phone(self):
        self.assert_field_error(self.post(phone="123"), "phone", "teléfono válido")

    def test_square_meters_must_be_greater_than_zero(self):
        self.assert_field_error(self.post(square_meters="0"), "square_meters", "mayores que 0")
        self.assert_field_error(self.post(square_meters="-5"), "square_meters", "mayores que 0")

    def test_square_meters_cannot_exceed_the_maximum_of_the_panel(self):
        settings = SiteSettings.load()
        settings.max_square_meters = 500
        settings.save()

        self.assert_field_error(self.post(square_meters="501"), "square_meters", "500 m²")
        self.assertEqual(self.post(square_meters="500").status_code, 201)

    def test_other_area_requires_the_description(self):
        response = self.post(area=self.other.pk, area_other="   ")

        self.assert_field_error(response, "area_other", "Especifica")

    def test_inactive_or_unknown_area_is_rejected(self):
        self.kitchen.is_active = False
        self.kitchen.save()

        self.assert_field_error(self.post(), "area", "Elige un área")
        self.assert_field_error(self.post(area=99999), "area", "Elige un área")

    def test_message_cannot_be_longer_than_1000_characters(self):
        response = self.post(message="a" * 1001)

        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json())

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
        self.assertEqual(
            set(response.json()),
            {"id", "estimated_price", "estimated_price_display", "whatsapp_url"},
        )
        self.assertNotIn("584127305964", response.json()["whatsapp_url"])
        self.assertEqual(Quote.objects.count(), 0)

    def test_bot_with_invalid_data_also_gets_the_fake_success(self):
        response = self.post(website="spam", email="malo", square_meters="-1")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Quote.objects.count(), 0)

    # --- Otros métodos ---

    def test_quotes_cannot_be_read_through_the_api(self):
        self.post()

        self.assertEqual(self.client.get(self.url).status_code, 405)


# Los límites se fijan aquí para que el test no dependa de lo que diga el archivo .env
TEST_RATES = {"public": "3/min", "quotes": "5/hour"}


@patch.object(ScopedRateThrottle, "THROTTLE_RATES", TEST_RATES)
class ThrottleTests(TestCase):
    def setUp(self):
        cache.clear()
        area = RemodelArea.objects.get(slug="cocina")
        self.quote_data = {
            "name": "Ana",
            "email": "ana@mail.com",
            "phone": "+584121234567",
            "area": area.pk,
            "square_meters": "10",
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
        url = reverse("quote-area-list")

        codes = [self.client.get(url).status_code for _ in range(4)]

        self.assertEqual(codes, [200, 200, 200, 429])

    def test_reading_does_not_use_up_the_quote_limit(self):
        for _ in range(3):
            self.client.get(reverse("quote-area-list"), REMOTE_ADDR="10.0.0.1")

        self.assertEqual(self.post_quote(ip="10.0.0.1").status_code, 201)
