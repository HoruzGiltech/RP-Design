from django.conf import settings
from django.contrib import admin
from django.urls import path

admin.site.site_header = "Panel RP Design"
admin.site.site_title = "Panel RP Design"
admin.site.index_title = "Administración del sitio"

urlpatterns = [
    # La URL del panel sale de .env para que no sea la típica /admin/
    path(settings.ADMIN_URL, admin.site.urls),
]
