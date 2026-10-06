"""
Da a los grupos Admin y Viewer los permisos del modelo nuevo de specs-001:
las categorías de proyectos.
"""
from django.db import migrations

from core.roles import assign_group_permissions


def update_groups(apps, schema_editor):
    assign_group_permissions(apps)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_legal_pages_permissions"),
        ("projects", "0004_remove_old_fields"),
        ("site_content", "0007_hero_texts"),
    ]

    operations = [
        # Al deshacer no se quita nada: los permisos de más no hacen daño
        migrations.RunPython(update_groups, migrations.RunPython.noop),
    ]
