"""
Crea los grupos Admin y Viewer con sus permisos.

Al estar en una migración, los grupos existen siempre después de `migrate`,
sin tener que configurarlos a mano en cada entorno.

OJO: si más adelante se agrega un modelo nuevo, hay que escribir otra migración
como esta para darle sus permisos a los grupos.
"""
from django.contrib.auth.management import create_permissions
from django.db import migrations

from core.roles import ADMIN_GROUP, CONTENT_APPS, USER_MODELS, VIEWER_GROUP


def ensure_permissions_exist(apps):
    """
    Django crea los permisos al terminar TODAS las migraciones.
    Esta migración los necesita antes, así que se le pide crearlos ya.
    """
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def create_groups(apps, schema_editor):
    ensure_permissions_exist(apps)

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    content_permissions = Permission.objects.filter(content_type__app_label__in=CONTENT_APPS)
    user_permissions = Permission.objects.filter(
        content_type__app_label="auth", content_type__model__in=USER_MODELS
    )

    admin_group, _created = Group.objects.get_or_create(name=ADMIN_GROUP)
    admin_group.permissions.set(list(content_permissions) + list(user_permissions))

    viewer_group, _created = Group.objects.get_or_create(name=VIEWER_GROUP)
    viewer_group.permissions.set(content_permissions.filter(codename__startswith="view_"))


def delete_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=[ADMIN_GROUP, VIEWER_GROUP]).delete()


class Migration(migrations.Migration):

    # Tiene que ejecutarse después de crear todas las tablas de contenido
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("projects", "0001_initial"),
        ("quotes", "0002_initial_areas"),
        ("site_content", "0002_initial_content"),
    ]

    operations = [
        migrations.RunPython(create_groups, delete_groups),
    ]
