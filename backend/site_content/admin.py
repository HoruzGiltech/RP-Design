from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from site_content.models import (
    ContactSection,
    FooterSection,
    HeroSection,
    ProcessSection,
    ProcessStep,
    ProjectsSection,
    SeoSettings,
    Service,
    ServicesSection,
    SiteSettings,
    Specialty,
)


class SingletonAdmin(admin.ModelAdmin):
    """
    Panel para modelos de un solo registro: no se puede agregar ni eliminar,
    y al entrar desde el menú se va directo al formulario de edición.
    """

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # load() crea el registro si por algún motivo no existiera
        instance = self.model.load()
        options = self.model._meta
        url = reverse(
            f"admin:{options.app_label}_{options.model_name}_change", args=[instance.pk]
        )
        return redirect(url)


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        (
            "Marca",
            {
                "fields": (
                    "brand_initials",
                    "brand_name",
                    "brand_subtitle",
                    "logo",
                    "header_cta_text",
                    "accent_color",
                )
            },
        ),
        (
            "Contacto",
            {
                "fields": (
                    "whatsapp_number",
                    "whatsapp_display",
                    "contact_email",
                    "instagram_handle",
                    "city",
                )
            },
        ),
        ("Calculadora", {"fields": ("price_note", "max_square_meters")}),
    )


@admin.register(
    HeroSection,
    ServicesSection,
    ProjectsSection,
    ProcessSection,
    ContactSection,
    FooterSection,
    SeoSettings,
)
class SectionAdmin(SingletonAdmin):
    """Las secciones únicas no necesitan nada más que el formulario por defecto."""


class OrderedListAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Listas que se ordenan arrastrando y se ocultan desde la misma lista."""

    list_editable = ("is_visible",)


@admin.register(Specialty)
class SpecialtyAdmin(OrderedListAdmin):
    list_display = ("text", "is_visible")


@admin.register(Service, ProcessStep)
class TitledListAdmin(OrderedListAdmin):
    list_display = ("title", "is_visible")
