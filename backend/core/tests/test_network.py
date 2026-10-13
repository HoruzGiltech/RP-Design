from unittest.mock import patch

from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from rest_framework.throttling import ScopedRateThrottle

from core.network import get_client_ip
from core.tests.helpers import TempMediaMixin

PROXY = "10.0.0.1"
VISITOR = "200.1.2.3"


class ClientIpTests(SimpleTestCase):
    """La IP real del visitante, con y sin proxies delante (specs-006, RF-51)."""

    def make_request(self, forwarded_for=None):
        headers = {"REMOTE_ADDR": PROXY}
        if forwarded_for is not None:
            headers["HTTP_X_FORWARDED_FOR"] = forwarded_for
        return RequestFactory().get("/", **headers)

    @override_settings(NUM_PROXIES=0)
    def test_without_proxies_the_header_is_ignored(self):
        # Sin proxy de confianza, la cabecera la pudo inventar cualquiera
        request = self.make_request(forwarded_for="1.1.1.1")

        self.assertEqual(get_client_ip(request), PROXY)

    @override_settings(NUM_PROXIES=1)
    def test_with_one_proxy_the_last_address_is_the_visitor(self):
        request = self.make_request(forwarded_for=VISITOR)

        self.assertEqual(get_client_ip(request), VISITOR)

    @override_settings(NUM_PROXIES=1)
    def test_addresses_invented_by_the_visitor_are_ignored(self):
        # El visitante mandó su propia cabecera; el proxy agregó al final la IP real
        request = self.make_request(forwarded_for=f"1.1.1.1, 2.2.2.2, {VISITOR}")

        self.assertEqual(get_client_ip(request), VISITOR)

    @override_settings(NUM_PROXIES=2)
    def test_with_two_proxies_it_is_the_second_from_the_end(self):
        request = self.make_request(forwarded_for=f"1.1.1.1, {VISITOR}, 172.16.0.9")

        self.assertEqual(get_client_ip(request), VISITOR)

    @override_settings(NUM_PROXIES=2)
    def test_shorter_header_than_expected_uses_the_first_address(self):
        request = self.make_request(forwarded_for=VISITOR)

        self.assertEqual(get_client_ip(request), VISITOR)

    @override_settings(NUM_PROXIES=1)
    def test_without_the_header_the_remote_address_is_used(self):
        self.assertEqual(get_client_ip(self.make_request()), PROXY)


# Los límites se fijan aquí para que el test no dependa de lo que diga el archivo .env
TEST_RATES = {"public": "100/min", "quotes": "2/hour"}


@patch.object(ScopedRateThrottle, "THROTTLE_RATES", TEST_RATES)
class QuoteLimitBehindProxyTests(TestCase):
    """El límite de cotizaciones cuenta por visitante, no por proxy."""

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

    def post_quote(self, forwarded_for):
        return self.client.post(
            reverse("quote-create"),
            self.quote_data,
            content_type="application/json",
            REMOTE_ADDR=PROXY,
            HTTP_X_FORWARDED_FOR=forwarded_for,
        ).status_code

    def test_each_visitor_behind_the_proxy_has_its_own_limit(self):
        proxy_settings = {"NUM_PROXIES": 1}
        with self.settings(NUM_PROXIES=1, REST_FRAMEWORK=self.rest_settings(proxy_settings)):
            first_visitor = [self.post_quote("200.1.1.1") for _ in range(3)]
            second_visitor = self.post_quote("200.2.2.2")

        self.assertEqual(first_visitor, [201, 201, 429])
        self.assertEqual(second_visitor, 201)

    def test_without_proxies_a_made_up_header_does_not_avoid_the_limit(self):
        with self.settings(NUM_PROXIES=0, REST_FRAMEWORK=self.rest_settings({"NUM_PROXIES": 0})):
            codes = [self.post_quote(f"1.1.1.{number}") for number in range(3)]

        self.assertEqual(codes, [201, 201, 429])

    def rest_settings(self, changes):
        """La configuración de la API del proyecto, con los cambios indicados."""
        from django.conf import settings

        return {**settings.REST_FRAMEWORK, **changes}


class ServeMediaTests(TempMediaMixin, TestCase):
    """Los archivos subidos, servidos por Django (specs-006, RF-50)."""

    def setUp(self):
        self.name = default_storage.save("site/prueba.txt", ContentFile(b"contenido"))

    def get_file(self, name):
        return self.client.get(f"/media/{name}")

    @override_settings(SERVE_MEDIA=True)
    def test_file_is_served_when_the_option_is_on(self):
        response = self.get_file(self.name)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"contenido")

    @override_settings(SERVE_MEDIA=False)
    def test_file_is_not_served_when_the_option_is_off(self):
        self.assertEqual(self.get_file(self.name).status_code, 404)

    @override_settings(SERVE_MEDIA=True)
    def test_missing_file_gives_404(self):
        self.assertEqual(self.get_file("site/no-existe.jpg").status_code, 404)

    @override_settings(SERVE_MEDIA=True)
    def test_cannot_leave_the_media_folder(self):
        # Django rechaza estas rutas con "petición incorrecta" (400) o "no existe" (404)
        for path in ["../manage.py", "site/../../manage.py", "..%2Fmanage.py"]:
            with self.subTest(path=path):
                self.assertIn(self.get_file(path).status_code, [400, 404])
