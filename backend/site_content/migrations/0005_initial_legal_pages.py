"""
Crea las dos páginas legales con su estructura: títulos y apartados.

Los textos NO se inventan: quedan como [TEXTO PENDIENTE] para que los escriba
el cliente o su abogado desde el panel. Los subtítulos son solo una guía de
los temas que suele cubrir cada página; se pueden cambiar, quitar o reordenar.
"""
from django.db import migrations

PENDING = "[TEXTO PENDIENTE]"

LEGAL_PAGES = [
    {
        "slug": "terminos",
        "title": "Términos y condiciones",
        "sections": [
            "Uso del sitio",
            "Cotizaciones y precios",
            "Propiedad intelectual",
            "Cambios en estos términos",
            "Contacto",
        ],
    },
    {
        "slug": "privacidad",
        "title": "Política de privacidad",
        "sections": [
            "Datos que recogemos",
            "Para qué usamos tus datos",
            "Con quién los compartimos",
            "Cookies",
            "Tus derechos",
            "Contacto",
        ],
    },
]


def create_legal_pages(apps, schema_editor):
    LegalPage = apps.get_model("site_content", "LegalPage")
    LegalSection = apps.get_model("site_content", "LegalSection")

    for page_data in LEGAL_PAGES:
        page, created = LegalPage.objects.get_or_create(
            slug=page_data["slug"], defaults={"title": page_data["title"], "intro": PENDING}
        )
        # Si la página ya existía, no se le agregan apartados otra vez
        if not created:
            continue
        for position, title in enumerate(page_data["sections"], start=1):
            LegalSection.objects.create(page=page, title=title, body=PENDING, order=position)


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0004_legal_pages"),
    ]

    operations = [
        # Al deshacer la migración no se borra nada: el cliente pudo editar los textos
        migrations.RunPython(create_legal_pages, migrations.RunPython.noop),
    ]
