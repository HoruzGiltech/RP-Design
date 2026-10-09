"""
Contenido editable del sitio.

Cada modelo corresponde a una sección de la maqueta (ver specs/requirements.md §3).
Los textos iniciales los carga la migración 0002_initial_content.
"""
from django.core.validators import RegexValidator
from django.db import models

from core.images import optimize_image_field
from core.models import OrderedModel, SingletonModel, VisibleModel
from core.uploads import build_unique_path
from core.validators import validate_font_file, validate_image_file, validate_video_file

# Las secciones únicas (SingletonModel) siempre usan este id
SINGLETON_PK = 1

DEFAULT_PRICE_NOTE = (
    "Precio referencial en USD, sujeto a modificación tras visita técnica. "
    "También puede pagarse en bolívares a tasa BCV del día."
)

DEFAULT_WHATSAPP_GREETING = "Hola! quiero agendar una reunión"

FONT_HELP_TEXT = (
    "Opcional. Formatos: woff2, woff, ttf u otf. Lo ideal es una fuente variable "
    "(un solo archivo con todos los grosores): con un archivo de un solo grosor, las "
    "negritas se ven peor. Debes tener licencia para usarla en la web. "
    "Vacío = fuente original del sitio."
)

whatsapp_number_validator = RegexValidator(
    regex=r"^\d{10,15}$",
    message="Escribe el número en formato internacional, solo dígitos. Ejemplo: 584127305964",
)


def site_upload_path(instance, filename):
    """Los archivos del contenido del sitio van a 'site/<año>/<uuid>.<ext>'."""
    return build_unique_path("site", filename)


def site_image_field(verbose_name, **options):
    """Campo de imagen opcional con las validaciones de siempre."""
    return models.ImageField(
        verbose_name,
        upload_to=site_upload_path,
        blank=True,
        validators=[validate_image_file],
        **options,
    )


def site_video_field(verbose_name, **options):
    """Campo de video opcional con las validaciones de siempre."""
    return models.FileField(
        verbose_name,
        upload_to=site_upload_path,
        blank=True,
        validators=[validate_video_file],
        **options,
    )


# ---------------------------------------------------------------------------
# Configuración general
# ---------------------------------------------------------------------------


