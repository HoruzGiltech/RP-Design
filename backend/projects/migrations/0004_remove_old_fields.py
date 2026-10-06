"""
Paso 3 de 3 del cambio a categorías (specs-001): limpia lo antiguo.

Con los datos ya copiados, se borran el campo de texto de categoría y los
"destacados", y la categoría nueva toma el nombre definitivo. La dirección
web del proyecto deja de editarse a mano.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0003_migrate_categories"),
    ]

    operations = [
        migrations.RemoveField(model_name="project", name="category"),
        migrations.RemoveField(model_name="project", name="is_featured"),
        migrations.RemoveField(model_name="project", name="featured_order"),
        migrations.RenameField(model_name="project", old_name="category_fk", new_name="category"),
        migrations.AlterField(
            model_name="project",
            name="slug",
            field=models.SlugField(
                editable=False, max_length=170, unique=True, verbose_name="dirección web"
            ),
        ),
    ]
