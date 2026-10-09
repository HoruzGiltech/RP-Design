import re

from rest_framework import serializers

from projects.models import ProjectCategory
from quotes.models import Quote, RemodelArea
from quotes.services import area_belongs_to_category, clean_phone, format_square_meters
from site_content.models import SiteSettings

MIN_PHONE_DIGITS = 7
MAX_PHONE_DIGITS = 15
# Tope de áreas por cotización. Ningún tipo de remodelación tiene tantas:
# solo evita que alguien envíe una lista enorme.
MAX_ITEMS = 30


def first_message(errors):
    """De los errores de un serializer ({campo: [mensajes]}), devuelve el primer mensaje."""
    return str(next(iter(errors.values()))[0])


def items_error(message):
    """Error que el sitio muestra debajo de la lista de áreas."""
    return serializers.ValidationError({"items": [message]})


class RemodelAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemodelArea
        fields = ["id", "name", "price_per_m2", "is_other"]


class QuoteCategorySerializer(serializers.ModelSerializer):
    """
    Un tipo de remodelación con las áreas que se pueden elegir en él.
    La vista le pone a cada categoría la lista `form_areas` ya armada.
    """

    areas = RemodelAreaSerializer(source="form_areas", many=True, read_only=True)

    class Meta:
        model = ProjectCategory
        fields = ["id", "name", "slug", "areas"]


class QuoteItemInputSerializer(serializers.Serializer):
    """Un área marcada en el formulario, con sus metros cuadrados."""

    # Solo se puede elegir un área que esté activa
    area = serializers.PrimaryKeyRelatedField(
        queryset=RemodelArea.objects.filter(is_active=True),
        error_messages={
            "does_not_exist": "Elige un área de la lista.",
            "incorrect_type": "Elige un área de la lista.",
            "required": "Elige un área de la lista.",
            "null": "Elige un área de la lista.",
        },
    )
    area_other = serializers.CharField(max_length=120, required=False, allow_blank=True)
    # Opcional aquí: si hacen falta o no depende de la casilla de visita (ver validate)
    square_meters = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )


class QuoteCreateSerializer(serializers.ModelSerializer):
    """
    Valida lo que envía el formulario del sitio.

    No incluye ningún precio: aunque el navegador lo envíe, se ignora.
    Los precios los calcula siempre el backend (ver quotes/views.py).
    """

    # El tipo de remodelación: una de las categorías visibles del panel
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProjectCategory.objects.filter(is_visible=True),
        error_messages={
            "does_not_exist": "Elige el tipo de remodelación.",
            "incorrect_type": "Elige el tipo de remodelación.",
            "required": "Elige el tipo de remodelación.",
            "null": "Elige el tipo de remodelación.",
        },
    )

    # Las áreas marcadas: una o varias. Aquí solo se comprueba que llegue una
    # lista; cada área se revisa en validate() con QuoteItemInputSerializer,
    # para que todos los errores de áreas salgan con la misma forma.
    items = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False,
        max_length=MAX_ITEMS,
        error_messages={
            "required": "Elige al menos un área.",
            "null": "Elige al menos un área.",
            "empty": "Elige al menos un área.",
            "not_a_list": "Elige al menos un área.",
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
            "category",
            "location",
            "items",
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

    def validate_privacy_accepted(self, accepted):
        if not accepted:
            raise serializers.ValidationError("Debes aceptar la política de privacidad.")
        return accepted

    def validate(self, data):
        needs_visit = data.get("needs_visit", False)
        seen_area_ids = set()
        items = []

        for raw_item in data["items"]:
            item_serializer = QuoteItemInputSerializer(data=raw_item)
            if not item_serializer.is_valid():
                raise items_error(first_message(item_serializer.errors))
            item = dict(item_serializer.validated_data)
            area = item["area"]
            # El área tiene que ser del tipo elegido (o común a todos, como "Otro")
            if not area_belongs_to_category(area, data["category"]):
                raise items_error("Elige un área de la lista.")
            if area.pk in seen_area_ids:
                raise items_error("No repitas un área.")
            seen_area_ids.add(area.pk)

            area_other = item.get("area_other", "").strip()
            if area.is_other and not area_other:
                raise items_error("Especifica qué área quieres remodelar.")
            # Si el área no es "Otro", ese texto no aplica y se guarda vacío
            item["area_other"] = area_other if area.is_other else ""

            # Quien pide una visita no sabe los metros: se ignoran aunque lleguen
            if needs_visit:
                item["square_meters"] = None
            else:
                item["square_meters"] = self._check_square_meters(item.get("square_meters"))
            items.append(item)

        data["items"] = items
        return data

    def _check_square_meters(self, square_meters):
        maximum = SiteSettings.load().max_square_meters
        if square_meters is None:
            raise items_error("Escribe los metros cuadrados de cada área.")
        if square_meters <= 0:
            raise items_error("Los metros cuadrados deben ser mayores que 0.")
        if square_meters > maximum:
            raise items_error(f"El máximo es {format_square_meters(maximum)} m².")
        return square_meters
