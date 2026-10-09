"""
El botón de la sección Proyectos del inicio pasa a decir "Ver proyectos"
(specs-004, RF-34).

Solo se cambia si sigue con el texto original. Si el cliente ya escribió
otro desde el panel, se respeta el suyo.
"""
from django.db import migrations

OLD_TEXT = "Ver todos los proyectos"
NEW_TEXT = "Ver proyectos"


def update_button_text(apps, schema_editor):
    ProjectsSection = apps.get_model("site_content", "ProjectsSection")
    ProjectsSection.objects.filter(view_all_text=OLD_TEXT).update(view_all_text=NEW_TEXT)


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0014_service_image"),
    ]

    operations = [
        # Al deshacer no se restaura el texto viejo: el cliente ya no lo quiere
        migrations.RunPython(update_button_text, migrations.RunPython.noop),
    ]
