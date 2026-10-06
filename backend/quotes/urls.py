from django.urls import path

from quotes.views import QuoteCreateView, RemodelAreaListView

urlpatterns = [
    path("quote-areas/", RemodelAreaListView.as_view(), name="quote-area-list"),
    path("quotes/", QuoteCreateView.as_view(), name="quote-create"),
]
