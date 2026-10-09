from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.tests.helpers import TempMediaMixin, make_image_file, make_video_file
from projects.models import Project, ProjectCategory, ProjectMedia
from projects.tests.test_models import create_project, get_category


class ProjectAdminTests(TempMediaMixin, TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("dev", password="clave-de-prueba")
        self.client.force_login(user)

    def project_form_data(self, **fields):
        """Datos mínimos del formulario de proyecto, con la galería vacía."""
        data = {
            "title": "Cocina en Chacao",
            "category": get_category().pk,
            "summary": "Resumen",
            "description": "Descripción",
            "cover_alt": "Cocina terminada",
            "hero_order": 0,
            "media-TOTAL_FORMS": 0,
            "media-INITIAL_FORMS": 0,
        }
        data.update(fields)
        return data

    def test_project_list_shows_the_cover_preview(self):
        project = create_project()

        response = self.client.get(reverse("admin:projects_project_changelist"))

        self.assertContains(response, project.cover_thumbnail.url)

    def test_project_can_be_created_with_images_and_a_video(self):
        data = self.project_form_data(
            cover_image=make_image_file("portada.jpg"),
            **{
                "media-TOTAL_FORMS": 2,
                "media-0-file": make_image_file("sala.jpg"),
                "media-0-alt_text": "Sala",
                "media-0-order": 1,
                "media-1-file": make_video_file("recorrido.mp4"),
                "media-1-alt_text": "Recorrido",
                "media-1-order": 2,
            },
        )

        response = self.client.post(reverse("admin:projects_project_add"), data)

        self.assertRedirects(response, reverse("admin:projects_project_changelist"))
        project = Project.objects.get()
        types = list(project.media.values_list("media_type", flat=True))
        self.assertEqual(types, [ProjectMedia.IMAGE, ProjectMedia.VIDEO])

    def test_gallery_order_is_saved(self):
        project = create_project(title="Cocina en Chacao")
        first = ProjectMedia.objects.create(
            project=project, file=make_image_file(), alt_text="Primera", order=1
        )
        second = ProjectMedia.objects.create(
            project=project, file=make_image_file(), alt_text="Segunda", order=2
        )
        # Lo mismo que envía el panel después de arrastrar la segunda al primer lugar
        data = self.project_form_data(
            **{
                "media-TOTAL_FORMS": 2,
                "media-INITIAL_FORMS": 2,
                "media-0-id": first.pk,
                "media-0-project": project.pk,
                "media-0-alt_text": "Primera",
                "media-0-order": 2,
                "media-1-id": second.pk,
                "media-1-project": project.pk,
                "media-1-alt_text": "Segunda",
                "media-1-order": 1,
            },
        )

        response = self.client.post(
            reverse("admin:projects_project_change", args=[project.pk]), data
        )

        self.assertRedirects(response, reverse("admin:projects_project_changelist"))
        alts = list(project.media.values_list("alt_text", flat=True))
        self.assertEqual(alts, ["Segunda", "Primera"])

    def test_seventh_project_in_the_hero_shows_a_clear_message(self):
        for number in range(6):
            create_project(title=f"Proyecto del hero {number}", show_in_hero=True)
        data = self.project_form_data(
            cover_image=make_image_file("portada.jpg"), show_in_hero="on"
        )

        response = self.client.post(reverse("admin:projects_project_add"), data)

        self.assertContains(response, "Ya hay 6 proyectos en el hero")
        self.assertEqual(Project.objects.count(), 6)

    def test_form_has_no_field_to_write_the_slug(self):
        response = self.client.get(reverse("admin:projects_project_add"))

        self.assertNotContains(response, 'name="slug"')
        self.assertContains(response, "Se genera sola al guardar")

    def test_slug_is_generated_when_the_project_is_created_from_the_panel(self):
        data = self.project_form_data(title="Casa", cover_image=make_image_file("portada.jpg"))

        self.client.post(reverse("admin:projects_project_add"), data)

        self.assertEqual(Project.objects.get().slug, "proyecto-casa")

    def test_category_is_required_in_the_form(self):
        data = self.project_form_data(cover_image=make_image_file("portada.jpg"), category="")

        response = self.client.post(reverse("admin:projects_project_add"), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 0)


class ProjectCategoryAdminTests(TempMediaMixin, TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("dev", password="clave-de-prueba")
        self.client.force_login(user)

    def test_category_list_shows_how_many_projects_each_one_has(self):
        create_project()

        response = self.client.get(reverse("admin:projects_projectcategory_changelist"))

        self.assertContains(response, "Residencial")
        self.assertContains(response, "Corporativo")
        # specs-002: cuántas áreas del formulario tiene cada categoría
        self.assertContains(response, "Áreas del formulario")

    def test_category_is_created_with_only_its_name(self):
        self.client.post(
            reverse("admin:projects_projectcategory_add"),
            {"name": "Hotelería", "is_visible": "on"},
        )

        self.assertEqual(ProjectCategory.objects.get(name="Hotelería").slug, "hoteleria")

    def test_category_can_be_hidden_from_the_list(self):
        # specs-003: la casilla se cambia directo en la lista
        response = self.client.get(reverse("admin:projects_projectcategory_changelist"))

        self.assertContains(response, "form-0-is_visible")
        self.assertTrue(all(category.is_visible for category in ProjectCategory.objects.all()))

    def test_category_with_projects_is_not_deleted_from_the_panel(self):
        category = create_project().category

        self.client.post(
            reverse("admin:projects_projectcategory_delete", args=[category.pk]), {"post": "yes"}
        )

        self.assertTrue(ProjectCategory.objects.filter(pk=category.pk).exists())
