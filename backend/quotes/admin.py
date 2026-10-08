from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.utils.html import format_html

from quotes.models import Quote, RemodelArea
from quotes.services import build_whatsapp_link, format_usd


@admin.register(RemodelArea)
class RemodelAreaAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("name", "category", "price_per_m2", "is_active", "is_other")
    # La categoría y el precio se cambian directo en la lista, sin entrar a cada área
    list_editable = ("category", "price_per_m2", "is_active")
    list_filter = ("category", "is_active")
    # El identificador no aparece: se genera solo a partir del nombre
    fields = ("name", "category", "price_per_m2", "is_other", "is_active")


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "name",
        "phone",
        "category_name",
        "area",
        "square_meters",
        "estimate_display",
        "status",
    )
    list_display_links = ("created_at", "name")
    list_editable = ("status",)
    list_filter = ("status", "category", "area", "created_at")
    search_fields = ("name", "email", "phone")
    date_hierarchy = "created_at"

    # El estado es lo único que se puede cambiar: el resto es lo que envió la persona
    fields = (
        "status",
        "created_at",
        "name",
        "email",
        "phone",
        "whatsapp_link",
        "category_name",
        "area",
        "area_other",
        "square_meters",
        "price_per_m2_snapshot",
        "estimate_display",
        "message",
        "whatsapp_message",
        "privacy_accepted_at",
    )
    readonly_fields = tuple(field for field in fields if field != "status")

    def has_add_permission(self, request):
        # Las cotizaciones solo llegan desde el formulario del sitio
        return False

    @admin.display(description="Estimado", ordering="estimated_price")
    def estimate_display(self, quote):
        return format_usd(quote.estimated_price)

    @admin.display(description="Escribirle")
    def whatsapp_link(self, quote):
        url = build_whatsapp_link(quote.phone, "")
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Abrir WhatsApp</a>', url
        )
