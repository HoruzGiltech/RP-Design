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
    """
    Devuelve m² × precio del área. Devuelve None ("A cotizar") si el área no
    tiene precio o si no se dieron los metros (la persona pidió una visita).
    """
    if area.price_per_m2 is None or square_meters is None:
        return None
    return (area.price_per_m2 * square_meters).quantize(TWO_DECIMALS)


def calculate_total(subtotals):
    """
    Suma los subtotales de todas las áreas.

    Si alguna área está "A cotizar" (None), el total también lo está: mostrar
    una suma parcial haría creer que ese es el precio de todo.
    """
    if not subtotals or None in subtotals:
        return None
    return sum(subtotals, Decimal("0")).quantize(TWO_DECIMALS)


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


def describe_item(item, show_estimate=True):
    """
    Texto de un renglón para el mensaje: 'Cocina: 10 m² (USD 1.000,00)'.
    Sin metros (visita pedida) queda solo el nombre del área.
    """
    name = item.area.name
    if item.area.is_other and item.area_other:
        name = f"{name} ({item.area_other})"
    if item.square_meters is None:
        return name

    text = f"{name}: {format_square_meters(item.square_meters)} m²"
    if show_estimate:
        text += f" ({format_usd(item.subtotal)})"
    return text


def build_whatsapp_message(quote, items, show_estimate=True):
    """
    Arma el texto que la persona enviará por WhatsApp.

    No lleva emojis: algunas versiones de WhatsApp los muestran como "?"
    cuando llegan dentro de un enlace. Cada línea empieza con un guion.
    Con show_estimate apagado no se menciona ningún precio.
    """
    lines = [
        "Hola RP Design, quiero una cotización:",
        "",
        f"- Nombre: {quote.name}",
        f"- Correo: {quote.email}",
        f"- Teléfono: {quote.phone}",
    ]
    if quote.location:
        lines.append(f"- Ubicación: {quote.location}")
    # Las cotizaciones anteriores a specs-002 no tienen tipo: la línea se omite
    if quote.category_name:
        lines.append(f"- Tipo: {quote.category_name}")

    lines.append("- Áreas:")
    lines += [f"  - {describe_item(item, show_estimate)}" for item in items]

    if show_estimate:
        lines.append(f"- Estimado total: {format_usd(quote.estimated_price)}")
    if quote.has_photos:
        lines.append("- Tengo fotos del espacio")
    if quote.needs_visit:
        lines.append("- No sé los m²: quiero agendar una visita")
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
