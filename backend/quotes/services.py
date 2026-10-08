"""
Reglas de negocio de las cotizaciones.

Son funciones simples, sin efectos secundarios: reciben datos y devuelven
un resultado. Por eso son fáciles de probar una por una.
"""
import re
from decimal import Decimal
from urllib.parse import quote as url_encode

TO_BE_QUOTED = "A cotizar"
TWO_DECIMALS = Decimal("0.01")


def calculate_estimate(area, square_meters):
    """Devuelve m² × precio del área, o None si el área no tiene precio."""
    if area.price_per_m2 is None:
        return None
    return (area.price_per_m2 * square_meters).quantize(TWO_DECIMALS)


def _to_venezuelan_format(number_text):
    """Cambia '1,250.50' por '1.250,50' (punto para miles y coma para decimales)."""
    return number_text.replace(",", "#").replace(".", ",").replace("#", ".")


def format_usd(amount):
    """Decimal('1250.5') -> 'USD 1.250,50'. None -> 'A cotizar'."""
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


def area_belongs_to_category(area, category):
    """
    Dice si un área se puede elegir dentro de un tipo de remodelación:
    lo es si pertenece a esa categoría o si es común a todas (sin categoría).
    """
    return area.category_id is None or area.category_id == category.pk


def build_whatsapp_message(quote):
    """Arma el texto que la persona enviará por WhatsApp."""
    area = quote.area.name
    if quote.area.is_other and quote.area_other:
        area = f"{area}: {quote.area_other}"

    lines = [
        "Hola RP Design, quiero una cotización:",
        "",
        f"👤 Nombre: {quote.name}",
        f"📧 Correo: {quote.email}",
        f"📱 Teléfono: {quote.phone}",
    ]
    # Las cotizaciones anteriores a specs-002 no tienen tipo: la línea se omite
    if quote.category_name:
        lines.append(f"🏗️ Tipo: {quote.category_name}")
    lines += [
        f"🏠 Área: {area}",
        f"📐 Metros cuadrados: {format_square_meters(quote.square_meters)} m²",
        f"💲 Estimado: {format_usd(quote.estimated_price)}",
    ]
    if quote.message:
        lines += ["", f"💬 Mensaje: {quote.message}"]
    return "\n".join(lines)


def build_whatsapp_link(phone, message):
    """
    Devuelve https://wa.me/<número>?text=<mensaje>.

    Es la única función que sabe de WhatsApp. Si algún día se usa la API
    oficial de WhatsApp Business, solo hay que cambiar esta función.
    """
    number = re.sub(r"\D", "", phone)
    return f"https://wa.me/{number}?text={url_encode(message, safe='')}"