class SiteSettings(SingletonModel):
    """Marca, datos de contacto y configuración general (encabezado, contacto y pie)."""

    ACCENT_COLOR_CHOICES = [
        ("#111111", "Negro"),
        ("#8A5A3B", "Terracota"),
        ("#3E4A3D", "Verde oliva"),
        ("#5B6670", "Pizarra"),
    ]

    brand_initials = models.CharField(
        "iniciales",
        max_length=4,
        default="RP",
        help_text="Se muestran dentro del círculo cuando no hay logo.",
    )
    brand_name = models.CharField("nombre de la marca", max_length=60, default="RP DISEÑO")
    brand_subtitle = models.CharField(
        "subtítulo de la marca", max_length=80, default="INTERIOR · ARQUITECTURA"
    )
    logo = site_image_field("logo", help_text="Opcional. Reemplaza al círculo con iniciales.")
    header_cta_text = models.CharField(
        "texto del botón del encabezado", max_length=40, default="Cotiza tu proyecto"
    )
    accent_color = models.CharField(
        "color de acento",
        max_length=7,
        choices=ACCENT_COLOR_CHOICES,
        default="#111111",
        help_text="Color de los botones principales y de los números de Servicios.",
    )

    whatsapp_number = models.CharField(
        "número de WhatsApp",
        max_length=15,
        default="584127305964",
        validators=[whatsapp_number_validator],
        help_text=(
            "A este número llegan las cotizaciones. Solo dígitos, con código de país. "
            "En el sitio se muestra en formato internacional: +58 412 730 5964."
        ),
    )
    contact_email = models.EmailField("correo de contacto", default="rpdesings05@gmail.com")
    instagram_handle = models.CharField(
        "usuario de Instagram", max_length=60, default="rpdesign_ve", help_text="Sin la @."
    )
    city = models.CharField("ciudad", max_length=80, default="Caracas, Venezuela")

    # Tipografía (specs-003). Vacías, el sitio usa sus fuentes originales.
    heading_font = models.FileField(
        "fuente de títulos",
        upload_to=site_upload_path,
        blank=True,
        validators=[validate_font_file],
        help_text=FONT_HELP_TEXT,
    )
    body_font = models.FileField(
        "fuente de texto",
        upload_to=site_upload_path,
        blank=True,
        validators=[validate_font_file],
        help_text=FONT_HELP_TEXT,
    )

    show_estimate = models.BooleanField(
        "mostrar el estimado de precio",
        default=True,
        help_text=(
            "Si se desmarca, el visitante no ve ningún precio en el formulario ni en el "
            "mensaje de WhatsApp. El estimado se sigue guardando en cada cotización del panel."
        ),
    )
    price_note = models.TextField(
        "nota de precio",
        default=DEFAULT_PRICE_NOTE,
        help_text="Se muestra debajo del estimado de la calculadora.",
    )
    show_whatsapp_button = models.BooleanField(
        "mostrar el botón flotante de WhatsApp",
        default=True,
        help_text="Botón fijo en la esquina inferior derecha de todas las páginas.",
    )
    whatsapp_greeting = models.CharField(
        "mensaje del botón flotante",
        max_length=200,
        default=DEFAULT_WHATSAPP_GREETING,
        help_text="Texto que ya viene escrito cuando alguien pulsa el botón.",
    )

    max_square_meters = models.DecimalField(
        "máximo de m² en la calculadora",
        max_digits=8,
        decimal_places=2,
        default=500,
        help_text="Tope del control deslizante de metros cuadrados del formulario.",
    )

    class Meta:
        verbose_name = "configuración general"
        verbose_name_plural = "configuración general"

    def __str__(self):
        return "Configuración general"

    def save(self, *args, **kwargs):
        optimize_image_field(self, "logo")
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Secciones únicas (un solo registro cada una)
# ---------------------------------------------------------------------------


class HeroSection(SingletonModel, VisibleModel):
    eyebrow = models.CharField("antetítulo", max_length=120, blank=True)
    title = models.CharField(
        "título",
        max_length=160,
        blank=True,
        help_text="Opcional. Si se deja vacío, el hero no muestra título.",
    )
    body = models.TextField("párrafo", blank=True)
    primary_cta_text = models.CharField("texto del botón principal", max_length=40)
    show_primary_cta = models.BooleanField("mostrar el botón principal", default=True)
    secondary_cta_text = models.CharField("texto del botón secundario", max_length=40)
    show_secondary_cta = models.BooleanField("mostrar el botón secundario", default=True)
    image = site_image_field(
        "imagen de respaldo",
        help_text=(
            "Solo se usa si ningún proyecto tiene marcado \"Mostrar en el hero\". "
            "Lo normal es que el hero muestre las portadas de los proyectos."
        ),
    )
    image_alt = models.CharField("texto alternativo de la imagen", max_length=150, blank=True)
    video = site_video_field(
        "video de respaldo",
        help_text=(
            "Opcional, y también solo como respaldo. Se reproduce en bucle y sin sonido "
            "en lugar de la imagen. Súbelo corto y ya comprimido."
        ),
    )

    class Meta:
        verbose_name = "portada"
        verbose_name_plural = "portada"

    def __str__(self):
        return "Portada"

    def save(self, *args, **kwargs):
        optimize_image_field(self, "image")
        super().save(*args, **kwargs)


class ServicesSection(SingletonModel, VisibleModel):
    title = models.CharField("título", max_length=160)
    intro = models.TextField("introducción", blank=True)
    cta_text = models.CharField(
        "texto del botón de cada servicio",
        max_length=40,
        default="Cotizar",
        help_text="Botón que aparece en cada tarjeta y lleva al formulario de contacto.",
    )

    class Meta:
        verbose_name = "servicios (encabezado)"
        verbose_name_plural = "servicios (encabezado)"

    def __str__(self):
        return "Servicios (encabezado)"


