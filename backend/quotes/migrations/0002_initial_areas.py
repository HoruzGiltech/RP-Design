from django.db import migrations

# (nombre, identificador, ¿es la opción "Otro"?)
# Se crean sin precio: los pone el cliente en el panel.
INITIAL_AREAS = [
    ("Baño", "bano", False),
    ("Cocina", "cocina", False),
    ("Sala", "sala", False),
    ("Patio", "patio", False),
    ("Piscina", "piscina", False),
    ("Otro", "otro", True),
]


def create_areas(apps, schema_editor):
    # En una migración se usa apps.get_model en vez de importar el modelo,
    # para trabajar con la versión del modelo de ese momento.
    RemodelArea = apps.get_model("quotes", "RemodelArea")
    for position, (name, slug, is_other) in enumerate(INITIAL_AREAS, start=1):
        RemodelArea.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "is_other": is_other, "order": position},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("quotes", "0001_initial"),
    ]

    operations = [
        # Al deshacer la migración no se borra nada: las áreas pueden tener cotizaciones
        migrations.RunPython(create_areas, migrations.RunPython.noop),
    ]
