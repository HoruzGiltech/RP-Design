from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from core.tests.helpers import TempMediaMixin, make_image_file
from site_content.models import HeroSection, ProcessStep, Service, ServicesSection


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
                "specialties",
                "services",
                "projects_section",
                "process",
                "contact",
                "footer",
                "seo",
            },
        )

    def test_new_database_returns_the_texts_of_the_mockup(self):
        site = self.get_site()

        self.assertEqual(site["settings"]["brand_name"], "RP DISEÑO")
        self.assertEqual(site["settings"]["whatsapp_display"], "0412 730 5964")
        self.assertEqual(site["settings"]["contact_email"], "rpdesings05@gmail.com")
        self.assertEqual(
            site["settings"]["instagram_url"], "https://www.instagram.com/rpdesign_ve/"
        )
        self.assertEqual(site["settings"]["accent_color"], "#111111")
        self.assertEqual(site["hero"]["eyebrow"], "ESTUDIO DE DISEÑO DE INTERIORES · CARACAS")
        self.assertEqual(
            site["hero"]["title"], "Transformamos tus espacios, del plano a la obra."
        )
        self.assertEqual(
            [item["text"] for item in site["specialties"]],
            ["Diseño residencial", "Diseño comercial", "Renders 3D", "Ejecución de obra"],
        )
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
