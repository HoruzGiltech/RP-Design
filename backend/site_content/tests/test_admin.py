from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.tests.helpers import TempMediaMixin, make_fake_file, make_font_file
from site_content.models import (
    HeroSection,
    LegalPage,
    ProcessStep,
    QuoteFormField,
    Service,
    SiteSettings,
)

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


class SiteContentAdminTests(TempMediaMixin, TestCase):
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
        # specs-002: interruptores de los dos botones del hero
        self.assertContains(response, 'name="show_primary_cta"')
        self.assertContains(response, 'name="show_secondary_cta"')

    def test_hero_text_can_be_edited(self):
        url = reverse("admin:site_content_herosection_change", args=[1])

        self.client.post(
            url,
            {
                "is_visible": "on",
                "title": "Título nuevo",
                "primary_cta_text": "Agenda una reunión",
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
                "whatsapp_greeting": settings.whatsapp_greeting,
                "show_whatsapp_button": "on",
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
        response = self.client.get(reverse("admin:site_content_specialty_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "is_visible")

    # --- specs-003: servicios y pasos dentro de su sección (RF-25) ---

    def test_services_and_steps_have_no_menu_entry_of_their_own(self):
        index = self.client.get(reverse("admin:index"))

        self.assertNotContains(index, "/site_content/service/")
        self.assertNotContains(index, "/site_content/processstep/")

    def test_section_form_shows_its_items(self):
        services = self.client.get(reverse("admin:site_content_servicessection_change", args=[1]))
        process = self.client.get(reverse("admin:site_content_processsection_change", args=[1]))

        self.assertContains(services, "Levantamiento de espacio")
        self.assertContains(services, 'name="cta_text"')
        self.assertContains(process, "Planimetría")

    def section_form(self, prefix, items):
        """Datos del formulario de una sección con su tabla de elementos."""
        data = {
            "is_visible": "on",
            "title": "Título",
            "cta_text": "Cotizar",
            f"{prefix}-TOTAL_FORMS": len(items),
            f"{prefix}-INITIAL_FORMS": len([item for item in items if "id" in item]),
        }
        for index, item in enumerate(items):
            values = {"section": 1, "description": "Texto", "is_visible": "on", **item}
            for field, value in values.items():
                data[f"{prefix}-{index}-{field}"] = value
        return data

    def test_service_can_be_added_and_edited_inside_the_section(self):
        first = Service.objects.first()
        url = reverse("admin:site_content_servicessection_change", args=[1])
        items = [
            {"id": service.pk, "title": service.title, "order": service.order}
            for service in Service.objects.all()
        ]
        items[0]["title"] = "Título cambiado"
        items.append({"title": "Asesoría", "order": 99})

        response = self.client.post(url, self.section_form("items", items))

        first.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(first.title, "Título cambiado")
        self.assertEqual(Service.objects.last().title, "Asesoría")

    def test_process_steps_are_reordered_inside_the_section(self):
        url = reverse("admin:site_content_processsection_change", args=[1])
        steps = list(ProcessStep.objects.all())
        # El último paso se arrastra al primer lugar
        new_order = [steps[-1]] + steps[:-1]
        items = [
            {"id": step.pk, "title": step.title, "order": position}
            for position, step in enumerate(new_order, start=1)
        ]

        response = self.client.post(url, self.section_form("steps", items))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProcessStep.objects.first(), steps[-1])

    # --- specs-003: textos del formulario (RF-31) ---

    def contact_form(self, **changes):
        """El formulario de Contacto con sus 11 filas; `changes` cambia el título de un campo."""
        form_fields = list(QuoteFormField.objects.all())
        data = {
            "is_visible": "on",
            "title": "Contacto",
            "submit_text": "Enviar por WhatsApp",
            "form_fields-TOTAL_FORMS": len(form_fields),
            "form_fields-INITIAL_FORMS": len(form_fields),
        }
        for index, form_field in enumerate(form_fields):
            data[f"form_fields-{index}-id"] = form_field.pk
            data[f"form_fields-{index}-section"] = 1
            data[f"form_fields-{index}-label"] = changes.get(form_field.key, form_field.label)
            data[f"form_fields-{index}-placeholder"] = form_field.placeholder
        return data

    def test_form_field_texts_can_be_edited(self):
        url = reverse("admin:site_content_contactsection_change", args=[1])

        response = self.client.post(url, self.contact_form(name="Nombre y apellido"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(QuoteFormField.objects.get(key="name").label, "Nombre y apellido")

    def test_form_fields_cannot_be_added_or_deleted(self):
        url = reverse("admin:site_content_contactsection_change", args=[1])
        data = self.contact_form()
        # Se intenta borrar la primera fila y agregar una nueva
        data["form_fields-0-DELETE"] = "on"
        data["form_fields-TOTAL_FORMS"] = 12
        data["form_fields-11-section"] = 1
        data["form_fields-11-label"] = "Campo inventado"

        page = self.client.get(url)
        self.client.post(url, data)

        self.assertContains(page, "Tipo de remodelación")
        self.assertNotContains(page, "form_fields-0-DELETE")
        self.assertEqual(QuoteFormField.objects.count(), 11)
        self.assertFalse(QuoteFormField.objects.filter(label="Campo inventado").exists())

    # --- specs-003: tipografía y estimado (RF-19, RF-30) ---

    def settings_form(self, **fields):
        settings = SiteSettings.load()
        data = {
            "brand_initials": settings.brand_initials,
            "brand_name": settings.brand_name,
            "brand_subtitle": settings.brand_subtitle,
            "header_cta_text": settings.header_cta_text,
            "accent_color": settings.accent_color,
            "whatsapp_number": settings.whatsapp_number,
            "whatsapp_greeting": settings.whatsapp_greeting,
            "show_whatsapp_button": "on",
            "contact_email": settings.contact_email,
            "instagram_handle": settings.instagram_handle,
            "city": settings.city,
            "show_estimate": "on",
            "price_note": settings.price_note,
            "max_square_meters": settings.max_square_meters,
        }
        data.update(fields)
        return data

    def test_font_can_be_uploaded_and_is_renamed(self):
        url = reverse("admin:site_content_sitesettings_change", args=[1])

        response = self.client.post(url, self.settings_form(heading_font=make_font_file()))

        settings = SiteSettings.load()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(settings.heading_font.name.endswith(".woff2"))
        self.assertNotIn("fuente", settings.heading_font.name)
        self.assertFalse(settings.body_font)

    def test_fake_font_is_rejected(self):
        url = reverse("admin:site_content_sitesettings_change", args=[1])

        response = self.client.post(
            url, self.settings_form(body_font=make_fake_file("fuente.ttf"))
        )

        self.assertContains(response, "no es una fuente válida")
        self.assertFalse(SiteSettings.load().body_font)

    def test_estimate_can_be_turned_off(self):
        url = reverse("admin:site_content_sitesettings_change", args=[1])
        data = self.settings_form()
        del data["show_estimate"]

        self.client.post(url, data)

        self.assertFalse(SiteSettings.load().show_estimate)

    def test_legal_pages_are_listed_but_cannot_be_added_or_deleted(self):
        page = LegalPage.objects.get(slug="privacidad")

        pages = self.client.get(reverse("admin:site_content_legalpage_changelist"))
        add = self.client.get(reverse("admin:site_content_legalpage_add"))
        delete = self.client.post(
            reverse("admin:site_content_legalpage_delete", args=[page.pk]), {"post": "yes"}
        )

        self.assertContains(pages, "Política de privacidad")
        self.assertEqual(add.status_code, 403)
        self.assertEqual(delete.status_code, 403)
        self.assertEqual(LegalPage.objects.count(), 2)

    def test_legal_page_text_and_sections_can_be_edited(self):
        page = LegalPage.objects.get(slug="terminos")
        section = page.sections.first()

        response = self.client.post(
            reverse("admin:site_content_legalpage_change", args=[page.pk]),
            {
                "title": "Términos del servicio",
                "intro": "Introducción nueva",
                "sections-TOTAL_FORMS": 2,
                "sections-INITIAL_FORMS": 1,
                "sections-0-id": section.pk,
                "sections-0-page": page.pk,
                "sections-0-title": section.title,
                "sections-0-body": "Texto escrito por el cliente",
                "sections-0-order": 1,
                "sections-1-page": page.pk,
                "sections-1-title": "Apartado nuevo",
                "sections-1-body": "Otro texto",
                "sections-1-order": 2,
            },
        )

        page.refresh_from_db()
        section.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(page.title, "Términos del servicio")
        self.assertEqual(section.body, "Texto escrito por el cliente")
        self.assertTrue(page.sections.filter(title="Apartado nuevo").exists())

    def test_specialties_list_says_it_is_no_longer_shown_on_the_site(self):
        response = self.client.get(reverse("admin:site_content_specialty_changelist"))

        self.assertContains(response, "ya no se muestran en el sitio")
