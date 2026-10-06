import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

GOOD_PASSWORD = "clave-larga-y-segura-2026"
MAX_FAILED_LOGINS = 5


class LoginLockoutTests(TestCase):
    """Bloqueo del login del panel con django-axes."""

    def setUp(self):
        get_user_model().objects.create_superuser("dev", password=GOOD_PASSWORD)
        self.login_url = reverse("admin:login")
        # axes avisa por consola de cada intento fallido. Aquí se provocan a propósito,
        # así que se silencia durante estos tests para no llenar la salida.
        axes_logger = logging.getLogger("axes")
        previous_level = axes_logger.level
        axes_logger.setLevel(logging.CRITICAL)
        self.addCleanup(axes_logger.setLevel, previous_level)

    def login(self, password, ip="10.0.0.1"):
        # "next" es la página a la que el panel lleva después de entrar
        data = {"username": "dev", "password": password, "next": reverse("admin:index")}
        return self.client.post(self.login_url, data, REMOTE_ADDR=ip)

    def test_correct_password_logs_in(self):
        response = self.login(GOOD_PASSWORD)

        self.assertRedirects(response, reverse("admin:index"))

    def test_four_failures_do_not_lock_the_login(self):
        for _ in range(MAX_FAILED_LOGINS - 1):
            self.login("clave-mala")

        response = self.login(GOOD_PASSWORD)

        self.assertRedirects(response, reverse("admin:index"))

    def test_five_failures_lock_the_login_even_with_the_right_password(self):
        for _ in range(MAX_FAILED_LOGINS):
            self.login("clave-mala")

        response = self.login(GOOD_PASSWORD)

        self.assertEqual(response.status_code, 429)
        self.assertContains(response, "bloqueado durante 30 minutos", status_code=429)

    def test_lock_does_not_affect_another_ip(self):
        for _ in range(MAX_FAILED_LOGINS):
            self.login("clave-mala", ip="10.0.0.1")

        response = self.login(GOOD_PASSWORD, ip="10.0.0.2")

        self.assertRedirects(response, reverse("admin:index"))

    def test_successful_login_resets_the_counter(self):
        for _ in range(MAX_FAILED_LOGINS - 1):
            self.login("clave-mala")
        self.login(GOOD_PASSWORD)
        self.client.logout()

        for _ in range(MAX_FAILED_LOGINS - 1):
            self.login("clave-mala")
        response = self.login(GOOD_PASSWORD)

        self.assertRedirects(response, reverse("admin:index"))


class PasswordRulesTests(TestCase):
    def test_password_shorter_than_10_characters_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_password("Xk7!pQ2z")

    def test_common_or_numeric_passwords_are_rejected(self):
        for weak_password in ["password123", "12345678901234"]:
            with self.subTest(password=weak_password):
                with self.assertRaises(ValidationError):
                    validate_password(weak_password)

    def test_long_uncommon_password_is_accepted(self):
        validate_password(GOOD_PASSWORD)
