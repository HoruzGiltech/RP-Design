from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.tests.helpers import TempMediaMixin, make_image_file, make_video_file
from projects.models import Project, ProjectMedia
from projects.tests.test_models import create_project


class ProjectAdminTests(TempMediaMixin, TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("dev", password="clave-de-prueba")
        self.client.force_login(user)

    def project_form_data(self, **fields):
        """Datos mínimos del formulario de proyecto, con la galería vacía."""
        data = {
            "title": "Cocina en Chacao",
            "slug": "cocina-en-chacao",
            "summary": "Resumen",
            "description": "Descripción",
            "cover_alt": "Cocina terminada",
            "featured_order": 0,
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
        project = create_project(slug="cocina-en-chacao")
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

    def test_fourth_featured_project_shows_a_clear_message(self):
        for number in range(3):
            create_project(title=f"Destacado {number}", is_featured=True)
        data = self.project_form_data(
            cover_image=make_image_file("portada.jpg"), is_featured="on"
        )

        response = self.client.post(reverse("admin:projects_project_add"), data)

        self.assertContains(response, "Ya hay 3 proyectos destacados")
        self.assertEqual(Project.objects.count(), 3)
