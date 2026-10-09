from rest_framework import serializers

from site_content.models import (
    ContactSection,
    FooterSection,
    HeroSection,
    LegalPage,
    LegalSection,
    ProcessSection,
    ProcessStep,
    ProjectsSection,
    SeoSettings,
    Service,
    ServicesSection,
    SiteSettings,
    Specialty,
)
from site_content.services import format_whatsapp_number


class SiteSettingsSerializer(serializers.ModelSerializer):
    instagram_url = serializers.SerializerMethodField()
    # No es un campo del panel: se calcula a partir del número (specs-001, RF-11)
    whatsapp_display = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = [
            "brand_initials",
            "brand_name",
            "brand_subtitle",
            "logo",
            "header_cta_text",
            "accent_color",
            "whatsapp_number",
            "whatsapp_display",
            "whatsapp_greeting",
            "show_whatsapp_button",
            "heading_font",
            "body_font",
            "show_estimate",
            "contact_email",
            "instagram_handle",
            "instagram_url",
            "city",
            "price_note",
            "max_square_meters",
        ]

    def get_whatsapp_display(self, settings):
        return format_whatsapp_number(settings.whatsapp_number)

    def get_instagram_url(self, settings):
        if not settings.instagram_handle:
            return ""
        return f"https://www.instagram.com/{settings.instagram_handle}/"


class HeroSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSection
        fields = [
            "is_visible",
            "eyebrow",
            "title",
            "body",
            "primary_cta_text",
            "show_primary_cta",
            "secondary_cta_text",
            "show_secondary_cta",
            "image",
            "image_alt",
            "video",
        ]


class ServicesSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicesSection
        fields = ["is_visible", "title", "intro", "cta_text"]


class ProjectsSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectsSection
        fields = ["is_visible", "title", "instagram_link_text", "view_all_text"]


class ProcessSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessSection
        fields = ["is_visible", "title", "intro", "video", "video_poster"]


class ContactSectionSerializer(serializers.ModelSerializer):
    form_fields = serializers.SerializerMethodField()

    class Meta:
        model = ContactSection
        fields = ["is_visible", "title", "intro", "submit_text", "form_fields"]

    def get_form_fields(self, contact):
        """
        Textos del formulario, indexados por campo para que el sitio los lea directo:
        { "name": { "label": "Nombre", "placeholder": "Tu nombre" }, ... }
        """
        return {
            form_field.key: {"label": form_field.label, "placeholder": form_field.placeholder}
            for form_field in contact.form_fields.all()
        }


class FooterSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterSection
        fields = ["is_visible", "name", "tagline"]


class SeoSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeoSettings
        fields = ["site_title", "meta_description", "share_image"]


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ["id", "text"]


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "title", "description"]


class ProcessStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStep
        fields = ["id", "title", "description"]


class LegalPageLinkSerializer(serializers.ModelSerializer):
    """Lo mínimo para armar los enlaces del pie de página."""

    class Meta:
        model = LegalPage
        fields = ["slug", "title"]


class LegalSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalSection
        fields = ["id", "title", "body"]


class LegalPageSerializer(serializers.ModelSerializer):
    # Los apartados llegan ya ordenados: LegalSection se ordena por "order"
    sections = LegalSectionSerializer(many=True, read_only=True)

    class Meta:
        model = LegalPage
        fields = ["slug", "title", "intro", "updated_at", "sections"]
