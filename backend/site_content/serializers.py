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


class SiteSettingsSerializer(serializers.ModelSerializer):
    instagram_url = serializers.SerializerMethodField()

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
            "contact_email",
            "instagram_handle",
            "instagram_url",
            "city",
            "price_note",
            "max_square_meters",
        ]

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
            "secondary_cta_text",
            "image",
            "image_alt",
            "video",
        ]


class ServicesSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicesSection
        fields = ["is_visible", "title", "intro"]


class ProjectsSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectsSection
        fields = ["is_visible", "title", "instagram_link_text", "view_all_text"]


class ProcessSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessSection
        fields = ["is_visible", "title", "intro", "video", "video_poster"]


class ContactSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSection
        fields = ["is_visible", "title", "intro", "submit_text"]


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
