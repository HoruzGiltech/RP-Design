"""
Carga los textos de la maqueta (docs/maqueta-legible.html) como contenido inicial.

Así el sitio se ve igual que la maqueta desde el primer arranque, y el cliente
solo tiene que subir sus fotos. Después todo se edita desde el panel.
"""
from django.db import migrations

# Secciones únicas: nombre del modelo -> valores iniciales.
# SiteSettings no lleva valores porque usa los que ya tiene por defecto el modelo.
SINGLETONS = {
    "SiteSettings": {},
    "HeroSection": {
        "eyebrow": "ESTUDIO DE DISEÑO DE INTERIORES · CARACAS",
        "title": "Transformamos tus espacios, del plano a la obra.",
        "body": (
            "Diseño residencial y comercial con renders 3D, video recorridos y "
            "planimetría. Y cuando el diseño está listo, también lo construimos."
        ),
        "primary_cta_text": "Agenda una visita",
        "secondary_cta_text": "Ver proyectos",
    },
    "ServicesSection": {
        "title": "Un solo equipo para todo tu proyecto",
        "intro": (
            "Te acompañamos desde la medición del espacio hasta la entrega final, "
            "sin tener que coordinar a varios proveedores."
        ),
    },
    "ProjectsSection": {
        "title": "Proyectos recientes",
        "instagram_link_text": "Ver más en Instagram",
        "view_all_text": "Ver todos los proyectos",
    },
    "ProcessSection": {
        "title": "Ve tu espacio antes de construirlo",
        "intro": (
            "Cada proyecto incluye entregables visuales y técnicos para decidir "
            "con seguridad."
        ),
    },
    "ContactSection": {
        "title": "Cuéntanos sobre tu espacio",
        "intro": "Te respondemos con los próximos pasos y una propuesta a la medida.",
        "submit_text": "Enviar por WhatsApp",
    },
    "FooterSection": {
        "name": "RP DISEÑO INTERIOR",
        "tagline": "Arquitectura · Interiorismo · Remodelaciones — Caracas",
    },
    # La maqueta no trae descripción para buscadores: queda vacía hasta que el cliente la escriba
    "SeoSettings": {"site_title": "RP Diseño Interior"},
}

SPECIALTIES = [
    "Diseño residencial",
    "Diseño comercial",
    "Renders 3D",
    "Ejecución de obra",
]

SERVICES = [
    (
        "Levantamiento de espacio",
        "Medimos y documentamos tu espacio actual para diseñar sobre información real.",
    ),
    (
        "Proyecto de diseño",
        "Renders 3D, video recorridos y planimetría para que veas el resultado "
        "antes de construir.",
    ),
    (
        "Ejecución de obra",
        "Construimos lo diseñado, con criterio técnico desde las fundaciones "
        "hasta los acabados.",
    ),
]

PROCESS_STEPS = [
    ("Renders 3D", "Imágenes realistas de materiales, luz y mobiliario."),
    ("Video recorridos", "Recorre tu espacio terminado como si ya existiera."),
    ("Planimetría", "Planos claros para ejecutar la obra sin improvisaciones."),
    ("Ejecución de obra", "Un mismo equipo responsable del diseño y la construcción."),
]


def load_content(apps, schema_editor):
    for model_name, values in SINGLETONS.items():
        model = apps.get_model("site_content", model_name)
        model.objects.get_or_create(pk=1, defaults=values)

    Specialty = apps.get_model("site_content", "Specialty")
    Service = apps.get_model("site_content", "Service")
    ProcessStep = apps.get_model("site_content", "ProcessStep")

    # Las listas solo se cargan si están vacías, para no duplicar nada
    if not Specialty.objects.exists():
        for position, text in enumerate(SPECIALTIES, start=1):
            Specialty.objects.create(text=text, order=position)

    if not Service.objects.exists():
        for position, (title, description) in enumerate(SERVICES, start=1):
            Service.objects.create(title=title, description=description, order=position)

    if not ProcessStep.objects.exists():
        for position, (title, description) in enumerate(PROCESS_STEPS, start=1):
            ProcessStep.objects.create(title=title, description=description, order=position)


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0001_initial"),
    ]

    operations = [
        # Al deshacer la migración no se borra nada: el cliente pudo editar el contenido
        migrations.RunPython(load_content, migrations.RunPython.noop),
    ]
