"""
Cambia un texto de la franja de especialidades: "Renders 3D" pasa a ser
"Corporativo" (pedido del cliente, specs-001, P-9).

Solo se toca si sigue con el texto original. Si el cliente ya escribió
otro desde el panel, se respeta el suyo. El paso "Renders 3D" de la
sección Proceso no cambia: es otro modelo.
"""
from django.db import migrations

OLD_TEXT = "Renders 3D"
NEW_TEXT = "Corporativo"


def update_specialty(apps, schema_editor):
    Specialty = apps.get_model("site_content", "Specialty")
    Specialty.objects.filter(text=OLD_TEXT).update(text=NEW_TEXT)


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0008_projects_section_title"),
    ]

    operations = [
        # Al deshacer no se restaura el texto viejo: el cliente ya no lo quiere
        migrations.RunPython(update_specialty, migrations.RunPython.noop),
    ]