class ProjectsSection(SingletonModel, VisibleModel):
    title = models.CharField("título", max_length=160)
    instagram_link_text = models.CharField("texto del enlace a Instagram", max_length=60)
    view_all_text = models.CharField('texto del botón "Ver todos"', max_length=60)

    class Meta:
        verbose_name = "proyectos (encabezado)"
        verbose_name_plural = "proyectos (encabezado)"

    def __str__(self):
        return "Proyectos (encabezado)"


class ProcessSection(SingletonModel, VisibleModel):
    title = models.CharField("título", max_length=160)
    intro = models.TextField("introducción", blank=True)
    video = site_video_field("video recorrido")
    video_poster = site_image_field(
        "vista previa del video", help_text="Imagen que se ve antes de reproducir."
    )

    class Meta:
        verbose_name = "proceso (encabezado)"
        verbose_name_plural = "proceso (encabezado)"

    def __str__(self):
        return "Proceso (encabezado)"

    def save(self, *args, **kwargs):
        optimize_image_field(self, "video_poster")
        super().save(*args, **kwargs)


class ContactSection(SingletonModel, VisibleModel):
    title = models.CharField("título", max_length=160)
    intro = models.TextField("introducción", blank=True)
    submit_text = models.CharField("texto del botón de envío", max_length=40)

    class Meta:
        verbose_name = "contacto"
        verbose_name_plural = "contacto"

    def __str__(self):
        return "Contacto"


class FooterSection(SingletonModel, VisibleModel):
    name = models.CharField("nombre", max_length=80)
    tagline = models.CharField("lema", max_length=160, blank=True)

    class Meta:
        verbose_name = "pie de página"
        verbose_name_plural = "pie de página"

    def __str__(self):
        return "Pie de página"


class SeoSettings(SingletonModel):
    """Lo que ven Google y las redes sociales. No es una sección visible del sitio."""

    site_title = models.CharField("título del sitio", max_length=70)
    meta_description = models.CharField(
        "descripción",
        max_length=160,
        blank=True,
        help_text="Texto que aparece debajo del título en Google. Máximo 160 caracteres.",
    )
    share_image = site_image_field(
        "imagen para compartir",
        help_text="Se ve al compartir el sitio en WhatsApp o redes. Ideal: 1200 × 630 px.",
    )

    class Meta:
        verbose_name = "SEO"
        verbose_name_plural = "SEO"

    def __str__(self):
        return "SEO"

    def save(self, *args, **kwargs):
        optimize_image_field(self, "share_image")
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Listas (el cliente agrega, edita, ordena y oculta elementos)
# ---------------------------------------------------------------------------


class Specialty(OrderedModel, VisibleModel):
    """
    Elemento de la antigua franja de especialidades.
    Desde specs-002 el sitio no la muestra; el modelo se conserva en el panel.
    """

    text = models.CharField("texto", max_length=60)

    class Meta(OrderedModel.Meta):
        verbose_name = "especialidad"
        # El cintillo se quitó del sitio (specs-002). La lista se conserva por si se recupera.
        verbose_name_plural = "especialidades (ya no se muestran en el sitio)"

    def __str__(self):
        return self.text


class Service(OrderedModel, VisibleModel):
    """Tarjeta de Servicios. Su número (01, 02...) lo calcula el sitio según el orden."""

    # La sección es un registro único (pk=1). Esta relación existe para poder editar
    # los servicios dentro del formulario de "Servicios (encabezado)" en el panel.
    section = models.ForeignKey(
        ServicesSection,
        on_delete=models.CASCADE,
        related_name="items",
        default=SINGLETON_PK,
        editable=False,
    )
    title = models.CharField("título", max_length=80)
    description = models.TextField("descripción")

    class Meta(OrderedModel.Meta):
        verbose_name = "servicio"
        verbose_name_plural = "servicios"

    def __str__(self):
        return self.title


