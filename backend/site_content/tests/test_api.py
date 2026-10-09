from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from core.tests.helpers import TempMediaMixin, make_font_file, make_image_file
from site_content.models import (
    HeroSection,
    LegalPage,
    LegalSection,
    ProcessStep,
    QuoteFormField,
    Service,
    ServicesSection,
    SiteSettings,
)


class SiteContentApiTests(TempMediaMixin, TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("site-content")

    def get_site(self):
        return self.client.get(self.url).json()

    def test_response_has_every_section(self):
        self.assertEqual(
            set(self.get_site()),
            {
                "settings",
                "hero",
                "services",
                "projects_section",
                "process",
                "contact",
                "footer",
                "seo",
                "legal_pages",
            },
        )

    def test_new_database_returns_the_texts_of_the_mockup(self):
        site = self.get_site()

        self.assertEqual(site["settings"]["brand_name"], "RP DISEÑO")
        self.assertEqual(site["settings"]["whatsapp_display"], "+58 412 730 5964")
        self.assertEqual(
            site["settings"]["whatsapp_greeting"], "Hola! quiero agendar una reunión"
        )
        self.assertTrue(site["settings"]["show_whatsapp_button"])
        self.assertEqual(site["settings"]["contact_email"], "rpdesings05@gmail.com")
        self.assertEqual(
            site["settings"]["instagram_url"], "https://www.instagram.com/rpdesign_ve/"
        )
        self.assertEqual(site["settings"]["accent_color"], "#111111")
        self.assertEqual(site["hero"]["eyebrow"], "ESTUDIO DE DISEÑO DE INTERIORES · CARACAS")
        self.assertEqual(site["hero"]["title"], "")
        self.assertEqual(site["hero"]["primary_cta_text"], "Agenda una reunión")
        self.assertEqual(site["services"]["title"], "Un solo equipo para todo tu proyecto")
        self.assertEqual(
            [item["title"] for item in site["services"]["items"]],
            ["Levantamiento de espacio", "Proyecto de diseño", "Ejecución de obra"],
        )
        self.assertEqual(site["projects_section"]["view_all_text"], "Ver todos los proyectos")
        self.assertEqual(
            [step["title"] for step in site["process"]["steps"]],
            ["Renders 3D", "Video recorridos", "Planimetría", "Ejecución de obra"],
        )
        self.assertEqual(site["contact"]["submit_text"], "Enviar por WhatsApp")
        self.assertEqual(site["footer"]["name"], "RP DISEÑO INTERIOR")
        self.assertEqual(site["seo"]["site_title"], "RP Diseño Interior")

    def test_files_that_were_not_uploaded_are_null(self):
        site = self.get_site()

        self.assertIsNone(site["hero"]["image"])
        self.assertIsNone(site["hero"]["video"])
        self.assertIsNone(site["settings"]["logo"])
        self.assertIsNone(site["process"]["video"])

    def test_uploaded_image_has_a_full_url(self):
        hero = HeroSection.load()
        hero.image = make_image_file()
        hero.save()

        image_url = self.get_site()["hero"]["image"]

        self.assertEqual(image_url, f"http://testserver{hero.image.url}")

    def test_change_in_the_panel_is_seen_right_away(self):
        hero = HeroSection.load()
        hero.title = "Título cambiado en el panel"
        hero.save()

        self.assertEqual(self.get_site()["hero"]["title"], "Título cambiado en el panel")

    def test_specialties_are_no_longer_sent(self):
        # specs-002: el cintillo se quitó del sitio (la lista sigue en el panel)
        self.assertNotIn("specialties", self.get_site())

    def test_hero_buttons_are_shown_by_default_and_can_be_hidden(self):
        hero = self.get_site()["hero"]
        self.assertTrue(hero["show_primary_cta"])
        self.assertTrue(hero["show_secondary_cta"])

        HeroSection.objects.update(show_primary_cta=False)

        hero = self.get_site()["hero"]
        self.assertFalse(hero["show_primary_cta"])
        self.assertTrue(hero["show_secondary_cta"])

    def test_whatsapp_display_follows_the_number_of_the_panel(self):
        settings = SiteSettings.load()
        settings.whatsapp_number = "584141112233"
        settings.save()

        self.assertEqual(self.get_site()["settings"]["whatsapp_display"], "+58 414 111 2233")

    def test_hidden_section_arrives_with_is_visible_false(self):
        ServicesSection.objects.update(is_visible=False)

        site = self.get_site()

        self.assertFalse(site["services"]["is_visible"])
        self.assertTrue(site["hero"]["is_visible"])

    def test_hidden_list_items_are_not_sent(self):
        Service.objects.filter(title="Proyecto de diseño").update(is_visible=False)

        titles = [item["title"] for item in self.get_site()["services"]["items"]]

        self.assertEqual(titles, ["Levantamiento de espacio", "Ejecución de obra"])

    def test_list_items_follow_the_order_of_the_panel(self):
        ProcessStep.objects.filter(title="Planimetría").update(order=0)

        titles = [step["title"] for step in self.get_site()["process"]["steps"]]

        self.assertEqual(titles[0], "Planimetría")

    def test_api_is_read_only(self):
        for method in [self.client.post, self.client.put, self.client.delete]:
            self.assertEqual(method(self.url).status_code, 405)

    # --- specs-003 ---

    def test_fonts_are_null_until_the_client_uploads_them(self):
        settings = self.get_site()["settings"]

        self.assertIsNone(settings["heading_font"])
        self.assertIsNone(settings["body_font"])

    def test_uploaded_font_has_a_full_url(self):
        settings = SiteSettings.load()
        settings.heading_font = make_font_file()
        settings.save()

        site_settings = self.get_site()["settings"]

        self.assertEqual(
            site_settings["heading_font"], f"http://testserver{settings.heading_font.url}"
        )
        self.assertIsNone(site_settings["body_font"])

    def test_estimate_is_shown_by_default_and_can_be_hidden(self):
        self.assertTrue(self.get_site()["settings"]["show_estimate"])

        SiteSettings.objects.update(show_estimate=False)

        self.assertFalse(self.get_site()["settings"]["show_estimate"])

    def test_services_have_the_text_of_the_quote_button(self):
        self.assertEqual(self.get_site()["services"]["cta_text"], "Cotizar")

    def test_contact_has_the_texts_of_every_form_field(self):
        form_fields = self.get_site()["contact"]["form_fields"]

        self.assertEqual(
            set(form_fields),
            {
                "name",
                "phone",
                "email",
                "category",
                "location",
                "areas",
                "area_other",
                "square_meters",
                "needs_visit",
                "message",
                "has_photos",
            },
        )
        self.assertEqual(form_fields["name"], {"label": "Nombre", "placeholder": "Tu nombre"})
        self.assertEqual(form_fields["has_photos"]["label"], "Tengo fotos del espacio")

    def test_photos_checkbox_goes_before_the_message(self):
        # specs-004, RF-40: el mensaje es el último campo del formulario
        keys = list(QuoteFormField.objects.values_list("key", flat=True))

        self.assertEqual(keys[-2:], ["has_photos", "message"])
        self.assertEqual(len(keys), 11)

    def test_form_field_text_changed_in_the_panel_is_seen_right_away(self):
        QuoteFormField.objects.filter(key="phone").update(label="WhatsApp")

        self.assertEqual(self.get_site()["contact"]["form_fields"]["phone"]["label"], "WhatsApp")

    def test_site_has_the_links_to_the_legal_pages(self):
        self.assertEqual(
            self.get_site()["legal_pages"],
            [
                {"slug": "terminos", "title": "Términos y condiciones"},
                {"slug": "privacidad", "title": "Política de privacidad"},
            ],
        )


class LegalPageApiTests(TestCase):
    """Las dos páginas las crea la migración site_content.0005_initial_legal_pages."""

    def setUp(self):
        cache.clear()

    def get_page(self, slug):
        return self.client.get(reverse("legal-page", args=[slug]))

    def test_both_pages_exist_with_their_sections_in_order(self):
        terms = self.get_page("terminos").json()
        privacy = self.get_page("privacidad").json()

        self.assertEqual(terms["title"], "Términos y condiciones")
        self.assertEqual(
            [section["title"] for section in terms["sections"]],
            [
                "Uso del sitio",
                "Cotizaciones y precios",
                "Propiedad intelectual",
                "Cambios en estos términos",
                "Contacto",
            ],
        )
        self.assertEqual(privacy["title"], "Política de privacidad")
        self.assertIn("Cookies", [section["title"] for section in privacy["sections"]])

    def test_texts_are_pending_and_not_invented(self):
        page = self.get_page("privacidad").json()

        self.assertEqual(page["intro"], "[TEXTO PENDIENTE]")
        self.assertTrue(
            all(section["body"] == "[TEXTO PENDIENTE]" for section in page["sections"])
        )

    def test_page_has_the_date_of_the_last_update(self):
        self.assertIn("updated_at", self.get_page("terminos").json())

    def test_editing_a_section_updates_the_date_of_the_page(self):
        page = LegalPage.objects.get(slug="privacidad")
        old_date = page.updated_at

        section = page.sections.first()
        section.body = "Texto nuevo"
        section.save()

        page.refresh_from_db()
        self.assertGreater(page.updated_at, old_date)

    def test_sections_follow_the_order_of_the_panel(self):
        page = LegalPage.objects.get(slug="terminos")
        LegalSection.objects.create(page=page, title="Primero", body="x", order=0)

        titles = [section["title"] for section in self.get_page("terminos").json()["sections"]]

        self.assertEqual(titles[0], "Primero")

    def test_unknown_page_gives_404(self):
        self.assertEqual(self.get_page("no-existe").status_code, 404)

    def test_api_is_read_only(self):
        url = reverse("legal-page", args=["terminos"])

        for method in [self.client.post, self.client.put, self.client.delete]:
            self.assertEqual(method(url).status_code, 405)
