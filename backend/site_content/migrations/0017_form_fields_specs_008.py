"""
Textos del formulario tras specs-008:

- La fila "category" pasa a llamarse "remodel_type": el tipo de remodelación
  ya no es una lista, es un texto libre. Su texto de ejemplo cambia solo si
  sigue siendo el original.
- Se borran las filas de las áreas, que el formulario ya no tiene.
- Se reordenan como aparecen ahora en el formulario.
"""
from django.db import migrations

OLD_PLACEHOLDER = "Elige una opción"
NEW_PLACEHOLDER = "cocina, patio, baño, casa, quinta, etc."

REMOVED_KEYS = ["areas", "area_other"]

# El orden de los campos en el formulario
FIELD_ORDER = [
    "name",
    "phone",
    "email",
    "remodel_type",
    "location",
    "square_meters",
    "needs_visit",
    "has_photos",
    "message",
]


def update_form_fields(apps, schema_editor):
    QuoteFormField = apps.get_model("site_content", "QuoteFormField")

    QuoteFormField.objects.filter(key="category").update(key="remodel_type")
    QuoteFormField.objects.filter(key="remodel_type", placeholder=OLD_PLACEHOLDER).update(
        placeholder=NEW_PLACEHOLDER
    )
    QuoteFormField.objects.filter(key__in=REMOVED_KEYS).delete()

    for order, key in enumerate(FIELD_ORDER):
        QuoteFormField.objects.filter(key=key).update(order=order)


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0016_form_field_keys"),
    ]

    operations = [
        # Al deshacer no se recrean las filas de las áreas: el formulario ya no las usa
        migrations.RunPython(update_form_fields, migrations.RunPython.noop),
    ]