class ProcessStep(OrderedModel, VisibleModel):
    """Entregable de Proceso. Su letra (A, B...) la calcula el sitio según el orden."""

    # Igual que en Service: permite editar los pasos dentro de "Proceso (encabezado)"
    section = models.ForeignKey(
        ProcessSection,
        on_delete=models.CASCADE,
        related_name="steps",
        default=SINGLETON_PK,
        editable=False,
    )
    title = models.CharField("título", max_length=80)
    description = models.TextField("descripción")

    class Meta(OrderedModel.Meta):
        verbose_name = "paso del proceso"
        verbose_name_plural = "pasos del proceso"

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------
# Páginas legales (Términos y Privacidad)
# ---------------------------------------------------------------------------


class LegalPage(models.Model):
    """
    Página legal del sitio. Son siempre dos y las crea una migración:
    el cliente edita su contenido, pero no puede agregar ni borrar páginas.
    """

    TERMS = "terminos"
    PRIVACY = "privacidad"
    SLUG_CHOICES = [(TERMS, "Términos y condiciones"), (PRIVACY, "Política de privacidad")]

    slug = models.SlugField("dirección web", unique=True, choices=SLUG_CHOICES, editable=False)
    title = models.CharField("título", max_length=120)
    intro = models.TextField("introducción", blank=True)
    updated_at = models.DateTimeField("última actualización", auto_now=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "página legal"
        verbose_name_plural = "páginas legales"

    def __str__(self):
        return self.title


class LegalSection(OrderedModel):
    """Apartado de una página legal: un subtítulo y su texto."""

    page = models.ForeignKey(
        LegalPage, on_delete=models.CASCADE, related_name="sections", verbose_name="página"
    )
    title = models.CharField("subtítulo", max_length=120)
    body = models.TextField("texto", help_text="Los saltos de línea se respetan en el sitio.")

    class Meta(OrderedModel.Meta):
        verbose_name = "apartado"
        verbose_name_plural = "apartados"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Editar un apartado también cuenta como actualizar la página:
        # así cambia la fecha de "última actualización" que ve el visitante.
        self.page.save()


# ---------------------------------------------------------------------------
# Textos del formulario de cotización (specs-003, RF-31)
# ---------------------------------------------------------------------------


class QuoteFormField(models.Model):
    """
    Título y texto de ejemplo de un campo del formulario de cotización.

    Las filas son fijas y las crea una migración: el cliente cambia los
    textos, pero no agrega ni borra campos. `key` le dice al sitio a qué
    campo corresponde cada fila.
    """

    KEY_CHOICES = [
        ("name", "Nombre"),
        ("phone", "Teléfono"),
        ("email", "Correo"),
        ("category", "Tipo de remodelación"),
        ("location", "Ubicación del espacio"),
        ("areas", "Áreas a remodelar"),
        ("area_other", "Especificar el área (opción Otro)"),
        ("square_meters", "Metros cuadrados"),
        ("needs_visit", "Casilla: no sé cuántos m² son"),
        ("message", "Mensaje"),
        ("has_photos", "Casilla: tengo fotos del espacio"),
    ]

    section = models.ForeignKey(
        ContactSection,
        on_delete=models.CASCADE,
        related_name="form_fields",
        default=SINGLETON_PK,
        editable=False,
    )
    key = models.CharField("campo", max_length=30, unique=True, choices=KEY_CHOICES, editable=False)
    label = models.CharField("título", max_length=120)
    placeholder = models.CharField(
        "texto de ejemplo",
        max_length=120,
        blank=True,
        help_text="Lo que se lee dentro del campo antes de escribir. Las casillas no lo usan.",
    )
    order = models.PositiveSmallIntegerField("orden", default=0, editable=False)

    class Meta:
        ordering = ["order"]
        verbose_name = "campo del formulario"
        verbose_name_plural = "campos del formulario"

    def __str__(self):
        return self.get_key_display()
