from django.conf import settings


class NoIndexMiddleware:
    """
    Agrega "X-Robots-Tag: noindex" a las respuestas del backend para que el
    panel y la API no aparezcan en Google.

    Se exceptúan el sitemap (Google debe poder leerlo) y las fotos y videos
    de /media/ (si no, las fotos de los proyectos no saldrían en Google Imágenes).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        is_public_file = request.path == "/sitemap.xml" or request.path.startswith(
            settings.MEDIA_URL
        )
        if not is_public_file:
            response["X-Robots-Tag"] = "noindex"
        return response
