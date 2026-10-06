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
from projects.services import build_base_slug, make_unique_slug

MAX_HERO_PROJECTS = 6


def project_upload_path(instance, filename):
    """Todos los archivos de proyectos van a 'projects/<año>/<uuid>.<ext>'."""
    return build_unique_path("projects", filename)


class ProjectCategory(OrderedModel):
    """Categoría de proyectos: Comercial, Residencial, Corporativo..."""

    name = models.CharField("nombre", max_length=60, unique=True)
    slug = models.SlugField("dirección web", max_length=70, unique=True, editable=False)

    class Meta(OrderedModel.Meta):
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # La dirección se crea una vez y no cambia, aunque después cambie el nombre:
        # así los enlaces ya compartidos siguen funcionando.
        if not self.slug:
            existing = set(ProjectCategory.objects.values_list("slug", flat=True))
            self.slug = make_unique_slug(slugify(self.name) or "categoria", existing)
        super().save(*args, **kwargs)


class Project(TimeStampedModel, OrderedModel):
    title = models.CharField("título", max_length=150)
    slug = models.SlugField("dirección web", max_length=170, unique=True, editable=False)
    summary = models.CharField(
        "resumen", max_length=300, help_text="Texto corto que se ve en la tarjeta."
    )
    description = models.TextField("descripción")
    # PROTECT: no se puede borrar una categoría que tiene proyectos.
    # null=True solo por los proyectos anteriores a que existieran las categorías;
    # en el panel es obligatoria (blank=False).
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.PROTECT,
        related_name="projects",
        verbose_name="categoría",
        null=True,
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
    show_in_hero = models.BooleanField(
        "mostrar en el hero",
        default=False,
        help_text=(
            "La portada aparece en la parte superior del inicio. "
            f"Con más de una, van rotando. Máximo {MAX_HERO_PROJECTS}."
        ),
    )
    hero_order = models.PositiveSmallIntegerField(
        "orden en el hero", default=0, help_text="El número menor va primero."
    )
    is_category_cover = models.BooleanField(
        "usar como portada de su categoría",
        default=False,
        help_text=(
            "Su portada representa a la categoría en el inicio. Solo una por categoría: "
            "al marcar esta, se desmarca la anterior."
        ),
    )

    class Meta(OrderedModel.Meta):
        verbose_name = "proyecto"
        verbose_name_plural = "proyectos"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.show_in_hero and self._count_other_hero_projects() >= MAX_HERO_PROJECTS:
            raise ValidationError(
                {
                    "show_in_hero": (
                        f"Ya hay {MAX_HERO_PROJECTS} proyectos en el hero. "
                        "Quita uno antes de agregar otro."
                    )
                }
            )

    def save(self, *args, **kwargs):
        # La dirección se crea una vez, al guardar por primera vez. Después no
        # cambia aunque cambie el título, para no romper enlaces ya compartidos.
        if not self.slug:
            existing = set(Project.objects.values_list("slug", flat=True))
            self.slug = make_unique_slug(build_base_slug(self.title), existing)
        if file_has_changed(self, "cover_image"):
            self._process_cover()
        super().save(*args, **kwargs)
        if self.is_category_cover:
            self._unmark_other_category_covers()

    def _count_other_hero_projects(self):
        return Project.objects.filter(show_in_hero=True).exclude(pk=self.pk).count()

    def _unmark_other_category_covers(self):
        """Solo un proyecto puede ser la portada de su categoría."""
        if self.category_id is None:
            return
        others = Project.objects.filter(category_id=self.category_id, is_category_cover=True)
        others.exclude(pk=self.pk).update(is_category_cover=False)

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
