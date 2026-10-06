from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import MAX_HERO_PROJECTS, Project, ProjectCategory
from projects.serializers import (
    ProjectCardSerializer,
    ProjectCategorySerializer,
    ProjectDetailSerializer,
)


def published_projects():
    """Los borradores nunca salen por la API pública."""
    return Project.objects.filter(is_published=True).select_related("category")


class ProjectListView(generics.ListAPIView):
    """
    GET /api/projects/                    -> todos los proyectos publicados
    GET /api/projects/?hero=true          -> los que van en el hero (máximo 6)
    GET /api/projects/?category=<slug>    -> los de una categoría
    """

    serializer_class = ProjectCardSerializer
    throttle_scope = "public"

    def get_queryset(self):
        projects = published_projects()
        params = self.request.query_params

        if params.get("hero") == "true":
            return projects.filter(show_in_hero=True).order_by("hero_order", "order")[
                :MAX_HERO_PROJECTS
            ]

        category_slug = params.get("category")
        # Una categoría que no existe no es un error: se devuelven todos
        if category_slug and ProjectCategory.objects.filter(slug=category_slug).exists():
            return projects.filter(category__slug=category_slug)
        return projects


class ProjectDetailView(generics.RetrieveAPIView):
    """GET /api/projects/<slug>/ -> detalle con su galería. Un borrador da 404."""

    serializer_class = ProjectDetailSerializer
    throttle_scope = "public"
    lookup_field = "slug"
    queryset = published_projects().prefetch_related("media")


class ProjectCategoryListView(APIView):
    """
    GET /api/project-categories/ -> categorías que tienen proyectos publicados.

    Una categoría vacía no se envía: el sitio no debe mostrar una tarjeta
    que lleve a una página sin proyectos.
    """

    throttle_scope = "public"

    def get(self, request):
        categories = []
        for category in ProjectCategory.objects.all():
            projects = list(published_projects().filter(category=category))
            if not projects:
                continue
            category.project_count = len(projects)
            category.cover_project = self._choose_cover(projects)
            categories.append(category)

        serializer = ProjectCategorySerializer(
            categories, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def _choose_cover(self, projects):
        """El proyecto marcado como portada; si no hay, el primero según el orden del panel."""
        for project in projects:
            if project.is_category_cover:
                return project
        return projects[0]
