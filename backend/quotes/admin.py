from django.contrib import admin
from django.utils.html import format_html

from quotes.models import Quote, QuoteItem
from quotes.services import build_whatsapp_link, format_usd

# RemodelArea ("Áreas y precios") ya no se registra en el panel: desde specs-008
# el formulario no pide áreas ni calcula precios. El modelo y sus datos se
# conservan para las cotizaciones anteriores.


class QuoteItemInline(admin.TabularInline):
    """
    Las áreas de una cotización anterior a specs-008, cuando el formulario
    pedía áreas con sus metros y calculaba un estimado. Solo se leen.
    """

    model = QuoteItem
    extra = 0
    fields = ("area", "area_other", "square_meters", "price_per_m2_snapshot", "subtotal_display")
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Subtotal")
    def subtotal_display(self, item):
        return format_usd(item.subtotal)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "name",
        "phone",
        "type_display",
        "location",
        "status",
    )
    list_display_links = ("created_at", "name")
    list_editable = ("status",)
    list_filter = ("status", "needs_visit", "has_photos", "created_at")
    search_fields = ("name", "email", "phone", "remodel_type", "location")
    date_hierarchy = "created_at"

    # Lo que tienen todas las cotizaciones
    BASE_FIELDS = (
        "status",
        "created_at",
        "name",
        "email",
        "phone",
        "whatsapp_link",
        "type_display",
        "location",
        "square_meters",
        "needs_visit",
        "has_photos",
        "message",
        "whatsapp_message",
        "privacy_accepted_at",
    )
    # Lo que solo tienen las cotizaciones anteriores a specs-008
    OLD_QUOTE_FIELDS = ("estimate_display",)

    # El estado es lo único que se puede cambiar: el resto es lo que envió la persona
    readonly_fields = tuple(
        field for field in BASE_FIELDS + OLD_QUOTE_FIELDS if field != "status"
    )

    def has_add_permission(self, request):
        # Las cotizaciones solo llegan desde el formulario del sitio
        return False

    def get_queryset(self, request):
        # Trae las áreas de todas las cotizaciones en una sola consulta
        return super().get_queryset(request).prefetch_related("items__area")

    def get_fields(self, request, obj=None):
        if obj and self._is_old_quote(obj):
            return self.BASE_FIELDS + self.OLD_QUOTE_FIELDS
        return self.BASE_FIELDS

    def get_inlines(self, request, obj):
        # La tabla de áreas solo aparece en las cotizaciones que las tienen
        if obj and self._is_old_quote(obj):
            return [QuoteItemInline]
        return []

    def _is_old_quote(self, quote):
        return len(quote.items.all()) > 0

    @admin.display(description="Tipo de remodelación")
    def type_display(self, quote):
        # Las cotizaciones anteriores no tienen el tipo escrito: tenían una categoría
        return quote.remodel_type or quote.category_name or "—"

    @admin.display(description="Estimado total", ordering="estimated_price")
    def estimate_display(self, quote):
        return format_usd(quote.estimated_price)

    @admin.display(description="Escribirle")
    def whatsapp_link(self, quote):
        url = build_whatsapp_link(quote.phone, "")
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Abrir WhatsApp</a>', url
        )
