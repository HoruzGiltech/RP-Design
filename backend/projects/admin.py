from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from django.utils.html import format_html

from projects.models import Project, ProjectCategory, ProjectMedia

NO_PREVIEW = "—"


def image_preview(image, height):
    """Devuelve la etiqueta <img> de una vista previa, o una raya si no hay imagen."""
    if not image:
        return NO_PREVIEW
    return format_html(
        '<img src="{}" alt="" style="height: {}px; width: auto;">', image.url, height
    )


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    Categorías de proyectos. Se ordenan arrastrando.
    La dirección web no se escribe: se genera sola a partir del nombre.
    Una categoría con proyectos no se puede eliminar (Django lo avisa).
    """

    list_display = ("name", "project_count")
    fields = ("name",)

    @admin.display(description="Proyectos")
    def project_count(self, category):
        return category.projects.count()


class ProjectMediaInline(SortableInlineAdminMixin, admin.TabularInline):
    """Galería del proyecto: se edita y se ordena dentro del mismo proyecto."""

    model = ProjectMedia
    extra = 0
    fields = ("preview", "file", "poster", "alt_text")
    readonly_fields = ("preview",)

    @admin.display(description="Vista previa")
    def preview(self, media):
        if media.is_video:
            # Un video solo tiene imagen si el cliente subió la vista previa
            return image_preview(media.poster, height=70) if media.poster else "Video"
        return image_preview(media.thumbnail, height=70)


@admin.register(Project)
class ProjectAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "cover_preview",
        "title",
        "category",
        "is_published",
        "show_in_hero",
        "hero_order",
        "is_category_cover",
    )
    list_display_links = ("cover_preview", "title")
    list_filter = ("is_published", "category", "show_in_hero")
    search_fields = ("title", "location")
    # La dirección web se muestra, pero no se escribe: se genera sola
    readonly_fields = ("slug_display", "cover_preview_large")
    inlines = [ProjectMediaInline]

    fieldsets = (
        (None, {"fields": ("title", "slug_display", "summary", "description")}),
        ("Datos del proyecto", {"fields": ("category", "location", "year")}),
        ("Portada", {"fields": ("cover_preview_large", "cover_image", "cover_alt")}),
        (
            "Publicación",
            {"fields": ("is_published", "show_in_hero", "hero_order", "is_category_cover")},
        ),
    )

    @admin.display(description="Dirección web")
    def slug_display(self, project):
        if not project.slug:
            return "Se genera sola al guardar, a partir del título."
        return project.slug

    @admin.display(description="Portada")
    def cover_preview(self, project):
        return image_preview(project.cover_thumbnail, height=50)

    @admin.display(description="Vista previa")
    def cover_preview_large(self, project):
        return image_preview(project.cover_thumbnail, height=160)
