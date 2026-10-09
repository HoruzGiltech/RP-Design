from importlib import import_module

from django.apps import apps
from django.test import TestCase

from site_content.models import HeroSection, ProcessStep, ProjectsSection, Specialty

# El nombre del archivo empieza por un número, así que no se puede importar con "import"
hero_texts_migration = import_module("site_content.migrations.0007_hero_texts")
specialty_migration = import_module("site_content.migrations.0009_specialty_corporativo")
button_migration = import_module("site_content.migrations.0015_projects_button_text")


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


class SpecialtyMigrationTests(TestCase):
    """La migración 0009 cambia "Renders 3D" por "Corporativo" solo en la franja."""

    def run_migration(self):
        specialty_migration.update_specialty(apps, None)

    def test_original_text_is_replaced(self):
        Specialty.objects.filter(text="Corporativo").update(text="Renders 3D")

        self.run_migration()

        self.assertFalse(Specialty.objects.filter(text="Renders 3D").exists())
        self.assertTrue(Specialty.objects.filter(text="Corporativo").exists())

    def test_text_changed_by_the_client_is_kept(self):
        Specialty.objects.filter(text="Corporativo").update(text="Paisajismo")

        self.run_migration()

        self.assertTrue(Specialty.objects.filter(text="Paisajismo").exists())
        self.assertFalse(Specialty.objects.filter(text="Corporativo").exists())

    def test_process_step_is_not_changed(self):
        self.run_migration()

        self.assertTrue(ProcessStep.objects.filter(title="Renders 3D").exists())


class ProjectsButtonMigrationTests(TestCase):
    """La migración 0015 cambia el texto del botón de Proyectos solo si es el original."""

    def run_migration(self):
        button_migration.update_button_text(apps, None)

    def test_original_text_is_replaced(self):
        ProjectsSection.objects.update(view_all_text="Ver todos los proyectos")

        self.run_migration()

        self.assertEqual(ProjectsSection.objects.get().view_all_text, "Ver proyectos")

    def test_text_changed_by_the_client_is_kept(self):
        ProjectsSection.objects.update(view_all_text="Conoce nuestro trabajo")

        self.run_migration()

        self.assertEqual(ProjectsSection.objects.get().view_all_text, "Conoce nuestro trabajo")
