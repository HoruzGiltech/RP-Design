"""
Cambios de texto de la Portada que pidió el cliente (specs-001):

- Se elimina el título "Transformamos tus espacios, del plano a la obra.".
- El botón "Agenda una visita" pasa a decir "Agenda una reunión".

Solo se tocan si siguen con el texto original. Si el cliente ya escribió
otro desde el panel, se respeta el suyo.
"""
from django.db import migrations

OLD_TITLE = "Transformamos tus espacios, del plano a la obra."
OLD_BUTTON = "Agenda una visita"
NEW_BUTTON = "Agenda una reunión"


def update_hero_texts(apps, schema_editor):
    HeroSection = apps.get_model("site_content", "HeroSection")
    HeroSection.objects.filter(title=OLD_TITLE).update(title="")
    HeroSection.objects.filter(primary_cta_text=OLD_BUTTON).update(primary_cta_text=NEW_BUTTON)


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0006_whatsapp_floating_button"),
    ]

    operations = [
        # Al deshacer no se restauran los textos viejos: el cliente ya no los quiere
        migrations.RunPython(update_hero_texts, migrations.RunPython.noop),
    ]
