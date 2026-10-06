from importlib import import_module

from django.apps import apps
from django.test import TestCase

from site_content.models import HeroSection

# El nombre del archivo empieza por un número, así que no se puede importar con "import"
hero_texts_migration = import_module("site_content.migrations.0007_hero_texts")


class HeroTextsMigrationTests(TestCase):
    """La migración 0007 cambia los textos de la Portada solo si siguen siendo los originales."""

    def run_migration(self):
        hero_texts_migration.update_hero_texts(apps, None)

    def test_original_texts_are_replaced(self):
        HeroSection.objects.update(
            title="Transformamos tus espacios, del plano a la obra.",
            primary_cta_text="Agenda una visita",
        )

        self.run_migration()

        hero = HeroSection.objects.get()
        self.assertEqual(hero.title, "")
        self.assertEqual(hero.primary_cta_text, "Agenda una reunión")

    def test_texts_changed_by_the_client_are_kept(self):
        HeroSection.objects.update(
            title="Un título escrito por el cliente", primary_cta_text="Hablemos"
        )

        self.run_migration()

        hero = HeroSection.objects.get()
        self.assertEqual(hero.title, "Un título escrito por el cliente")
        self.assertEqual(hero.primary_cta_text, "Hablemos")
