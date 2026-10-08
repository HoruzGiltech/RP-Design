from django.urls import path

from quotes.views import QuoteCategoryListView, QuoteCreateView

urlpatterns = [
    path("quote-categories/", QuoteCategoryListView.as_view(), name="quote-category-list"),
    path("quotes/", QuoteCreateView.as_view(), name="quote-create"),
]
