from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from core.images import build_optimized, build_thumbnail
from core.models import OrderedModel, TimeStampedModel
from core.uploads import build_unique_path, file_has_changed
from core.validators import (
    VIDEO_EXTENSIONS,
    get_extension,
    validate_image_file,
    validate_media_file,
)

MAX_FEATURED_PROJECTS = 3


def project_upload_path(instance, filename):
    """Todos los archivos de proyectos van a 'projects/<año>/<uuid>.<ext>'."""
    return build_unique_path("projects", filename)


class Project(TimeStampedModel, OrderedModel):
    title = models.CharField("título", max_length=150)
    slug = models.SlugField(
        "dirección web",
        max_length=170,
        unique=True,
        blank=True,
        help_text="Parte final de la URL del proyecto. Si se deja vacía, sale del título.",
    )
    summary = models.CharField(
        "resumen", max_length=300, help_text="Texto corto que se ve en la tarjeta."
    )
    description = models.TextField("descripción")
    category = models.CharField(
        "categoría", max_length=80, blank=True, help_text="Ejemplo: Fachada · Residencial"
    )
    location = models.CharField("ubicación", max_length=120, blank=True)
    year = models.PositiveSmallIntegerField("año", null=True, blank=True)

    cover_image = models.ImageField(
        "imagen de portada",
        upload_to=project_upload_path,
        validators=[validate_image_file],
    )
    cover_thumbnail = models.ImageField(
        "miniatura de portada", upload_to=project_upload_path, blank=True, editable=False
    )
    cover_alt = models.CharField(
        "texto alternativo de la portada",
        max_length=150,
        help_text="Describe la foto para quien no puede verla.",
    )

    is_published = models.BooleanField(
        "publicado", default=False, help_text="Si no está marcado, es un borrador."
    )
    is_featured = models.BooleanField(
        "destacado",
        default=False,
        help_text=f"Se muestra en el inicio. Máximo {MAX_FEATURED_PROJECTS}.",
    )
    featured_order = models.PositiveSmallIntegerField(
        "orden entre destacados", default=0, help_text="El número menor va primero."
    )

    class Meta(OrderedModel.Meta):
        verbose_name = "proyecto"
        verbose_name_plural = "proyectos"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.is_featured and self._count_other_featured() >= MAX_FEATURED_PROJECTS:
            raise ValidationError(
                {
                    "is_featured": (
                        f"Ya hay {MAX_FEATURED_PROJECTS} proyectos destacados. "
                        "Quita uno antes de destacar otro."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._build_unique_slug()
        if file_has_changed(self, "cover_image"):
            self._process_cover()
        super().save(*args, **kwargs)

    def _count_other_featured(self):
        return Project.objects.filter(is_featured=True).exclude(pk=self.pk).count()

    def _build_unique_slug(self):
        """Crea el slug desde el título; si ya existe, le agrega -2, -3..."""
        base_slug = slugify(self.title) or "proyecto"
        slug = base_slug
        number = 2
        while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{number}"
            number += 1
        return slug

    def _process_cover(self):
        """Reemplaza la foto subida por su versión optimizada y crea la miniatura."""
        uploaded = self.cover_image.file
        # Las dos versiones se generan antes de guardar: ambas salen del original
        thumbnail = build_thumbnail(uploaded)
        optimized = build_optimized(uploaded)
        # save=False: solo guarda el archivo; el registro se guarda después en save()
        self.cover_thumbnail.save(thumbnail.name, thumbnail, save=False)
        self.cover_image.save(optimized.name, optimized, save=False)


class ProjectMedia(OrderedModel):
    IMAGE = "image"
    VIDEO = "video"
    MEDIA_TYPE_CHOICES = [(IMAGE, "Imagen"), (VIDEO, "Video")]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="media", verbose_name="proyecto"
    )
    media_type = models.CharField(
        "tipo", max_length=10, choices=MEDIA_TYPE_CHOICES, default=IMAGE, editable=False
    )
    file = models.FileField(
        "archivo",
        upload_to=project_upload_path,
        validators=[validate_media_file],
        help_text="Imagen (jpg, png, webp) o video (mp4, webm).",
    )
    thumbnail = models.ImageField(
        "miniatura", upload_to=project_upload_path, blank=True, editable=False
    )
    poster = models.ImageField(
        "vista previa del video",
        upload_to=project_upload_path,
        blank=True,
        validators=[validate_image_file],
        help_text="Solo para videos: la imagen que se ve antes de reproducir.",
    )
    alt_text = models.CharField(
        "texto alternativo",
        max_length=150,
        help_text="Describe la imagen o el video para quien no puede verlo.",
    )

    class Meta(OrderedModel.Meta):
        verbose_name = "imagen o video"
        verbose_name_plural = "galería"

    def __str__(self):
        return f"{self.get_media_type_display()} de {self.project}"

    @property
    def is_video(self):
        return self.media_type == self.VIDEO

    def save(self, *args, **kwargs):
        if file_has_changed(self, "file"):
            self._process_file()
        if self.poster and file_has_changed(self, "poster"):
            optimized = build_optimized(self.poster.file)
            self.poster.save(optimized.name, optimized, save=False)
        super().save(*args, **kwargs)

    def _process_file(self):
        """Detecta si es imagen o video. Las imágenes se optimizan; los videos no se tocan."""
        if get_extension(self.file) in VIDEO_EXTENSIONS:
            self.media_type = self.VIDEO
            self.thumbnail = ""
            return

        self.media_type = self.IMAGE
        uploaded = self.file.file
        thumbnail = build_thumbnail(uploaded)
        optimized = build_optimized(uploaded)
        self.thumbnail.save(thumbnail.name, thumbnail, save=False)
        self.file.save(optimized.name, optimized, save=False)
