from django.urls import path

from site_content.views import SiteContentView

urlpatterns = [
    path("site/", SiteContentView.as_view(), name="site-content"),
]
