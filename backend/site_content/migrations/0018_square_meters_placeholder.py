"""
Texto de ejemplo del campo "Metros cuadrados" del formulario: "10 m²".
Solo se pone si el campo no tiene ninguno; si el cliente ya escribió uno, se respeta.
"""
from django.db import migrations

NEW_PLACEHOLDER = "10 m²"


def set_placeholder(apps, schema_editor):
    QuoteFormField = apps.get_model("site_content", "QuoteFormField")
    QuoteFormField.objects.filter(key="square_meters", placeholder="").update(
        placeholder=NEW_PLACEHOLDER
    )


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0017_form_fields_specs_008"),
    ]

    operations = [
        migrations.RunPython(set_placeholder, migrations.RunPython.noop),
    ]
