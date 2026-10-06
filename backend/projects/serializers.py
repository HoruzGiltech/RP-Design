from rest_framework import serializers

from projects.models import Project, ProjectMedia


class ProjectCardSerializer(serializers.ModelSerializer):
    """Datos mínimos para la tarjeta de un proyecto en las cuadrículas."""

    class Meta:
        model = Project
        fields = ["slug", "title", "summary", "category", "cover_thumbnail", "cover_alt"]


class ProjectMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMedia
        fields = ["id", "media_type", "file", "thumbnail", "poster", "alt_text"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    # La galería llega ya ordenada: ProjectMedia se ordena por "order"
    media = ProjectMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "slug",
            "title",
            "summary",
            "description",
            "category",
            "location",
            "year",
            "cover_image",
            "cover_thumbnail",
            "cover_alt",
            "media",
        ]
