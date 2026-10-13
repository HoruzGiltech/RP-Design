"""
De qué dirección IP viene una petición.

En local el navegador habla directo con Django y la IP está en REMOTE_ADDR.
En internet hay un proxy delante (Railway, Cloudflare): para Django todas las
peticiones vienen del proxy, y la IP real del visitante llega en la cabecera
X-Forwarded-For, que el proxy va completando.
"""
from django.conf import settings


def get_client_ip(request, credentials=None):
    """
    Devuelve la IP del visitante.

    settings.NUM_PROXIES dice cuántos proxies de confianza hay delante:
    - 0: no hay ninguno. Se usa REMOTE_ADDR y se ignora X-Forwarded-For,
      porque esa cabecera la puede inventar cualquiera.
    - N: cada proxy agrega al final de X-Forwarded-For la dirección de quien
      le habló. La que puso el proxy más externo es la N-ésima desde el final.

    Es la misma regla que usa Django REST Framework para sus límites, así que
    la API y el bloqueo del panel cuentan por la misma dirección.

    `credentials` no se usa: django-axes lo envía al llamar a esta función.
    """
    remote_address = request.META.get("REMOTE_ADDR", "")
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")

    if settings.NUM_PROXIES == 0 or not forwarded_for:
        return remote_address

    addresses = [address.strip() for address in forwarded_for.split(",")]
    # Si la cabecera trae menos direcciones de las esperadas, se usa la primera
    position = min(settings.NUM_PROXIES, len(addresses))
    return addresses[-position]
