"""
Da a los grupos Admin y Viewer los permisos de los modelos nuevos
(páginas legales y sus apartados).

Los grupos no se enteran solos de que existe un modelo nuevo: hay que
volver a repartir los permisos con una migración como esta.
"""
from django.db import migrations

from core.roles import assign_group_permissions


def update_groups(apps, schema_editor):
    assign_group_permissions(apps)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_create_groups"),
        ("site_content", "0005_initial_legal_pages"),
        ("quotes", "0003_privacy_accepted_at"),
    ]

    operations = [
        # Al deshacer no se quita nada: los permisos de más no hacen daño
        migrations.RunPython(update_groups, migrations.RunPython.noop),
    ]
