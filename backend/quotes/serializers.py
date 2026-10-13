import re

from rest_framework import serializers

from quotes.models import Quote
from quotes.services import clean_phone

MIN_PHONE_DIGITS = 7
MAX_PHONE_DIGITS = 15


def required_messages(message):
    """El mismo mensaje para un campo que falta, que llega vacío o que llega nulo."""
    return {"required": message, "blank": message, "null": message}


class QuoteCreateSerializer(serializers.ModelSerializer):
    """
    Valida lo que envía el formulario del sitio (specs-008).

    El tipo de remodelación y la ubicación son obligatorios aquí, aunque en el
    modelo sean opcionales: las cotizaciones anteriores no los tienen.
    """

    remodel_type = serializers.CharField(
        max_length=120, error_messages=required_messages("Escribe qué quieres remodelar.")
    )
    location = serializers.CharField(
        max_length=160, error_messages=required_messages("Escribe la ubicación del espacio.")
    )
    # Opcional: la persona puede no saber los metros
    square_meters = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )

    # No es un campo del modelo: solo se comprueba que venga marcada.
    # La fecha de aceptación la pone el backend (ver quotes/views.py).
    privacy_accepted = serializers.BooleanField(
        write_only=True,
        error_messages={"required": "Debes aceptar la política de privacidad."},
    )

    class Meta:
        model = Quote
        fields = [
            "name",
            "email",
            "phone",
            "remodel_type",
            "location",
            "square_meters",
            "needs_visit",
            "has_photos",
            "message",
            "privacy_accepted",
        ]

    def validate_phone(self, phone):
        digits = re.sub(r"\D", "", phone)
        if not MIN_PHONE_DIGITS <= len(digits) <= MAX_PHONE_DIGITS:
            raise serializers.ValidationError("Escribe un número de teléfono válido.")
        return clean_phone(phone)

    def validate_square_meters(self, square_meters):
        if square_meters is not None and square_meters <= 0:
            raise serializers.ValidationError("Los metros cuadrados deben ser mayores que 0.")
        return square_meters

    def validate_privacy_accepted(self, accepted):
        if not accepted:
            raise serializers.ValidationError("Debes aceptar la política de privacidad.")
        return accepted

    def validate(self, data):
        # Quien pide una visita no sabe los metros: se ignoran aunque lleguen
        if data.get("needs_visit"):
            data["square_meters"] = None
        return data
