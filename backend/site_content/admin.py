from adminsortable2.admin import SortableAdminBase, SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from site_content.models import (
    ContactSection,
    FooterSection,
    HeroSection,
    LegalPage,
    LegalSection,
    ProcessSection,
    ProcessStep,
    ProjectsSection,
    QuoteFormField,
    SeoSettings,
    Service,
    ServicesSection,
    SiteSettings,
    Specialty,
)


class SingletonAdmin(SortableAdminBase, admin.ModelAdmin):
    """
    Panel para modelos de un solo registro: no se puede agregar ni eliminar,
    y al entrar desde el menú se va directo al formulario de edición.

    Hereda de SortableAdminBase porque algunas secciones llevan dentro una
    tabla que se ordena arrastrando (servicios, pasos del proceso).
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
                    "contact_email",
                    "instagram_handle",
                    "city",
                )
            },
        ),
        (
            "Botón flotante de WhatsApp",
            {"fields": ("show_whatsapp_button", "whatsapp_greeting")},
        ),
        (
            "Tipografía",
            {"fields": ("heading_font", "body_font")},
        ),
        ("Calculadora", {"fields": ("show_estimate", "price_note", "max_square_meters")}),
    )


@admin.register(HeroSection, ProjectsSection, FooterSection, SeoSettings)
class SectionAdmin(SingletonAdmin):
    """Las secciones únicas no necesitan nada más que el formulario por defecto."""


class SectionItemInline(SortableInlineAdminMixin, admin.StackedInline):
    """Lista que se edita y se ordena arrastrando dentro del formulario de su sección."""

    extra = 0
    fields = ("title", "description", "is_visible")


class ServiceInline(SectionItemInline):
    model = Service


class ProcessStepInline(SectionItemInline):
    model = ProcessStep


@admin.register(ServicesSection)
class ServicesSectionAdmin(SingletonAdmin):
    """El encabezado de Servicios y, debajo, sus tarjetas."""

    inlines = [ServiceInline]


@admin.register(ProcessSection)
class ProcessSectionAdmin(SingletonAdmin):
    """El encabezado de Proceso y, debajo, sus pasos."""

    inlines = [ProcessStepInline]


class QuoteFormFieldInline(admin.TabularInline):
    """
    Títulos y textos de ejemplo de los campos del formulario.
    Las filas son fijas: se editan, pero no se agregan ni se borran.
    """

    model = QuoteFormField
    extra = 0
    # El nombre del campo no hace falta como columna: el panel ya lo escribe sobre cada fila
    fields = ("label", "placeholder")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactSection)
class ContactSectionAdmin(SingletonAdmin):
    """El encabezado de Contacto y los textos del formulario."""

    inlines = [QuoteFormFieldInline]


class OrderedListAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Listas que se ordenan arrastrando y se ocultan desde la misma lista."""

    list_editable = ("is_visible",)


@admin.register(Specialty)
class SpecialtyAdmin(OrderedListAdmin):
    list_display = ("text", "is_visible")


class LegalSectionInline(SortableInlineAdminMixin, admin.StackedInline):
    """Apartados de la página: se editan y se ordenan dentro de la misma página."""

    model = LegalSection
    extra = 0


@admin.register(LegalPage)
class LegalPageAdmin(SortableAdminBase, admin.ModelAdmin):
    """Las dos páginas legales se editan, pero no se agregan ni se eliminan."""

    list_display = ("title", "updated_at")
    fields = ("title", "intro")
    inlines = [LegalSectionInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
