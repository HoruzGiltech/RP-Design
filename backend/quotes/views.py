from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import ProjectCategory
from quotes.models import Quote, RemodelArea
from quotes.serializers import QuoteCategorySerializer, QuoteCreateSerializer
from quotes.services import (
    build_whatsapp_link,
    build_whatsapp_message,
    calculate_estimate,
    format_usd,
)
from site_content.models import SiteSettings

# Campo trampa: está oculto en el formulario, así que una persona nunca lo llena
HONEYPOT_FIELD = "website"


class QuoteCategoryListView(APIView):
    """
    GET /api/quote-categories/ -> tipos de remodelación con sus áreas.

    Cada tipo es una categoría del panel. Sus áreas son las que pertenecen a
    esa categoría más las comunes a todas (las que no tienen categoría, como
    "Otro"), que van al final. Un tipo sin ninguna área no se envía.
    """

    throttle_scope = "public"

    def get(self, request):
        active_areas = list(RemodelArea.objects.filter(is_active=True))
        common_areas = [area for area in active_areas if area.category_id is None]

        categories = []
        for category in ProjectCategory.objects.all():
            own_areas = [area for area in active_areas if area.category_id == category.pk]
            category.form_areas = own_areas + common_areas
            if category.form_areas:
                categories.append(category)

        return Response(QuoteCategorySerializer(categories, many=True).data)


class QuoteCreateView(APIView):
    """POST /api/quotes/ -> guarda la cotización y devuelve el enlace de WhatsApp."""

    throttle_scope = "quotes"

    def post(self, request):
        if request.data.get(HONEYPOT_FIELD):
            return self._fake_success()

        serializer = QuoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quote = self._build_quote(serializer.validated_data)
        quote.save()

        whatsapp_number = SiteSettings.load().whatsapp_number
        return Response(
            {
                "id": quote.pk,
                # Como texto ("1250.00") para no perder decimales al pasar por JSON
                "estimated_price": self._as_text(quote.estimated_price),
                "estimated_price_display": format_usd(quote.estimated_price),
                "whatsapp_url": build_whatsapp_link(whatsapp_number, quote.whatsapp_message),
            },
            status=status.HTTP_201_CREATED,
        )

    def _build_quote(self, data):
        """Calcula el precio aquí, en el servidor, y arma el mensaje con ese precio."""
        # privacy_accepted no es un campo de Quote: se cambia por la fecha de aceptación
        data.pop("privacy_accepted")
        quote = Quote(**data)
        # Copia del nombre del tipo: la cotización lo conserva aunque la categoría cambie
        quote.category_name = quote.category.name
        quote.privacy_accepted_at = timezone.now()
        quote.price_per_m2_snapshot = quote.area.price_per_m2
        quote.estimated_price = calculate_estimate(quote.area, quote.square_meters)
        quote.whatsapp_message = build_whatsapp_message(quote)
        return quote

    def _as_text(self, amount):
        return None if amount is None else f"{amount:.2f}"

    def _fake_success(self):
        """
        Respuesta para los bots: parece un envío correcto, pero no se guarda nada.
        Así el bot no se entera de que fue detectado y no prueba otra cosa.
        """
        return Response(
            {
                "id": 0,
                "estimated_price": None,
                "estimated_price_display": format_usd(None),
                "whatsapp_url": "https://wa.me/",
            },
            status=status.HTTP_201_CREATED,
        )
