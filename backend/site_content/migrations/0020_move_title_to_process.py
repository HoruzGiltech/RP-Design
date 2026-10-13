"""
El título "Un solo equipo para todo tu proyecto" y su introducción pasan de
la sección Servicios a la sección Proceso, que es la que ahora muestra las
tarjetas numeradas debajo de ese título (specs-008, RF-58).

La sección Servicios queda con el título "Servicios" y sin introducción.

Solo se hace si Servicios sigue con el título original. Si el cliente ya lo
cambió desde el panel, no se toca nada.
"""
from django.db import migrations

ORIGINAL_SERVICES_TITLE = "Un solo equipo para todo tu proyecto"
NEW_SERVICES_TITLE = "Servicios"


def move_title(apps, schema_editor):
    ServicesSection = apps.get_model("site_content", "ServicesSection")
    ProcessSection = apps.get_model("site_content", "ProcessSection")

    services = ServicesSection.objects.filter(title=ORIGINAL_SERVICES_TITLE).first()
    process = ProcessSection.objects.first()
    if services is None or process is None:
        return

    process.title = services.title
    process.intro = services.intro
    process.save()

    services.title = NEW_SERVICES_TITLE
    services.intro = ""
    services.save()


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0019_process_show_video"),
    ]

    operations = [
        # Al deshacer no se devuelven los títulos: el cliente ya no los quiere así
        migrations.RunPython(move_title, migrations.RunPython.noop),
    ]
