"""
Baja el máximo de m² por defecto de 10000 a 500.

Los metros cuadrados del formulario se eligen ahora con un control deslizante,
y con un tope de 10000 sería imposible atinarle a un valor. El cliente puede
cambiar el tope en "Configuración general".
"""
from decimal import Decimal

from django.db import migrations, models

OLD_DEFAULT = Decimal("10000")
NEW_DEFAULT = Decimal("500")


def lower_default_maximum(apps, schema_editor):
    # Solo se toca si sigue con el valor por defecto anterior:
    # si el cliente ya eligió su propio máximo, se respeta.
    SiteSettings = apps.get_model("site_content", "SiteSettings")
    SiteSettings.objects.filter(max_square_meters=OLD_DEFAULT).update(
        max_square_meters=NEW_DEFAULT
    )


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0002_initial_content"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="max_square_meters",
            field=models.DecimalField(
                decimal_places=2,
                default=500,
                help_text="Tope del control deslizante de metros cuadrados del formulario.",
                max_digits=8,
                verbose_name="máximo de m² en la calculadora",
            ),
        ),
        migrations.RunPython(lower_default_maximum, migrations.RunPython.noop),
    ]
