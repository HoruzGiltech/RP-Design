from django.urls import path

from quotes.views import QuoteCreateView

urlpatterns = [
    path("quotes/", QuoteCreateView.as_view(), name="quote-create"),
]
