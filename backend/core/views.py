from django.conf import settings
from django.http import Http404
from django.views.static import serve


def serve_media(request, path):
    """
    Entrega un archivo subido desde el panel (foto, video o fuente).

    Solo funciona con SERVE_MEDIA activado: en local, y en un servidor que
    guarda los archivos en su propio disco. Cuando los archivos vivan en
    Cloudflare R2 los entregará Cloudflare, y esta vista responderá 404.

    `serve` es la función de Django para esto: ya impide pedir archivos de
    fuera de la carpeta con rutas como "../../.env".
    """
    if not settings.SERVE_MEDIA:
        raise Http404("Los archivos no se sirven desde este servidor.")
    return serve(request, path, document_root=settings.MEDIA_ROOT)
