from rest_framework import serializers

from projects.models import Project, ProjectCategory, ProjectMedia


class CategoryLabelSerializer(serializers.ModelSerializer):
    """Nombre y dirección de la categoría, para la etiqueta de un proyecto."""

    class Meta:
        model = ProjectCategory
        fields = ["name", "slug"]


class ProjectCardSerializer(serializers.ModelSerializer):
    """
    Datos mínimos de un proyecto para las cuadrículas y para el hero.
    cover_thumbnail es la miniatura de las tarjetas; cover_image, la foto
    grande que usa el hero.
    """

    category = CategoryLabelSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            "slug",
            "title",
            "summary",
            # La descripción se muestra sobre la portada al pasar el mouse (specs-003)
            "description",
            "category",
            "cover_image",
            "cover_thumbnail",
            "cover_alt",
        ]


class ProjectMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMedia
        fields = ["id", "media_type", "file", "thumbnail", "poster", "alt_text"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    category = CategoryLabelSerializer(read_only=True)
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


class ProjectCategorySerializer(serializers.ModelSerializer):
    """
    Categoría para la tarjeta del inicio y el filtro de /proyectos.

    La vista le agrega a cada categoría dos datos calculados:
    `project_count` (cuántos proyectos publicados tiene) y `cover_project`
    (el proyecto cuya portada la representa).
    """

    project_count = serializers.IntegerField(read_only=True)
    cover_thumbnail = serializers.SerializerMethodField()
    cover_alt = serializers.SerializerMethodField()

    class Meta:
        model = ProjectCategory
        fields = ["name", "slug", "project_count", "cover_thumbnail", "cover_alt"]

    def get_cover_thumbnail(self, category):
        thumbnail = category.cover_project.cover_thumbnail
        if not thumbnail:
            return None
        # Con el request se arma la dirección completa de la imagen
        return self.context["request"].build_absolute_uri(thumbnail.url)

    def get_cover_alt(self, category):
        return category.cover_project.cover_alt
