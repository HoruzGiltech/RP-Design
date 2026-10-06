"""
Cambia el título de la sección Proyectos del inicio: "Proyectos recientes"
pasa a ser "Mis Proyectos" (pedido del cliente, specs-001).

Solo se toca si sigue con el texto original. Si el cliente ya escribió
otro desde el panel, se respeta el suyo.
"""
from django.db import migrations

OLD_TITLE = "Proyectos recientes"
NEW_TITLE = "Mis Proyectos"


def update_title(apps, schema_editor):
    ProjectsSection = apps.get_model("site_content", "ProjectsSection")
    ProjectsSection.objects.filter(title=OLD_TITLE).update(title=NEW_TITLE)


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0007_hero_texts"),
    ]

    operations = [
        # Al deshacer no se restaura el texto viejo: el cliente ya no lo quiere
        migrations.RunPython(update_title, migrations.RunPython.noop),
    ]
