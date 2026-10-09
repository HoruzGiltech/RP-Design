"""
Crea las filas de "Campos del formulario" con los textos que el formulario
ya tenía escritos en el código. Desde aquí se editan en el panel.
"""
from django.db import migrations

# (campo, título, texto de ejemplo), en el orden en que aparecen en el formulario
FORM_FIELDS = [
    ("name", "Nombre", "Tu nombre"),
    ("phone", "Teléfono", "0412 000 0000"),
    ("email", "Correo", "nombre@correo.com"),
    ("category", "Tipo de remodelación", "Elige una opción"),
    ("location", "Ubicación del espacio", ""),
    ("areas", "Áreas a remodelar", ""),
    ("area_other", "Especifica el área", "Ejemplo: terraza"),
    ("square_meters", "Metros cuadrados", ""),
    ("needs_visit", "No sé cuántos m² son, agendar una visita", ""),
    ("message", "Mensaje (opcional)", "Cuéntanos qué quieres transformar"),
    ("has_photos", "Tengo fotos del espacio", ""),
]


def create_form_fields(apps, schema_editor):
    ContactSection = apps.get_model("site_content", "ContactSection")
    QuoteFormField = apps.get_model("site_content", "QuoteFormField")

    # Las filas cuelgan de la sección Contacto, que es un registro único
    section, _ = ContactSection.objects.get_or_create(pk=1)
    for order, (key, label, placeholder) in enumerate(FORM_FIELDS):
        QuoteFormField.objects.get_or_create(
            key=key,
            defaults={
                "section": section,
                "label": label,
                "placeholder": placeholder,
                "order": order,
            },
        )


def delete_form_fields(apps, schema_editor):
    apps.get_model("site_content", "QuoteFormField").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0011_specs_003"),
    ]

    operations = [
        migrations.RunPython(create_form_fields, delete_form_fields),
    ]
