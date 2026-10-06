from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase
from PIL import Image

from core.tests.helpers import (
    TempMediaMixin,
    make_fake_file,
    make_image_file,
    make_video_file,
)
from projects.models import Project, ProjectCategory, ProjectMedia


def get_category(slug="residencial"):
    """Las categorías iniciales las crea la migración projects.0003."""
    return ProjectCategory.objects.get(slug=slug)


def create_project(**fields):
    """Crea un proyecto válido; cada test cambia solo lo que le interesa."""
    values = {
        "category": get_category(),
        "title": "Casa en El Hatillo",
        "summary": "Remodelación completa.",
        "description": "Descripción del proyecto.",
        "cover_image": make_image_file("portada.jpg"),
        "cover_alt": "Fachada de la casa",
    }
    values.update(fields)
    return Project.objects.create(**values)


class ProjectCoverTests(TempMediaMixin, TestCase):
    def test_cover_is_reduced_and_thumbnail_is_created(self):
        project = create_project(cover_image=make_image_file(size=(4000, 3000)))

        self.assertEqual(Image.open(project.cover_image).size, (1920, 1440))
        self.assertEqual(Image.open(project.cover_thumbnail).size, (600, 450))

    def test_files_are_renamed(self):
        project = create_project(cover_image=make_image_file("casa de ana.jpg"))

        self.assertRegex(project.cover_image.name, r"^projects/\d{4}/[0-9a-f]{32}\.jpg$")
        self.assertRegex(project.cover_thumbnail.name, r"^projects/\d{4}/[0-9a-f]{32}\.jpg$")
        self.assertNotEqual(project.cover_image.name, project.cover_thumbnail.name)

    def test_saving_without_changing_the_cover_keeps_the_same_files(self):
        project = create_project()
        cover_name = project.cover_image.name
        thumbnail_name = project.cover_thumbnail.name

        project = Project.objects.get(pk=project.pk)
        project.title = "Otro título"
        project.save()

        self.assertEqual(project.cover_image.name, cover_name)
        self.assertEqual(project.cover_thumbnail.name, thumbnail_name)

    def test_changing_the_cover_creates_a_new_thumbnail(self):
        project = create_project()
        old_thumbnail_name = project.cover_thumbnail.name

        project.cover_image = make_image_file("nueva.png", image_format="PNG")
        project.save()

        self.assertNotEqual(project.cover_thumbnail.name, old_thumbnail_name)
        self.assertTrue(project.cover_thumbnail.name.endswith(".png"))

    def test_fake_image_does_not_pass_validation(self):
        project = Project(
            title="Proyecto",
            category=get_category(),
            summary="Resumen",
            description="Descripción",
            cover_image=make_fake_file("portada.jpg"),
            cover_alt="Portada",
        )

        with self.assertRaises(ValidationError) as error:
            project.full_clean()

        self.assertIn("cover_image", error.exception.message_dict)


class ProjectSlugTests(TempMediaMixin, TestCase):
    """La dirección web se genera sola (specs-001, RF-10)."""

    def test_slug_is_created_from_the_title(self):
        project = create_project(title="Cocina Moderna en Chacao")

        self.assertEqual(project.slug, "cocina-moderna-en-chacao")

    def test_single_word_title_gets_the_word_proyecto_first(self):
        project = create_project(title="Casa")

        self.assertEqual(project.slug, "proyecto-casa")

    def test_repeated_title_gets_a_different_slug(self):
        create_project(title="Baño principal")
        second = create_project(title="Baño principal")
        third = create_project(title="Baño principal")

        self.assertEqual(second.slug, "bano-principal-2")
        self.assertEqual(third.slug, "bano-principal-3")

    def test_slug_does_not_change_when_the_title_is_edited(self):
        project = create_project(title="Cocina en Chacao")

        project.title = "Otra cosa distinta"
        project.save()

        self.assertEqual(project.slug, "cocina-en-chacao")

    def test_slug_cannot_be_written_in_a_form(self):
        self.assertFalse(Project._meta.get_field("slug").editable)


class ProjectCategoryTests(TempMediaMixin, TestCase):
    def test_three_categories_exist_in_order(self):
        names = list(ProjectCategory.objects.values_list("name", flat=True))

        self.assertEqual(names, ["Comercial", "Residencial", "Corporativo"])

    def test_category_slug_is_created_from_the_name_without_the_word_proyecto(self):
        category = ProjectCategory.objects.create(name="Diseño de Oficinas")
        single_word = ProjectCategory.objects.create(name="Hotelería")

        self.assertEqual(category.slug, "diseno-de-oficinas")
        self.assertEqual(single_word.slug, "hoteleria")

    def test_category_slug_does_not_change_when_the_name_is_edited(self):
        category = get_category("comercial")

        category.name = "Locales"
        category.save()

        self.assertEqual(category.slug, "comercial")

    def test_category_with_projects_cannot_be_deleted(self):
        project = create_project()

        with self.assertRaises(ProtectedError):
            project.category.delete()

    def test_project_requires_a_category(self):
        project = Project(
            title="Sin categoría",
            summary="Resumen",
            description="Descripción",
            cover_image=make_image_file(),
            cover_alt="Portada",
        )

        with self.assertRaises(ValidationError) as error:
            project.full_clean()

        self.assertIn("category", error.exception.message_dict)

    def test_only_one_project_is_the_cover_of_its_category(self):
        first = create_project(title="Primero", is_category_cover=True)
        second = create_project(title="Segundo", is_category_cover=True)

        first.refresh_from_db()
        self.assertFalse(first.is_category_cover)
        self.assertTrue(second.is_category_cover)

    def test_cover_of_another_category_is_not_touched(self):
        residential = create_project(title="Casa grande", is_category_cover=True)
        create_project(
            title="Local nuevo", category=get_category("comercial"), is_category_cover=True
        )

        residential.refresh_from_db()
        self.assertTrue(residential.is_category_cover)


