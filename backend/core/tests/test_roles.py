import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

from core.roles import ADMIN_GROUP, VIEWER_GROUP
from core.tests.helpers import TempMediaMixin, make_image_file
from projects.models import Project, ProjectCategory
from projects.tests.test_models import create_project
from quotes.models import Quote, RemodelArea
from quotes.tests.test_models_and_admin import create_quote
from site_content.models import HeroSection, QuoteFormField, Service

User = get_user_model()

# Modelos que el cliente gestiona en el panel: (app, modelo)
CONTENT_MODELS = [
    ("projects", "project"),
    ("projects", "projectcategory"),
    ("projects", "projectmedia"),
    ("quotes", "remodelarea"),
    ("quotes", "quote"),
    ("quotes", "quoteitem"),
    ("site_content", "sitesettings"),
    ("site_content", "herosection"),
    ("site_content", "servicessection"),
    ("site_content", "projectssection"),
    ("site_content", "processsection"),
    ("site_content", "contactsection"),
    ("site_content", "footersection"),
    ("site_content", "seosettings"),
    ("site_content", "specialty"),
    ("site_content", "service"),
    ("site_content", "processstep"),
    ("site_content", "legalpage"),
    ("site_content", "legalsection"),
    ("site_content", "quoteformfield"),
]

# Páginas de lista que tienen entrada en el menú del panel
LIST_PAGES = [
    "projects_project",
    "projects_projectcategory",
    "quotes_remodelarea",
    "quotes_quote",
    "site_content_specialty",
    "site_content_legalpage",
]


def create_staff_user(username, group_name):
    """Usuario del panel con un rol. No es superusuario."""
    user = User.objects.create_user(username, password="clave-de-prueba", is_staff=True)
    user.groups.add(Group.objects.get(name=group_name))
    return user


def codenames(group_name):
    group = Group.objects.get(name=group_name)
    return set(group.permissions.values_list("codename", flat=True))


class GroupsTests(TestCase):
    """Los grupos los crea la migración core.0001_create_groups."""

    def test_both_groups_exist_after_migrate(self):
        names = set(Group.objects.values_list("name", flat=True))

        self.assertEqual(names, {ADMIN_GROUP, VIEWER_GROUP})

    def test_admin_has_every_permission_of_every_content_model(self):
        admin_codenames = codenames(ADMIN_GROUP)

        for _app, model in CONTENT_MODELS:
            for action in ["add", "change", "delete", "view"]:
                self.assertIn(f"{action}_{model}", admin_codenames)

    def test_admin_can_manage_users_and_groups(self):
        admin_codenames = codenames(ADMIN_GROUP)

        for model in ["user", "group"]:
            for action in ["add", "change", "delete", "view"]:
                self.assertIn(f"{action}_{model}", admin_codenames)

    def test_viewer_only_has_view_permissions_of_content(self):
        viewer_codenames = codenames(VIEWER_GROUP)

        self.assertEqual(viewer_codenames, {f"view_{model}" for _app, model in CONTENT_MODELS})

    def test_no_content_permission_is_left_out_of_the_admin_group(self):
        # Si alguien agrega un modelo y olvida dar sus permisos, este test avisa
        all_content = Permission.objects.filter(
            content_type__app_label__in=["projects", "quotes", "site_content"]
        )

        missing = set(all_content.values_list("codename", flat=True)) - codenames(ADMIN_GROUP)

        self.assertEqual(missing, set())


class ViewerPermissionsTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.client.force_login(create_staff_user("visor", VIEWER_GROUP))
        self.project = create_project()
        self.quote = create_quote()

    def test_can_see_every_list(self):
        for page in LIST_PAGES:
            with self.subTest(page=page):
                response = self.client.get(reverse(f"admin:{page}_changelist"))

                self.assertEqual(response.status_code, 200)

    def test_can_open_a_record_but_sees_no_save_or_delete_buttons(self):
        pages = [
            reverse("admin:projects_project_change", args=[self.project.pk]),
            reverse("admin:quotes_quote_change", args=[self.quote.pk]),
            reverse("admin:site_content_herosection_change", args=[1]),
            reverse("admin:site_content_sitesettings_change", args=[1]),
            # Secciones que llevan una tabla dentro (specs-003)
            reverse("admin:site_content_servicessection_change", args=[1]),
            reverse("admin:site_content_processsection_change", args=[1]),
            reverse("admin:site_content_contactsection_change", args=[1]),
        ]
        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'name="_save"')
                self.assertNotContains(response, "deletelink")

    def test_lists_have_no_add_button_or_editable_fields(self):
        projects = self.client.get(reverse("admin:projects_project_changelist"))
        areas = self.client.get(reverse("admin:quotes_remodelarea_changelist"))

        self.assertNotContains(projects, "addlink")
        self.assertNotContains(areas, 'name="_save"')
        self.assertNotContains(areas, "form-0-price_per_m2")

    def test_cannot_add(self):
        for app, model in [("projects", "project"), ("projects", "projectcategory")]:
            with self.subTest(model=model):
                url = reverse(f"admin:{app}_{model}_add")

                self.assertEqual(self.client.get(url).status_code, 403)
                self.assertEqual(self.client.post(url, {"title": "Nuevo"}).status_code, 403)

        self.assertEqual(Project.objects.count(), 1)

    def test_cannot_edit_by_direct_post(self):
        self.client.post(
            reverse("admin:projects_project_change", args=[self.project.pk]),
            {
                "title": "Cambiado por el visor",
                "category": self.project.category.pk,
                "summary": "x",
                "description": "x",
                "cover_alt": "x",
                "cover_image": make_image_file(),
                "hero_order": 0,
                "media-TOTAL_FORMS": 0,
                "media-INITIAL_FORMS": 0,
            },
        )
        hero_response = self.client.post(
            reverse("admin:site_content_herosection_change", args=[1]),
            {"title": "Cambiado", "primary_cta_text": "x", "secondary_cta_text": "x"},
        )

        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Casa en El Hatillo")
        self.assertEqual(hero_response.status_code, 403)
        self.assertNotEqual(HeroSection.objects.get().title, "Cambiado")

    def test_cannot_edit_the_lists_inside_a_section(self):
        # specs-003: servicios y textos del formulario se editan dentro de su sección
        service = Service.objects.first()
        form_field = QuoteFormField.objects.get(key="name")

        services_response = self.client.post(
            reverse("admin:site_content_servicessection_change", args=[1]),
            {
                "title": "x",
                "items-TOTAL_FORMS": 1,
                "items-INITIAL_FORMS": 1,
                "items-0-id": service.pk,
                "items-0-section": 1,
                "items-0-title": "Cambiado por el visor",
                "items-0-description": "x",
                "items-0-order": 1,
            },
        )
        contact_response = self.client.post(
            reverse("admin:site_content_contactsection_change", args=[1]),
            {
                "title": "x",
                "submit_text": "x",
                "form_fields-TOTAL_FORMS": 1,
                "form_fields-INITIAL_FORMS": 1,
                "form_fields-0-id": form_field.pk,
                "form_fields-0-section": 1,
                "form_fields-0-label": "Cambiado por el visor",
            },
        )

        service.refresh_from_db()
        form_field.refresh_from_db()
        self.assertEqual(services_response.status_code, 403)
        self.assertEqual(contact_response.status_code, 403)
        self.assertNotEqual(service.title, "Cambiado por el visor")
        self.assertEqual(form_field.label, "Nombre")

    def test_cannot_delete(self):
        url = reverse("admin:projects_project_delete", args=[self.project.pk])

        response = self.client.post(url, {"post": "yes"})

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_cannot_delete_from_the_list_action(self):
        self.client.post(
            reverse("admin:projects_project_changelist"),
            {"action": "delete_selected", "_selected_action": [self.project.pk], "post": "yes"},
        )

        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_cannot_reorder(self):
        response = self.client.post(
            reverse("admin:projects_project_sortable_update"),
            data=json.dumps({"updatedItems": [[self.project.pk, 99]]}),
            content_type="application/json",
        )

        self.project.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(self.project.order, 99)

    def test_cannot_change_prices_or_quote_status_from_the_lists(self):
        area = RemodelArea.objects.get(slug="cocina")
        list_form = {"form-TOTAL_FORMS": 1, "form-INITIAL_FORMS": 1, "_save": "Guardar"}

        self.client.post(
            reverse("admin:quotes_remodelarea_changelist"),
            {**list_form, "form-0-id": area.pk, "form-0-price_per_m2": "999"},
        )
        self.client.post(
            reverse("admin:quotes_quote_changelist"),
            {**list_form, "form-0-id": self.quote.pk, "form-0-status": Quote.CLOSED},
        )

        area.refresh_from_db()
        self.quote.refresh_from_db()
        self.assertIsNone(area.price_per_m2)
        self.assertEqual(self.quote.status, Quote.NEW)

    def test_cannot_see_users(self):
        response = self.client.get(reverse("admin:auth_user_changelist"))

        self.assertEqual(response.status_code, 403)


class AdminRoleTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.user = create_staff_user("cliente", ADMIN_GROUP)
        self.client.force_login(self.user)

    def test_is_not_a_superuser(self):
        self.assertFalse(self.user.is_superuser)

    def test_can_create_edit_and_delete_content(self):
        add_url = reverse("admin:projects_projectcategory_add")
        self.client.post(add_url, {"name": "Hotelería", "is_visible": "on"})
        category = ProjectCategory.objects.get(name="Hotelería")

        change_url = reverse("admin:projects_projectcategory_change", args=[category.pk])
        self.client.post(change_url, {"name": "Hoteles", "is_visible": "on"})
        category.refresh_from_db()
        self.assertEqual(category.name, "Hoteles")

        delete_url = reverse("admin:projects_projectcategory_delete", args=[category.pk])
        self.client.post(delete_url, {"post": "yes"})
        self.assertFalse(ProjectCategory.objects.filter(pk=category.pk).exists())

    def test_can_edit_the_services_inside_their_section(self):
        # specs-003: los servicios ya no tienen entrada propia en el menú
        Service.objects.all().delete()

        self.client.post(
            reverse("admin:site_content_servicessection_change", args=[1]),
            {
                "is_visible": "on",
                "title": "Servicios",
                "cta_text": "Cotizar",
                "items-TOTAL_FORMS": 1,
                "items-INITIAL_FORMS": 0,
                "items-0-section": 1,
                "items-0-title": "Asesoría",
                "items-0-description": "x",
                "items-0-is_visible": "on",
                "items-0-order": 1,
            },
        )

        self.assertTrue(Service.objects.filter(title="Asesoría").exists())

    def test_can_reorder_projects(self):
        project = create_project()

        response = self.client.post(
            reverse("admin:projects_project_sortable_update"),
            data=json.dumps({"updatedItems": [[project.pk, 5]]}),
            content_type="application/json",
        )

        project.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(project.order, 5)

    def test_can_change_prices_and_quote_status(self):
        area = RemodelArea.objects.get(slug="cocina")
        quote = create_quote()

        self.client.post(
            reverse("admin:quotes_remodelarea_change", args=[area.pk]),
            {"name": area.name, "slug": area.slug, "price_per_m2": "100", "is_active": "on"},
        )
        self.client.post(
            reverse("admin:quotes_quote_change", args=[quote.pk]),
            {"status": Quote.CONTACTED, "items-TOTAL_FORMS": 0, "items-INITIAL_FORMS": 0},
        )

        area.refresh_from_db()
        quote.refresh_from_db()
        self.assertEqual(area.price_per_m2, 100)
        self.assertEqual(quote.status, Quote.CONTACTED)

    def test_can_edit_single_sections(self):
        self.client.post(
            reverse("admin:site_content_herosection_change", args=[1]),
            {"title": "Nuevo", "primary_cta_text": "a", "secondary_cta_text": "b"},
        )

        self.assertEqual(HeroSection.objects.get().title, "Nuevo")

    def test_can_see_and_add_users(self):
        users = self.client.get(reverse("admin:auth_user_changelist"))
        add_user = self.client.get(reverse("admin:auth_user_add"))

        self.assertEqual(users.status_code, 200)
        self.assertEqual(add_user.status_code, 200)

    def test_cannot_make_itself_superuser(self):
        url = reverse("admin:auth_user_change", args=[self.user.pk])

        page = self.client.get(url)
        self.client.post(
            url,
            {
                "username": self.user.username,
                "is_active": "on",
                "is_staff": "on",
                "is_superuser": "on",
                "groups": [Group.objects.get(name=ADMIN_GROUP).pk],
                "date_joined_0": "2026-01-01",
                "date_joined_1": "00:00:00",
            },
        )

        self.user.refresh_from_db()
        self.assertNotContains(page, 'name="is_superuser"')
        self.assertFalse(self.user.is_superuser)

    def test_cannot_edit_or_delete_the_developer_account(self):
        developer = User.objects.create_superuser("dev", password="clave-de-prueba")

        change = self.client.post(
            reverse("admin:auth_user_change", args=[developer.pk]), {"username": "hackeado"}
        )
        delete = self.client.post(
            reverse("admin:auth_user_delete", args=[developer.pk]), {"post": "yes"}
        )

        developer.refresh_from_db()
        self.assertEqual(change.status_code, 403)
        self.assertEqual(delete.status_code, 403)
        self.assertEqual(developer.username, "dev")
