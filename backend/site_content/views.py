from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from site_content import serializers
from site_content.models import (
    ContactSection,
    FooterSection,
    HeroSection,
    LegalPage,
    ProcessSection,
    ProcessStep,
    ProjectsSection,
    SeoSettings,
    Service,
    ServicesSection,
    SiteSettings,
)


class SiteContentView(APIView):
    """
    GET /api/site/ -> todo el contenido del sitio en una sola llamada.

    Las secciones ocultas se envían igual, con "is_visible": false, y el
    frontend decide no mostrarlas. De las listas solo se envían los
    elementos visibles, ya ordenados.
    """

    throttle_scope = "public"

    def get(self, request):
        # Con el request, los serializers arman las URLs completas de los archivos
        context = {"request": request}

        def section(serializer_class, model):
            return serializer_class(model.load(), context=context).data

        def visible_items(serializer_class, model):
            items = model.objects.filter(is_visible=True)
            return serializer_class(items, many=True, context=context).data

        services = section(serializers.ServicesSectionSerializer, ServicesSection)
        services["items"] = visible_items(serializers.ServiceSerializer, Service)

        process = section(serializers.ProcessSectionSerializer, ProcessSection)
        process["steps"] = visible_items(serializers.ProcessStepSerializer, ProcessStep)

        return Response(
            {
                "settings": section(serializers.SiteSettingsSerializer, SiteSettings),
                "hero": section(serializers.HeroSectionSerializer, HeroSection),
                "services": services,
                "projects_section": section(
                    serializers.ProjectsSectionSerializer, ProjectsSection
                ),
                "process": process,
                "contact": section(serializers.ContactSectionSerializer, ContactSection),
                "footer": section(serializers.FooterSectionSerializer, FooterSection),
                "seo": section(serializers.SeoSettingsSerializer, SeoSettings),
                # Solo título y dirección, para los enlaces del pie de página
                "legal_pages": serializers.LegalPageLinkSerializer(
                    LegalPage.objects.all(), many=True
                ).data,
            }
        )


class LegalPageView(generics.RetrieveAPIView):
    """GET /api/legal/<slug>/ -> una página legal con sus apartados."""

    serializer_class = serializers.LegalPageSerializer
    throttle_scope = "public"
    lookup_field = "slug"
    queryset = LegalPage.objects.prefetch_related("sections")
