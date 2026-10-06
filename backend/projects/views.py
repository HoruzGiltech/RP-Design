from rest_framework import generics

from projects.models import MAX_FEATURED_PROJECTS, Project
from projects.serializers import ProjectCardSerializer, ProjectDetailSerializer


class ProjectListView(generics.ListAPIView):
    """
    GET /api/projects/                 -> todos los proyectos publicados
    GET /api/projects/?featured=true   -> solo los destacados (máximo 3)
    """

    serializer_class = ProjectCardSerializer
    throttle_scope = "public"

    def get_queryset(self):
        # Los borradores nunca salen por la API pública
        published = Project.objects.filter(is_published=True)

        if self.request.query_params.get("featured") == "true":
            featured = published.filter(is_featured=True).order_by("featured_order", "order")
            return featured[:MAX_FEATURED_PROJECTS]
        return published


class ProjectDetailView(generics.RetrieveAPIView):
    """GET /api/projects/<slug>/ -> detalle con su galería. Un borrador da 404."""

    serializer_class = ProjectDetailSerializer
    throttle_scope = "public"
    lookup_field = "slug"
    queryset = Project.objects.filter(is_published=True).prefetch_related("media")
