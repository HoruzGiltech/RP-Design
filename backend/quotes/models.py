from django.db import models
from django.utils.text import slugify

from core.models import OrderedModel, TimeStampedModel
from projects.models import ProjectCategory
from projects.services import make_unique_slug


class RemodelArea(OrderedModel):
    """Área que se puede remodelar (baño, cocina...) y su precio por metro cuadrado."""

    name = models.CharField("nombre", max_length=60)
    # Se genera solo a partir del nombre. Dos áreas pueden llamarse igual en
    # categorías distintas ("Sala"): la segunda recibe "sala-2".
    slug = models.SlugField("identificador", max_length=70, unique=True, editable=False)
    # El tipo de remodelación al que pertenece el área (specs-002, RF-17).
    # PROTECT: no se puede borrar una categoría que todavía tiene áreas.
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.PROTECT,
        related_name="remodel_areas",
        verbose_name="categoría",
        null=True,
        blank=True,
        help_text=(
            "Tipo de remodelación en el que aparece esta área. Déjala vacía para que "
            "aparezca en todos los tipos (por ejemplo, Otro)."
        ),
    )
    price_per_m2 = models.DecimalField(
        "precio por m² (USD)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Si se deja vacío, el sitio muestra "A cotizar".',
    )
    is_other = models.BooleanField(
        'es la opción "Otro"',
        default=False,
        help_text="Si está marcado, el formulario pide especificar el área.",
    )
    is_active = models.BooleanField(
        "activa", default=True, help_text="Las áreas inactivas no aparecen en el formulario."
    )

    class Meta(OrderedModel.Meta):
        verbose_name = "área a remodelar"
        verbose_name_plural = "áreas y precios"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            existing = set(RemodelArea.objects.values_list("slug", flat=True))
            self.slug = make_unique_slug(slugify(self.name) or "area", existing)
        super().save(*args, **kwargs)


class Quote(TimeStampedModel):
    """Cotización enviada desde el formulario del sitio."""

    NEW = "new"
    CONTACTED = "contacted"
    CLOSED = "closed"
    STATUS_CHOICES = [(NEW, "Nuevo"), (CONTACTED, "Contactado"), (CLOSED, "Cerrado")]

    name = models.CharField("nombre", max_length=120)
    email = models.EmailField("correo")
    phone = models.CharField("teléfono", max_length=30)
    # Tipo de remodelación elegido. SET_NULL: si la categoría se borra, la
    # cotización se conserva; por eso también se guarda una copia de su nombre.
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        related_name="quotes",
        verbose_name="tipo de remodelación",
        null=True,
        blank=True,
    )
    category_name = models.CharField("tipo (nombre al cotizar)", max_length=60, blank=True)
    location = models.CharField("ubicación del espacio", max_length=160, blank=True)
    has_photos = models.BooleanField("tiene fotos del espacio", default=False)
    needs_visit = models.BooleanField(
        "pide una visita",
        default=False,
        help_text="La persona no sabe los metros cuadrados: sus áreas no tienen m² ni precio.",
    )
    # Las áreas elegidas están en QuoteItem (quote.items). Esto es la suma de sus subtotales.
    estimated_price = models.DecimalField(
        "estimado total (USD)",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Vacío significa "A cotizar".',
    )
    message = models.TextField("mensaje", max_length=1000, blank=True)
    whatsapp_message = models.TextField("mensaje de WhatsApp")
    status = models.CharField("estado", max_length=10, choices=STATUS_CHOICES, default=NEW)
    # Prueba de que la persona aceptó el tratamiento de sus datos, y cuándo.
    # Vacío solo en cotizaciones anteriores a que existiera la casilla.
    privacy_accepted_at = models.DateTimeField(
        "aceptó la política de privacidad", null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "cotización"
        verbose_name_plural = "cotizaciones"

    def __str__(self):
        return f"{self.name} — {self.created_at:%d/%m/%Y}"


class QuoteItem(models.Model):
    """Un renglón de la cotización: un área, con sus metros cuadrados y su precio."""

    quote = models.ForeignKey(
        Quote, on_delete=models.CASCADE, related_name="items", verbose_name="cotización"
    )
    # PROTECT: no se puede borrar un área que ya tiene cotizaciones
    area = models.ForeignKey(
        RemodelArea, on_delete=models.PROTECT, related_name="quote_items", verbose_name="área"
    )
    area_other = models.CharField("área especificada", max_length=120, blank=True)
    # Vacío cuando la persona pidió una visita porque no sabe los metros
    square_meters = models.DecimalField(
        "metros cuadrados", max_digits=8, decimal_places=2, null=True, blank=True
    )
    # Copia del precio del momento: si el cliente cambia sus precios después,
    # las cotizaciones viejas conservan su valor.
    price_per_m2_snapshot = models.DecimalField(
        "precio por m² usado (USD)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    subtotal = models.DecimalField(
        "subtotal (USD)",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Vacío significa "A cotizar".',
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "área cotizada"
        verbose_name_plural = "áreas cotizadas"

    def __str__(self):
        return self.area.name
