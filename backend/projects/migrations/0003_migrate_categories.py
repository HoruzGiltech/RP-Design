"""
Paso 2 de 3 del cambio a categorías (specs-001): copia los datos.

- Crea las tres categorías que pidió el cliente.
- Asocia cada proyecto a la categoría que mencionaba su texto antiguo:
  "Fachada · Residencial" -> Residencial. Si no menciona ninguna, queda sin
  categoría y el panel la pedirá al editarlo.
- Los proyectos que eran "destacados" pasan a mostrarse en el hero, con su
  mismo orden: así no se pierde lo que el cliente ya había elegido.
"""
from django.db import migrations

from projects.services import match_category_name

# (nombre, dirección web)
INITIAL_CATEGORIES = [
    ("Comercial", "comercial"),
    ("Residencial", "residencial"),
    ("Corporativo", "corporativo"),
]


def migrate_categories(apps, schema_editor):
    ProjectCategory = apps.get_model("projects", "ProjectCategory")
    Project = apps.get_model("projects", "Project")

    categories = {}
    for position, (name, slug) in enumerate(INITIAL_CATEGORIES, start=1):
        category, _created = ProjectCategory.objects.get_or_create(
            slug=slug, defaults={"name": name, "order": position}
        )
        categories[name] = category

    for project in Project.objects.all():
        matched_name = match_category_name(project.category, categories.keys())
        project.category_fk = categories.get(matched_name)
        project.show_in_hero = project.is_featured
        project.hero_order = project.featured_order
        project.save(update_fields=["category_fk", "show_in_hero", "hero_order"])


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_categories"),
    ]

    operations = [
        # Al deshacer no se borra nada: los campos antiguos siguen ahí con sus datos
        migrations.RunPython(migrate_categories, migrations.RunPython.noop),
    ]