class ProjectDefaultsTests(TempMediaMixin, TestCase):
    def test_new_project_is_a_draft_and_not_in_the_hero(self):
        project = create_project()

        self.assertFalse(project.is_published)
        self.assertFalse(project.show_in_hero)
        self.assertFalse(project.is_category_cover)

    def test_projects_are_sorted_by_order(self):
        create_project(title="Segundo", order=2)
        create_project(title="Primero", order=1)

        titles = list(Project.objects.values_list("title", flat=True))

        self.assertEqual(titles, ["Primero", "Segundo"])


class HeroLimitTests(TempMediaMixin, TestCase):
    """Como máximo 6 proyectos en el hero (specs-001, RF-08.11)."""

    def create_hero_projects(self, amount, **fields):
        return [
            create_project(title=f"Proyecto del hero {number}", show_in_hero=True, **fields)
            for number in range(amount)
        ]

    def test_six_projects_in_the_hero_are_allowed(self):
        for project in self.create_hero_projects(6):
            project.full_clean()

    def test_seventh_project_in_the_hero_is_rejected(self):
        self.create_hero_projects(6)
        seventh = create_project(title="El séptimo")
        seventh.show_in_hero = True

        with self.assertRaises(ValidationError) as error:
            seventh.full_clean()

        self.assertEqual(
            error.exception.message_dict["show_in_hero"],
            ["Ya hay 6 proyectos en el hero. Quita uno antes de agregar otro."],
        )

    def test_editing_a_project_that_is_already_in_the_hero_is_allowed(self):
        projects = self.create_hero_projects(6)

        first = projects[0]
        first.summary = "Resumen nuevo"
        first.full_clean()

    def test_drafts_also_count_towards_the_limit(self):
        self.create_hero_projects(6, is_published=False)
        seventh = create_project(title="El séptimo")
        seventh.show_in_hero = True

        with self.assertRaises(ValidationError):
            seventh.full_clean()


class ProjectMediaTests(TempMediaMixin, TestCase):
    def test_image_is_detected_reduced_and_gets_a_thumbnail(self):
        media = ProjectMedia.objects.create(
            project=create_project(),
            file=make_image_file("sala.jpg", size=(4000, 3000)),
            alt_text="Sala",
        )

        self.assertEqual(media.media_type, ProjectMedia.IMAGE)
        self.assertFalse(media.is_video)
        self.assertEqual(Image.open(media.file).size, (1920, 1440))
        self.assertEqual(Image.open(media.thumbnail).size, (600, 450))

    def test_video_is_detected_and_is_not_modified(self):
        video = make_video_file("recorrido.mp4")
        original_size = video.size

        media = ProjectMedia.objects.create(
            project=create_project(), file=video, alt_text="Recorrido"
        )

        self.assertEqual(media.media_type, ProjectMedia.VIDEO)
        self.assertTrue(media.is_video)
        self.assertFalse(media.thumbnail)
        self.assertEqual(media.file.size, original_size)
        self.assertRegex(media.file.name, r"^projects/\d{4}/[0-9a-f]{32}\.mp4$")

    def test_video_poster_is_reduced(self):
        media = ProjectMedia.objects.create(
            project=create_project(),
            file=make_video_file(),
            poster=make_image_file("poster.jpg", size=(4000, 3000)),
            alt_text="Recorrido",
        )

        self.assertEqual(Image.open(media.poster).size, (1920, 1440))

    def test_gallery_is_sorted_by_order(self):
        project = create_project()
        ProjectMedia.objects.create(
            project=project, file=make_image_file(), alt_text="Segunda", order=2
        )
        ProjectMedia.objects.create(
            project=project, file=make_image_file(), alt_text="Primera", order=1
        )

        alts = list(project.media.values_list("alt_text", flat=True))

        self.assertEqual(alts, ["Primera", "Segunda"])

    def test_deleting_the_project_deletes_its_gallery(self):
        project = create_project()
        ProjectMedia.objects.create(project=project, file=make_image_file(), alt_text="Sala")

        project.delete()

        self.assertEqual(ProjectMedia.objects.count(), 0)

    def test_exe_renamed_to_video_does_not_pass_validation(self):
        media = ProjectMedia(
            project=create_project(), file=make_fake_file("video.mp4"), alt_text="Video"
        )

        with self.assertRaises(ValidationError) as error:
            media.full_clean()

        self.assertIn("file", error.exception.message_dict)
