from django.urls import path

from site_content.views import LegalPageView, SiteContentView

urlpatterns = [
    path("site/", SiteContentView.as_view(), name="site-content"),
    path("legal/<slug:slug>/", LegalPageView.as_view(), name="legal-page"),
]
