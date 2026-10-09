"""
Da a los grupos Admin y Viewer los permisos de los modelos nuevos de specs-003:
los renglones de una cotización y los campos del formulario.
"""
from django.db import migrations

from core.roles import assign_group_permissions


def update_groups(apps, schema_editor):
    assign_group_permissions(apps)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_category_permissions"),
        ("projects", "0005_category_is_visible"),
        ("quotes", "0008_remove_single_area_fields"),
        ("site_content", "0012_form_fields"),
    ]

    operations = [
        # Al deshacer no se quita nada: los permisos de más no hacen daño
        migrations.RunPython(update_groups, migrations.RunPython.noop),
    ]
