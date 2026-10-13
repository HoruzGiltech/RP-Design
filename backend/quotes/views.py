from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from quotes.models import Quote
from quotes.serializers import QuoteCreateSerializer
from quotes.services import build_whatsapp_link, build_whatsapp_message
from site_content.models import SiteSettings

# Campo trampa: está oculto en el formulario, así que una persona nunca lo llena
HONEYPOT_FIELD = "website"


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
                "whatsapp_url": build_whatsapp_link(whatsapp_number, quote.whatsapp_message),
            },
            status=status.HTTP_201_CREATED,
        )

    def _build_quote(self, data):
        """Arma la cotización con el mensaje de WhatsApp ya redactado."""
        # privacy_accepted no es un campo de Quote: se cambia por la fecha de aceptación
        data.pop("privacy_accepted")
        quote = Quote(**data)
        quote.privacy_accepted_at = timezone.now()
        # El mensaje se guarda: así el cliente no pierde el contacto aunque la
        # persona no llegue a enviarlo por WhatsApp.
        quote.whatsapp_message = build_whatsapp_message(quote)
        return quote

    def _fake_success(self):
        """
        Respuesta para los bots: parece un envío correcto, pero no se guarda nada.
        Así el bot no se entera de que fue detectado y no prueba otra cosa.
        """
        return Response(
            {"id": 0, "whatsapp_url": "https://wa.me/"},
            status=status.HTTP_201_CREATED,
        )
