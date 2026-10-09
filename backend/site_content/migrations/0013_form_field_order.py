"""
Cambia el orden de los campos del formulario (specs-004, RF-40): la casilla
"Tengo fotos del espacio" pasa a ir antes del mensaje, que queda de último.
"""
from django.db import migrations


def move_photos_before_message(apps, schema_editor):
    QuoteFormField = apps.get_model("site_content", "QuoteFormField")
    photos = QuoteFormField.objects.filter(key="has_photos").first()
    message = QuoteFormField.objects.filter(key="message").first()

    # Solo se intercambian si siguen en el orden anterior (mensaje antes que fotos)
    if photos and message and message.order < photos.order:
        photos.order, message.order = message.order, photos.order
        photos.save()
        message.save()


def move_message_before_photos(apps, schema_editor):
    QuoteFormField = apps.get_model("site_content", "QuoteFormField")
    photos = QuoteFormField.objects.filter(key="has_photos").first()
    message = QuoteFormField.objects.filter(key="message").first()

    if photos and message and photos.order < message.order:
        photos.order, message.order = message.order, photos.order
        photos.save()
        message.save()


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0012_form_fields"),
    ]

    operations = [
        migrations.RunPython(move_photos_before_message, move_message_before_photos),
    ]
