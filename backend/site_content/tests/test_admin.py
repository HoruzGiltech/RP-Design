from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from site_content.models import HeroSection, Service, SiteSettings

SINGLETON_MODELS = [
    "sitesettings",
    "herosection",
    "servicessection",
    "projectssection",
    "processsection",
    "contactsection",
    "footersection",
    "seosettings",
]


class SiteContentAdminTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("dev", password="clave-de-prueba")
        self.client.force_login(user)

    def test_menu_link_goes_straight_to_the_edit_form(self):
        for model_name in SINGLETON_MODELS:
            with self.subTest(model=model_name):
                response = self.client.get(reverse(f"admin:site_content_{model_name}_changelist"))

                self.assertRedirects(
                    response, reverse(f"admin:site_content_{model_name}_change", args=[1])
                )

    def test_single_sections_cannot_be_added_or_deleted(self):
        for model_name in SINGLETON_MODELS:
            with self.subTest(model=model_name):
                add = self.client.get(reverse(f"admin:site_content_{model_name}_add"))
                delete = self.client.post(
                    reverse(f"admin:site_content_{model_name}_delete", args=[1]),
                    {"post": "yes"},
                )

                self.assertEqual(add.status_code, 403)
                self.assertEqual(delete.status_code, 403)

        self.assertEqual(HeroSection.objects.count(), 1)

    def test_edit_form_has_no_delete_button(self):
        response = self.client.get(reverse("admin:site_content_herosection_change", args=[1]))

        self.assertContains(response, "Mostrar en el sitio")
        self.assertNotContains(response, "deletelink")

    def test_hero_text_can_be_edited(self):
        url = reverse("admin:site_content_herosection_change", args=[1])

        self.client.post(
            url,
            {
                "is_visible": "on",
                "title": "Título nuevo",
                "primary_cta_text": "Agenda una visita",
                "secondary_cta_text": "Ver proyectos",
            },
        )

        self.assertEqual(HeroSection.objects.get().title, "Título nuevo")

    def test_invalid_whatsapp_number_shows_the_help_message(self):
        url = reverse("admin:site_content_sitesettings_change", args=[1])
        settings = SiteSettings.load()

        response = self.client.post(
            url,
            {
                "brand_initials": settings.brand_initials,
                "brand_name": settings.brand_name,
                "brand_subtitle": settings.brand_subtitle,
                "header_cta_text": settings.header_cta_text,
                "accent_color": settings.accent_color,
                "whatsapp_number": "0412-7305964",
                "whatsapp_display": settings.whatsapp_display,
                "contact_email": settings.contact_email,
                "instagram_handle": settings.instagram_handle,
                "city": settings.city,
                "price_note": settings.price_note,
                "max_square_meters": "10000",
            },
        )

        self.assertContains(response, "formato internacional")
        self.assertEqual(SiteSettings.objects.get().whatsapp_number, "584127305964")

    def test_lists_load_and_show_the_visible_switch(self):
        for model_name in ["specialty", "service", "processstep"]:
            with self.subTest(model=model_name):
                response = self.client.get(reverse(f"admin:site_content_{model_name}_changelist"))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "is_visible")

    def test_list_items_can_be_added(self):
        self.client.post(
            reverse("admin:site_content_service_add"),
            {"title": "Asesoría", "description": "Texto", "is_visible": "on"},
        )

        self.assertTrue(Service.objects.filter(title="Asesoría").exists())
