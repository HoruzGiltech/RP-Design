"""
Reglas de negocio de los proyectos.

Son funciones simples, sin efectos secundarios: reciben datos y devuelven
un resultado. Por eso son fáciles de probar una por una.
"""
import unicodedata

from django.utils.text import slugify

# Palabra que se antepone cuando el título tiene una sola palabra
SINGLE_WORD_PREFIX = "proyecto"


def build_base_slug(title):
    """
    Crea la dirección web de un proyecto a partir de su título.

    'Remodelación de cocina' -> 'remodelacion-de-cocina'
    'Casa'                   -> 'proyecto-casa'   (una sola palabra)
    '¿?'                     -> 'proyecto'        (sin letras ni números)
    """
    slug = slugify(title)
    if not slug or slug == SINGLE_WORD_PREFIX:
        return SINGLE_WORD_PREFIX
    # slugify une las palabras con guiones: sin guion, es una sola palabra
    if "-" not in slug:
        return f"{SINGLE_WORD_PREFIX}-{slug}"
    return slug


def make_unique_slug(base_slug, existing_slugs):
    """Si 'proyecto-casa' ya existe, devuelve 'proyecto-casa-2', '-3'..."""
    slug = base_slug
    number = 2
    while slug in existing_slugs:
        slug = f"{base_slug}-{number}"
        number += 1
    return slug


def _simplify(text):
    """Minúsculas y sin tildes: 'Categoría' -> 'categoria'. Sirve para comparar textos."""
    without_accents = unicodedata.normalize("NFKD", text)
    return "".join(c for c in without_accents if not unicodedata.combining(c)).lower()


def match_category_name(old_text, category_names):
    """
    Busca qué categoría menciona un texto libre de categoría.

    'Fachada · Residencial' -> 'Residencial'.  Sin coincidencia -> None.

    La usa la migración que convierte el campo de texto antiguo en una
    relación con la lista de categorías.
    """
    simplified_text = _simplify(old_text or "")
    for name in category_names:
        if _simplify(name) in simplified_text:
            return name
    return None
