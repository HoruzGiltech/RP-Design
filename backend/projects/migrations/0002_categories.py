"""
Paso 1 de 3 del cambio a categorías (specs-001).

Crea la lista de categorías y agrega los campos nuevos del proyecto.
La categoría nueva se llama por ahora "category_fk": el campo de texto
antiguo sigue existiendo hasta que el paso 2 copie sus datos.
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "order",
                    models.PositiveIntegerField(db_index=True, default=0, verbose_name="orden"),
                ),
                ("name", models.CharField(max_length=60, unique=True, verbose_name="nombre")),
                (
                    "slug",
                    models.SlugField(
                        editable=False, max_length=70, unique=True, verbose_name="dirección web"
                    ),
                ),
            ],
            options={
                "verbose_name": "categoría",
                "verbose_name_plural": "categorías",
                "ordering": ["order"],
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="project",
            name="category_fk",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="projects",
                to="projects.projectcategory",
                verbose_name="categoría",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="show_in_hero",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "La portada aparece en la parte superior del inicio. "
                    "Con más de una, van rotando. Máximo 6."
                ),
                verbose_name="mostrar en el hero",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="hero_order",
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text="El número menor va primero.",
                verbose_name="orden en el hero",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="is_category_cover",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Su portada representa a la categoría en el inicio. Solo una por categoría: "
                    "al marcar esta, se desmarca la anterior."
                ),
                verbose_name="usar como portada de su categoría",
            ),
        ),
    ]
