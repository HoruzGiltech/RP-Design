"""
Crea los grupos Admin y Viewer con sus permisos.

Al estar en una migración, los grupos existen siempre después de `migrate`,
sin tener que configurarlos a mano en cada entorno.

OJO: si más adelante se agrega un modelo nuevo, hay que escribir otra migración
que vuelva a repartir los permisos (ver 0002_legal_pages_permissions).
"""
from django.db import migrations

from core.roles import ADMIN_GROUP, VIEWER_GROUP, assign_group_permissions


def create_groups(apps, schema_editor):
    assign_group_permissions(apps)


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
