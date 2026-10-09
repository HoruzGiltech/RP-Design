"""
Convierte cada cotización existente en una cotización de un solo renglón.

Hasta specs-002 una cotización tenía una sola área, guardada en la propia
cotización. Desde specs-003 las áreas van en renglones (QuoteItem). Aquí se
copia el área de cada cotización a su primer renglón, antes de que la
migración siguiente borre los campos antiguos.
"""
from django.db import migrations


def copy_area_to_item(apps, schema_editor):
    Quote = apps.get_model("quotes", "Quote")
    QuoteItem = apps.get_model("quotes", "QuoteItem")

    for quote in Quote.objects.all():
        # Si la migración se ejecuta dos veces, no se duplica el renglón
        if QuoteItem.objects.filter(quote=quote).exists():
            continue
        QuoteItem.objects.create(
            quote=quote,
            area_id=quote.area_id,
            area_other=quote.area_other,
            square_meters=quote.square_meters,
            price_per_m2_snapshot=quote.price_per_m2_snapshot,
            # Con una sola área, el subtotal era el estimado completo
            subtotal=quote.estimated_price,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("quotes", "0006_quote_items"),
    ]

    operations = [
        # Al deshacer no se borra nada: los campos antiguos siguen con sus datos
        migrations.RunPython(copy_area_to_item, migrations.RunPython.noop),
    ]
