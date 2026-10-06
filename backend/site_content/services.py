"""Funciones de apoyo del contenido del sitio."""
import re

VENEZUELA_CODE = "58"
VENEZUELA_DIGITS = 12


def format_whatsapp_number(number):
    """
    Muestra el número de WhatsApp en formato internacional.

    '584127305964' -> '+58 412 730 5964'

    Solo se agrupan los números de Venezuela, que es el formato que se conoce.
    Para otros países se devuelve '+' y los dígitos, sin inventar agrupaciones.
    """
    digits = re.sub(r"\D", "", number or "")
    if not digits:
        return ""

    is_venezuelan = digits.startswith(VENEZUELA_CODE) and len(digits) == VENEZUELA_DIGITS
    if is_venezuelan:
        # 58 | 412 | 730 | 5964
        return f"+{digits[:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}"
    return f"+{digits}"
