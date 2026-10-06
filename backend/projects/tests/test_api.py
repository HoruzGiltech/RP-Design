from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from core.tests.helpers import TempMediaMixin, make_image_file, make_video_file
from projects.models import ProjectMedia
from projects.tests.test_models import create_project


class ProjectListApiTests(TempMediaMixin, TestCase):
    def setUp(self):
        # El límite de peticiones se guarda en caché: se limpia para que un test no afecte a otro
        cache.clear()
        self.url = reverse("project-list")

    def test_only_published_projects_are_listed(self):
        create_project(title="Publicado", is_published=True)
        create_project(title="Borrador", is_published=False)

        response = self.client.get(self.url)

        self.assertEqual([project["title"] for project in response.json()], ["Publicado"])

    def test_projects_follow_the_order_of_the_panel(self):
        create_project(title="Segundo", is_published=True, order=2)
        create_project(title="Primero", is_published=True, order=1)

        response = self.client.get(self.url)

        self.assertEqual(
            [project["title"] for project in response.json()], ["Primero", "Segundo"]
        )

    def test_card_has_the_thumbnail_with_a_full_url_and_not_the_big_image(self):
        project = create_project(is_published=True)

        card = self.client.get(self.url).json()[0]

        self.assertEqual(
            set(card), {"slug", "title", "summary", "category", "cover_thumbnail", "cover_alt"}
        )
        self.assertEqual(
            card["cover_thumbnail"], f"http://testserver{project.cover_thumbnail.url}"
        )

    def test_featured_filter_returns_featured_in_their_own_order(self):
        create_project(title="Normal", is_published=True)
        create_project(title="B", is_published=True, is_featured=True, featured_order=2)
        create_project(title="A", is_published=True, is_featured=True, featured_order=1)
        create_project(title="Borrador", is_published=False, is_featured=True)

        response = self.client.get(self.url, {"featured": "true"})

        self.assertEqual([project["title"] for project in response.json()], ["A", "B"])

    def test_featured_filter_never_returns_more_than_three(self):
        # Se crean 4 saltando la validación del panel, para probar el tope de la API
        for number in range(4):
            create_project(title=f"D{number}", is_published=True, is_featured=True)

        response = self.client.get(self.url, {"featured": "true"})

        self.assertEqual(len(response.json()), 3)

    def test_without_featured_projects_the_list_is_empty(self):
        create_project(is_published=True)

        response = self.client.get(self.url, {"featured": "true"})

        self.assertEqual(response.json(), [])

    def test_api_is_read_only(self):
        for method in [self.client.post, self.client.put, self.client.delete]:
            self.assertEqual(method(self.url).status_code, 405)


class ProjectDetailApiTests(TempMediaMixin, TestCase):
    def setUp(self):
        cache.clear()

    def test_detail_has_the_project_data(self):
        project = create_project(
            is_published=True, category="Cocina", location="Caracas", year=2025
        )

        data = self.client.get(reverse("project-detail", args=[project.slug])).json()

        self.assertEqual(data["title"], "Casa en El Hatillo")
        self.assertEqual(data["category"], "Cocina")
        self.assertEqual(data["location"], "Caracas")
        self.assertEqual(data["year"], 2025)
        self.assertEqual(data["cover_image"], f"http://testserver{project.cover_image.url}")

    def test_gallery_follows_the_order_of_the_panel(self):
        project = create_project(is_published=True)
        ProjectMedia.objects.create(
            project=project, file=make_video_file(), alt_text="Tercero", order=3
        )
        ProjectMedia.objects.create(
            project=project, file=make_image_file(), alt_text="Segundo", order=2
        )
        ProjectMedia.objects.create(
            project=project, file=make_image_file(), alt_text="Primero", order=1
        )

        media = self.client.get(reverse("project-detail", args=[project.slug])).json()["media"]

        self.assertEqual([item["alt_text"] for item in media], ["Primero", "Segundo", "Tercero"])
        self.assertEqual([item["media_type"] for item in media], ["image", "image", "video"])
        self.assertTrue(media[0]["thumbnail"].startswith("http://testserver/media/projects/"))
        self.assertIsNone(media[2]["thumbnail"])
        self.assertIsNone(media[2]["poster"])

    def test_draft_gives_404(self):
        project = create_project(is_published=False)

        response = self.client.get(reverse("project-detail", args=[project.slug]))

        self.assertEqual(response.status_code, 404)

    def test_unknown_slug_gives_404(self):
        response = self.client.get(reverse("project-detail", args=["no-existe"]))

        self.assertEqual(response.status_code, 404)
