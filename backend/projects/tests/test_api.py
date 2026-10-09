from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from core.tests.helpers import TempMediaMixin, make_image_file, make_video_file
from projects.models import ProjectCategory, ProjectMedia
from projects.tests.test_models import create_project, get_category


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
            set(card),
            {
                "slug",
                "title",
                "summary",
                "description",
                "category",
                "cover_image",
                "cover_thumbnail",
                "cover_alt",
            },
        )
        # specs-003: la descripción completa se muestra sobre la portada
        self.assertEqual(card["description"], "Descripción del proyecto.")
        self.assertEqual(card["category"], {"name": "Residencial", "slug": "residencial"})
        self.assertEqual(
            card["cover_thumbnail"], f"http://testserver{project.cover_thumbnail.url}"
        )

    # --- Hero (specs-001, RF-08) ---

    def test_hero_filter_returns_hero_projects_in_their_own_order(self):
        create_project(title="Normal", is_published=True)
        create_project(title="B", is_published=True, show_in_hero=True, hero_order=2)
        create_project(title="A", is_published=True, show_in_hero=True, hero_order=1)
        create_project(title="Borrador", is_published=False, show_in_hero=True)

        response = self.client.get(self.url, {"hero": "true"})

        self.assertEqual([project["title"] for project in response.json()], ["A", "B"])

    def test_hero_filter_never_returns_more_than_six(self):
        # Se crean 7 saltando la validación del panel, para probar el tope de la API
        for number in range(7):
            create_project(title=f"Hero {number}", is_published=True, show_in_hero=True)

        response = self.client.get(self.url, {"hero": "true"})

        self.assertEqual(len(response.json()), 6)

    def test_without_hero_projects_the_list_is_empty(self):
        create_project(is_published=True)

        response = self.client.get(self.url, {"hero": "true"})

        self.assertEqual(response.json(), [])

    def test_hero_project_has_the_big_cover_image(self):
        project = create_project(is_published=True, show_in_hero=True)

        slide = self.client.get(self.url, {"hero": "true"}).json()[0]

        self.assertEqual(slide["cover_image"], f"http://testserver{project.cover_image.url}")

    # --- Categorías (specs-001, RF-09) ---

    def test_category_filter_returns_only_the_projects_of_that_category(self):
        create_project(title="Casa", is_published=True)
        create_project(title="Tienda", is_published=True, category=get_category("comercial"))
        create_project(
            title="Tienda en borrador", is_published=False, category=get_category("comercial")
        )

        response = self.client.get(self.url, {"category": "comercial"})

        self.assertEqual([project["title"] for project in response.json()], ["Tienda"])

    def test_unknown_category_returns_every_project(self):
        create_project(title="Casa", is_published=True)
        create_project(title="Tienda", is_published=True, category=get_category("comercial"))

        response = self.client.get(self.url, {"category": "no-existe"})

        self.assertEqual(len(response.json()), 2)

    def test_hidden_category_filter_returns_every_project(self):
        # specs-003: el filtro de una categoría oculta se comporta como "Todos"
        create_project(title="Casa", is_published=True)
        create_project(title="Tienda", is_published=True, category=get_category("comercial"))
        ProjectCategory.objects.filter(slug="comercial").update(is_visible=False)

        response = self.client.get(self.url, {"category": "comercial"})

        self.assertEqual(len(response.json()), 2)

    def test_project_of_a_hidden_category_is_still_listed_with_its_label(self):
        create_project(title="Tienda", is_published=True, category=get_category("comercial"))
        ProjectCategory.objects.filter(slug="comercial").update(is_visible=False)

        card = self.client.get(self.url).json()[0]

        self.assertEqual(card["title"], "Tienda")
        self.assertEqual(card["category"]["name"], "Comercial")

    def test_project_without_category_is_listed_with_null(self):
        project = create_project(is_published=True)
        # Caso de los proyectos anteriores a las categorías que la migración no pudo asociar
        type(project).objects.filter(pk=project.pk).update(category=None)

        card = self.client.get(self.url).json()[0]

        self.assertIsNone(card["category"])

    def test_api_is_read_only(self):
        for method in [self.client.post, self.client.put, self.client.delete]:
            self.assertEqual(method(self.url).status_code, 405)


