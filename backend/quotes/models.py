from django.db import models

from core.models import OrderedModel, TimeStampedModel


class RemodelArea(OrderedModel):
    """Área que se puede remodelar (baño, cocina...) y su precio por metro cuadrado."""

    name = models.CharField("nombre", max_length=60)
    slug = models.SlugField("identificador", max_length=70, unique=True)
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


class Quote(TimeStampedModel):
    """Cotización enviada desde el formulario del sitio."""

    NEW = "new"
    CONTACTED = "contacted"
    CLOSED = "closed"
    STATUS_CHOICES = [(NEW, "Nuevo"), (CONTACTED, "Contactado"), (CLOSED, "Cerrado")]

    name = models.CharField("nombre", max_length=120)
    email = models.EmailField("correo")
    phone = models.CharField("teléfono", max_length=30)
    # PROTECT: no se puede borrar un área que ya tiene cotizaciones
    area = models.ForeignKey(
        RemodelArea, on_delete=models.PROTECT, related_name="quotes", verbose_name="área"
    )
    area_other = models.CharField("área especificada", max_length=120, blank=True)
    square_meters = models.DecimalField("metros cuadrados", max_digits=8, decimal_places=2)
    # Copia del precio del momento: si el cliente cambia sus precios después,
    # las cotizaciones viejas conservan su valor.
    price_per_m2_snapshot = models.DecimalField(
        "precio por m² usado (USD)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    estimated_price = models.DecimalField(
        "estimado (USD)",
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
        return f"{self.name} — {self.area}"
