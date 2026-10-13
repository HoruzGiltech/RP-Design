"""
Reglas de negocio de las cotizaciones.

Son funciones simples, sin efectos secundarios: reciben datos y devuelven
un resultado. Por eso son fáciles de probar una por una.
"""
import re
from urllib.parse import quote as url_encode

TO_BE_QUOTED = "A cotizar"


def _to_venezuelan_format(number_text):
    """Cambia '1,250.50' por '1.250,50' (punto para miles y coma para decimales)."""
    return number_text.replace(",", "#").replace(".", ",").replace("#", ".")


def format_usd(amount):
    """
    Decimal('1250.5') -> 'USD 1.250,50'. None -> 'A cotizar'.

    Desde specs-008 el sitio ya no calcula precios. Esta función sigue aquí
    porque el panel muestra el estimado de las cotizaciones anteriores.
    """
    if amount is None:
        return TO_BE_QUOTED
    return f"USD {_to_venezuelan_format(f'{amount:,.2f}')}"


def format_square_meters(square_meters):
    """Decimal('12.50') -> '12,5'. Decimal('30.00') -> '30'."""
    text = f"{square_meters:,.2f}".rstrip("0").rstrip(".")
    return _to_venezuelan_format(text)


def clean_phone(phone):
    """Deja solo el '+' inicial y los dígitos: '+58 412-123 45 67' -> '+584121234567'."""
    digits = re.sub(r"\D", "", phone)
    return f"+{digits}" if phone.strip().startswith("+") else digits


def build_whatsapp_message(quote):
    """
    Arma el texto que la persona enviará por WhatsApp.

    No lleva emojis: algunas versiones de WhatsApp los muestran como "?"
    cuando llegan dentro de un enlace. Cada línea empieza con un guion.
    Las líneas de lo que la persona no llenó se omiten.
    """
    lines = [
        "Hola RP Design, quiero una cotización:",
        "",
        f"- Nombre: {quote.name}",
        f"- Correo: {quote.email}",
        f"- Teléfono: {quote.phone}",
        f"- Tipo de remodelación: {quote.remodel_type}",
        f"- Ubicación: {quote.location}",
    ]
    if quote.square_meters is not None:
        lines.append(f"- Metros cuadrados: {format_square_meters(quote.square_meters)} m²")
    if quote.needs_visit:
        lines.append("- No sé los m²: quiero agendar una visita")
    if quote.has_photos:
        lines.append("- Tengo fotos del espacio")
    if quote.message:
        lines += ["", f"- Mensaje: {quote.message}"]
    return "\n".join(lines)


def build_whatsapp_link(phone, message):
    """
    Devuelve https://wa.me/<número>?text=<mensaje>.

    Es la única función que sabe de WhatsApp. Si algún día se usa la API
    oficial de WhatsApp Business, solo hay que cambiar esta función.
    """
    number = re.sub(r"\D", "", phone)
    return f"https://wa.me/{number}?text={url_encode(message, safe='')}"
