import re

from rest_framework import serializers

from quotes.models import Quote, RemodelArea
from quotes.services import clean_phone, format_square_meters
from site_content.models import SiteSettings

MIN_PHONE_DIGITS = 7
MAX_PHONE_DIGITS = 15


class RemodelAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemodelArea
        fields = ["id", "name", "price_per_m2", "is_other"]


class QuoteCreateSerializer(serializers.ModelSerializer):
    """
    Valida lo que envía el formulario del sitio.

    No incluye el precio: aunque el navegador lo envíe, se ignora.
    El precio lo calcula siempre el backend (ver quotes/views.py).
    """

    # Solo se puede elegir un área que esté activa
    area = serializers.PrimaryKeyRelatedField(
        queryset=RemodelArea.objects.filter(is_active=True),
        error_messages={
            "does_not_exist": "Elige un área de la lista.",
            "incorrect_type": "Elige un área de la lista.",
            "required": "Elige el área a remodelar.",
            "null": "Elige el área a remodelar.",
        },
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
            "area",
            "area_other",
            "square_meters",
            "message",
            "privacy_accepted",
        ]

    def validate_phone(self, phone):
        digits = re.sub(r"\D", "", phone)
        if not MIN_PHONE_DIGITS <= len(digits) <= MAX_PHONE_DIGITS:
            raise serializers.ValidationError("Escribe un número de teléfono válido.")
        return clean_phone(phone)

    def validate_square_meters(self, square_meters):
        maximum = SiteSettings.load().max_square_meters
        if square_meters <= 0:
            raise serializers.ValidationError("Los metros cuadrados deben ser mayores que 0.")
        if square_meters > maximum:
            raise serializers.ValidationError(f"El máximo es {format_square_meters(maximum)} m².")
        return square_meters

    def validate_privacy_accepted(self, accepted):
        if not accepted:
            raise serializers.ValidationError("Debes aceptar la política de privacidad.")
        return accepted

    def validate(self, data):
        area_other = data.get("area_other", "").strip()
        if data["area"].is_other and not area_other:
            raise serializers.ValidationError(
                {"area_other": "Especifica qué área quieres remodelar."}
            )
        # Si el área no es "Otro", ese campo no aplica y se guarda vacío
        data["area_other"] = area_other if data["area"].is_other else ""
        return data
