"""
Reparte las áreas a remodelar por tipo de remodelación (specs-002, RF-17).

- Las áreas que ya existían (Baño, Cocina, Sala, Patio, Piscina...) pasan a
  la categoría Residencial.
- "Otro" se queda sin categoría: así aparece en todos los tipos.
- Se crean las áreas de ejemplo que dio el cliente para Corporativo y
  Comercial, sin precio.

Si una categoría ya no existe (el cliente la borró), se salta lo suyo.
"""
from django.db import migrations

RESIDENTIAL_SLUG = "residencial"

# categoría -> [(nombre, identificador)]
NEW_AREAS = {
    "corporativo": [("Oficina", "oficina"), ("Sala de reuniones", "sala-de-reuniones")],
    "comercial": [("Showroom", "showroom")],
}


def assign_categories(apps, schema_editor):
    ProjectCategory = apps.get_model("projects", "ProjectCategory")
    RemodelArea = apps.get_model("quotes", "RemodelArea")

    residential = ProjectCategory.objects.filter(slug=RESIDENTIAL_SLUG).first()
    if residential:
        # Solo las que no son "Otro" y todavía no tienen categoría
        RemodelArea.objects.filter(category__isnull=True, is_other=False).update(
            category=residential
        )

    # Las nuevas van al final de la lista
    last_area = RemodelArea.objects.order_by("-order").first()
    next_order = (last_area.order if last_area else 0) + 1

    for category_slug, areas in NEW_AREAS.items():
        category = ProjectCategory.objects.filter(slug=category_slug).first()
        if category is None:
            continue
        for name, slug in areas:
            _area, created = RemodelArea.objects.get_or_create(
                slug=slug, defaults={"name": name, "category": category, "order": next_order}
            )
            if created:
                next_order += 1


class Migration(migrations.Migration):

    dependencies = [
        ("quotes", "0004_area_category"),
        # Las categorías las crea esta migración de projects
        ("projects", "0003_migrate_categories"),
    ]

    operations = [
        # Al deshacer no se borra nada: el cliente pudo editar las áreas
        migrations.RunPython(assign_categories, migrations.RunPython.noop),
    ]
