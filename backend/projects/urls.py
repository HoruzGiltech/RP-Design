from django.urls import path

from projects.views import ProjectCategoryListView, ProjectDetailView, ProjectListView

urlpatterns = [
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path("projects/<slug:slug>/", ProjectDetailView.as_view(), name="project-detail"),
    path("project-categories/", ProjectCategoryListView.as_view(), name="project-category-list"),
]