class ProjectDetailApiTests(TempMediaMixin, TestCase):
    def setUp(self):
        cache.clear()

    def test_detail_has_the_project_data(self):
        project = create_project(
            is_published=True, location="Caracas", year=2025
        )

        data = self.client.get(reverse("project-detail", args=[project.slug])).json()

        self.assertEqual(data["title"], "Casa en El Hatillo")
        self.assertEqual(data["category"], {"name": "Residencial", "slug": "residencial"})
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


class ProjectCategoryApiTests(TempMediaMixin, TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("project-category-list")

    def get_categories(self):
        return self.client.get(self.url).json()

    def test_only_categories_with_published_projects_are_listed(self):
        create_project(title="Casa", is_published=True)
        create_project(title="Tienda", is_published=False, category=get_category("comercial"))

        self.assertEqual([category["name"] for category in self.get_categories()], ["Residencial"])

    def test_without_published_projects_the_list_is_empty(self):
        self.assertEqual(self.get_categories(), [])

    def test_hidden_category_is_not_listed(self):
        # specs-003: la casilla "mostrar en el sitio" de la categoría
        create_project(title="Casa", is_published=True)
        create_project(title="Tienda", is_published=True, category=get_category("comercial"))
        ProjectCategory.objects.filter(slug="comercial").update(is_visible=False)

        self.assertEqual([category["slug"] for category in self.get_categories()], ["residencial"])

    def test_categories_follow_the_order_of_the_panel(self):
        create_project(title="Oficina", is_published=True, category=get_category("corporativo"))
        create_project(title="Tienda", is_published=True, category=get_category("comercial"))

        self.assertEqual(
            [category["slug"] for category in self.get_categories()], ["comercial", "corporativo"]
        )

    def test_project_count_only_counts_published_projects(self):
        create_project(title="Casa uno", is_published=True)
        create_project(title="Casa dos", is_published=True)
        create_project(title="Casa en borrador", is_published=False)

        category = self.get_categories()[0]

        self.assertEqual(
            set(category), {"name", "slug", "project_count", "cover_thumbnail", "cover_alt"}
        )
        self.assertEqual(category["project_count"], 2)

    def test_cover_is_the_project_marked_by_the_client(self):
        create_project(title="Primero", is_published=True, order=1, cover_alt="Foto del primero")
        chosen = create_project(
            title="Elegido",
            is_published=True,
            order=2,
            cover_alt="Foto elegida",
            is_category_cover=True,
        )

        category = self.get_categories()[0]

        self.assertEqual(category["cover_alt"], "Foto elegida")
        self.assertEqual(
            category["cover_thumbnail"], f"http://testserver{chosen.cover_thumbnail.url}"
        )

    def test_without_a_marked_cover_the_first_published_project_is_used(self):
        create_project(title="Segundo", is_published=True, order=2, cover_alt="Foto del segundo")
        create_project(title="Primero", is_published=True, order=1, cover_alt="Foto del primero")

        self.assertEqual(self.get_categories()[0]["cover_alt"], "Foto del primero")

    def test_a_draft_marked_as_cover_is_not_used(self):
        create_project(title="Publicado", is_published=True, cover_alt="Foto publicada")
        create_project(
            title="Borrador", is_published=False, cover_alt="Foto oculta", is_category_cover=True
        )

        self.assertEqual(self.get_categories()[0]["cover_alt"], "Foto publicada")

    def test_api_is_read_only(self):
        for method in [self.client.post, self.client.put, self.client.delete]:
            self.assertEqual(method(self.url).status_code, 405)
