from django.core.exceptions import ValidationError
from django.test import TestCase
from PIL import Image

from core.tests.helpers import TempMediaMixin, make_fake_file, make_image_file
from site_content.models import (
    ContactSection,
    FooterSection,
    HeroSection,
    ProcessSection,
    ProcessStep,
    ProjectsSection,
    SeoSettings,
    Service,
    ServicesSection,
    SiteSettings,
    Specialty,
)


class InitialContentTests(TestCase):
    """El contenido inicial lo carga una migración de datos, con los textos de la maqueta."""

    def test_site_settings_has_the_contact_data_of_the_mockup(self):
        settings = SiteSettings.objects.get()

        self.assertEqual(settings.brand_initials, "RP")
        self.assertEqual(settings.brand_name, "RP DISEÑO")
        self.assertEqual(settings.brand_subtitle, "INTERIOR · ARQUITECTURA")
        self.assertEqual(settings.header_cta_text, "Cotiza tu proyecto")
        self.assertEqual(settings.accent_color, "#111111")
        self.assertEqual(settings.whatsapp_number, "584127305964")
        self.assertEqual(settings.whatsapp_greeting, "Hola! quiero agendar una reunión")
        self.assertTrue(settings.show_whatsapp_button)
        self.assertEqual(settings.instagram_handle, "rpdesign_ve")
        self.assertEqual(settings.city, "Caracas, Venezuela")
        self.assertEqual(settings.max_square_meters, 500)
        self.assertTrue(settings.price_note.startswith("Precio referencial en USD"))

    def test_every_section_exists_with_its_title(self):
        # specs-001: el título de la Portada queda vacío y el botón cambia de texto
        self.assertEqual(HeroSection.objects.get().title, "")
        self.assertEqual(HeroSection.objects.get().primary_cta_text, "Agenda una reunión")
        self.assertEqual(
            ServicesSection.objects.get().title, "Un solo equipo para todo tu proyecto"
        )
        self.assertEqual(ProjectsSection.objects.get().title, "Proyectos recientes")
        self.assertEqual(
            ProcessSection.objects.get().title, "Ve tu espacio antes de construirlo"
        )
        self.assertEqual(ContactSection.objects.get().title, "Cuéntanos sobre tu espacio")
        self.assertEqual(ContactSection.objects.get().submit_text, "Enviar por WhatsApp")
        self.assertEqual(FooterSection.objects.get().name, "RP DISEÑO INTERIOR")
        self.assertEqual(SeoSettings.objects.get().site_title, "RP Diseño Interior")

    def test_sections_are_visible_by_default(self):
        self.assertTrue(HeroSection.objects.get().is_visible)
        self.assertTrue(ContactSection.objects.get().is_visible)

    def test_lists_have_the_items_of_the_mockup_in_order(self):
        self.assertEqual(
            list(Specialty.objects.values_list("text", flat=True)),
            ["Diseño residencial", "Diseño comercial", "Renders 3D", "Ejecución de obra"],
        )
        self.assertEqual(
            list(Service.objects.values_list("title", flat=True)),
            ["Levantamiento de espacio", "Proyecto de diseño", "Ejecución de obra"],
        )
        self.assertEqual(
            list(ProcessStep.objects.values_list("title", flat=True)),
            ["Renders 3D", "Video recorridos", "Planimetría", "Ejecución de obra"],
        )


class SiteSettingsValidationTests(TestCase):
    def test_whatsapp_number_must_be_only_digits(self):
        settings = SiteSettings.load()
        settings.whatsapp_number = "+58 412-7305964"

        with self.assertRaises(ValidationError) as error:
            settings.full_clean()

        self.assertIn("whatsapp_number", error.exception.message_dict)

    def test_accent_color_must_be_one_of_the_four_options(self):
        settings = SiteSettings.load()
        settings.accent_color = "#FF0000"

        with self.assertRaises(ValidationError) as error:
            settings.full_clean()

        self.assertIn("accent_color", error.exception.message_dict)


class SectionFilesTests(TempMediaMixin, TestCase):
    def test_hero_image_is_reduced_and_renamed(self):
        hero = HeroSection.load()
        hero.image = make_image_file("fachada.jpg", size=(4000, 3000))
        hero.save()

        self.assertEqual(Image.open(hero.image).size, (1920, 1440))
        self.assertRegex(hero.image.name, r"^site/\d{4}/[0-9a-f]{32}\.jpg$")

    def test_saving_again_keeps_the_same_image(self):
        hero = HeroSection.load()
        hero.image = make_image_file()
        hero.save()
        image_name = hero.image.name

        hero = HeroSection.load()
        hero.title = "Otro título"
        hero.save()

        self.assertEqual(hero.image.name, image_name)

    def test_hero_video_must_be_a_real_video(self):
        hero = HeroSection.load()
        hero.video = make_fake_file("portada.mp4")

        with self.assertRaises(ValidationError) as error:
            hero.full_clean()

        self.assertIn("video", error.exception.message_dict)

    def test_hero_works_without_image_or_video(self):
        hero = HeroSection.load()

        hero.full_clean()

        self.assertFalse(hero.image)
        self.assertFalse(hero.video)
